"""Dataset file service for business logic."""

import os
from pathlib import Path

import polars as pl
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError, ValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.dataset_file import (
    DatasetFileContentResponse,
    DatasetFileCreate,
    DatasetFileResponse,
    DatasetFileUpdate,
)
from app.api.services.utils import apply_sorting, build_list_response
from app.db.models.dataset_file import DatasetFile
from app.db.models.experiment import Experiment


class DatasetFileService:
    """Service for dataset file business logic."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db

    def list_dataset_files(
        self,
        pagination: PaginationParams,
        sorting: SortingParams,
        search_params: SearchParams,
    ) -> ListResponse[DatasetFileResponse]:
        """List all dataset files with pagination, sorting, and search."""
        query = self.db.query(DatasetFile).filter(DatasetFile.deleted_at.is_(None))

        if search_params.search:
            search_filter = or_(
                DatasetFile.name.ilike(f"%{search_params.search}%"),
                DatasetFile.path.ilike(f"%{search_params.search}%"),
            )
            query = query.filter(search_filter)

        if sorting.sort_by:
            if sorting.sort_by not in DatasetFile.valid_sort_fields:
                raise SortingValidationError(
                    f"Invalid sort field '{sorting.sort_by}'. "
                    f"Valid fields are: {', '.join(sorted(DatasetFile.valid_sort_fields))}"
                )
            sort_column = getattr(DatasetFile, sorting.sort_by)
            query = apply_sorting(query, sort_column, sorting.sort_direction)
        else:
            query = query.order_by(DatasetFile.created_at.desc())

        dataset_files = query.offset(pagination.skip).limit(pagination.limit).all()

        data = [self._build_dataset_file_response(dataset_file) for dataset_file in dataset_files]

        return build_list_response(pagination, sorting, search_params, data)

    def create_dataset_file(self, dataset_file_data: DatasetFileCreate) -> DatasetFileResponse:
        """Create a new dataset file."""
        # Validate that the file exists
        file_path = Path(dataset_file_data.path)
        if not file_path.exists():
            raise ValidationError(f"File not found at path: {dataset_file_data.path}")

        if not file_path.is_file():
            raise ValidationError(f"Path is not a file: {dataset_file_data.path}")

        existing_dataset_file = (
            self.db.query(DatasetFile)
            .filter(DatasetFile.path == dataset_file_data.path)
            .filter(DatasetFile.deleted_at.is_(None))
            .first()
        )
        if existing_dataset_file:
            raise ConflictError(f"Dataset file with path '{dataset_file_data.path}' already exists")

        # Extract file name from path
        file_name = os.path.basename(dataset_file_data.path)

        db_dataset_file = DatasetFile(name=file_name, path=dataset_file_data.path)
        self.db.add(db_dataset_file)
        self.db.commit()
        self.db.refresh(db_dataset_file)

        return self._build_dataset_file_response(db_dataset_file)

    def get_dataset_file(self, dataset_file_id: int) -> DatasetFileResponse:
        """Get a dataset file by ID."""
        dataset_file = (
            self.db.query(DatasetFile)
            .filter(DatasetFile.id == dataset_file_id)
            .filter(DatasetFile.deleted_at.is_(None))
            .first()
        )
        if not dataset_file:
            raise NotFoundError(f"Dataset file with ID {dataset_file_id} not found")

        return self._build_dataset_file_response(dataset_file)

    def update_dataset_file(
        self, dataset_file_id: int, dataset_file_update: DatasetFileUpdate
    ) -> DatasetFileResponse:
        """Update a dataset file."""
        dataset_file = (
            self.db.query(DatasetFile)
            .filter(DatasetFile.id == dataset_file_id)
            .filter(DatasetFile.deleted_at.is_(None))
            .first()
        )
        if not dataset_file:
            raise NotFoundError(f"Dataset file with ID {dataset_file_id} not found")

        if dataset_file_update.path is not None:
            if dataset_file_update.path != dataset_file.path:
                existing_dataset_file = (
                    self.db.query(DatasetFile)
                    .filter(DatasetFile.path == dataset_file_update.path)
                    .filter(DatasetFile.deleted_at.is_(None))
                    .first()
                )
                if existing_dataset_file:
                    raise ConflictError(
                        f"Dataset file with path '{dataset_file_update.path}' already exists"
                    )

            # Update path and extract new file name from path
            dataset_file.path = dataset_file_update.path
            dataset_file.name = os.path.basename(dataset_file_update.path)

        self.db.commit()
        self.db.refresh(dataset_file)

        return self._build_dataset_file_response(dataset_file)

    def delete_dataset_file(self, dataset_file_id: int) -> None:
        """Delete a dataset file."""
        dataset_file = (
            self.db.query(DatasetFile)
            .filter(DatasetFile.id == dataset_file_id)
            .filter(DatasetFile.deleted_at.is_(None))
            .first()
        )
        if not dataset_file:
            raise NotFoundError(f"Dataset file with ID {dataset_file_id} not found")

        # Check if dataset file is associated with any experiment
        associated_experiment = (
            self.db.query(Experiment)
            .filter(Experiment.dataset_file_id == dataset_file_id)
            .filter(Experiment.deleted_at.is_(None))
            .first()
        )
        if associated_experiment:
            raise ConflictError(
                f"Cannot delete dataset file with ID {dataset_file_id} because it is "
                f"associated with experiment ID {associated_experiment.id}"
            )

        self.db.delete(dataset_file)
        self.db.commit()

    # pylint: disable=too-many-locals
    def get_dataset_file_content(
        self, dataset_file_id: int, pagination: PaginationParams
    ) -> DatasetFileContentResponse:
        """Get paginated content from a dataset file CSV."""
        dataset_file = (
            self.db.query(DatasetFile)
            .filter(DatasetFile.id == dataset_file_id)
            .filter(DatasetFile.deleted_at.is_(None))
            .first()
        )
        if not dataset_file:
            raise NotFoundError(f"Dataset file with ID {dataset_file_id} not found")

        file_path = Path(dataset_file.path)
        if not file_path.exists():
            raise NotFoundError(f"CSV file not found at path: {dataset_file.path}")

        try:
            # Read CSV file with polars
            # Try to detect delimiter automatically by reading first line
            with file_path.open("r", encoding="utf-8") as f:
                first_line = f.readline()
                # Detect delimiter: if semicolon is present, use it; otherwise use comma
                separator = ";" if ";" in first_line else ","

            df = pl.read_csv(file_path, separator=separator)

            # Get total rows count
            total_rows = df.height

            # Apply pagination
            paginated_df = df.slice(pagination.skip, pagination.limit)

            # Convert to matrix format (list of lists) for efficiency
            # Each row is an array with values in the same order as columns
            rows_matrix = paginated_df.to_numpy().tolist()

            # Convert all values to JSON-serializable types
            rows_serializable: list[list[str | int | float | None]] = []
            for row in rows_matrix:
                row_values: list[str | int | float | None] = []
                for value in row:
                    if value is None or (isinstance(value, float) and str(value) == "nan"):
                        row_values.append(None)
                    elif isinstance(value, (int, float, str, bool)):
                        row_values.append(value)
                    else:
                        row_values.append(str(value))
                rows_serializable.append(row_values)

            return DatasetFileContentResponse(
                columns=df.columns,
                rows=rows_serializable,
                total_rows=total_rows,
                pagination=pagination,
            )
        except pl.exceptions.NoDataError as exc:
            raise NotFoundError(f"CSV file is empty: {dataset_file.path}") from exc
        except pl.exceptions.ComputeError as exc:
            raise ValueError(f"Error parsing CSV file: {dataset_file.path}") from exc
        except Exception as exc:
            raise ValueError(f"Error reading CSV file: {dataset_file.path}") from exc

    def _build_dataset_file_response(self, dataset_file: DatasetFile) -> DatasetFileResponse:
        """Build a DatasetFileResponse from a DatasetFile model."""
        # Read CSV to get columns and rows count
        try:
            df = pl.read_csv(dataset_file.path)
            columns_size = len(df.columns)
            rows_size = len(df)
        except Exception:
            # If file cannot be read, set defaults
            columns_size = 0
            rows_size = 0

        return DatasetFileResponse(
            id=dataset_file.id,
            name=dataset_file.name,
            path=dataset_file.path,
            created_at=dataset_file.created_at,
            updated_at=dataset_file.updated_at,
            columns_size=columns_size,
            rows_size=rows_size,
        )
