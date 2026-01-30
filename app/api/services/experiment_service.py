"""Experiment service for business logic."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.dataset_file import (
    DatasetFileContentResponse,
    DatasetFileCreate,
    DatasetFileResponse,
)
from app.api.schemas.experiment import (
    ExperimentAttachDataset,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentUpdate,
)
from app.api.services.dataset_file_service import DatasetFileService
from app.api.services.utils import apply_sorting, build_list_response
from app.db.models.experiment import Experiment
from app.db.models.experiment_type import ExperimentType
from app.db.models.project import Project
from app.schemas.common.base import ExperimentStatus


class ExperimentService:
    """Service for experiment business logic."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db

    def create_experiment(self, experiment_data: ExperimentCreate) -> ExperimentResponse:
        """Create a new experiment."""
        project = self.db.query(Project).filter(Project.id == experiment_data.project_id).first()
        if not project:
            raise NotFoundError(f"Project with ID {experiment_data.project_id} not found")

        # Validate experiment type exists
        experiment_type = (
            self.db.query(ExperimentType)
            .filter(ExperimentType.id == experiment_data.experiment_type_id)
            .first()
        )
        if not experiment_type:
            raise NotFoundError(
                f"Experiment type with ID {experiment_data.experiment_type_id} not found"
            )

        db_experiment = Experiment(
            name=experiment_data.name,
            experiment_type_id=experiment_data.experiment_type_id,
            description=experiment_data.description,
            project_id=experiment_data.project_id,
        )
        self.db.add(db_experiment)
        self.db.commit()
        self.db.refresh(db_experiment)

        return self._build_experiment_response(db_experiment)

    def get_experiment(self, experiment_id: int) -> ExperimentResponse:
        """Get an experiment by ID."""
        experiment = self.db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise NotFoundError(f"Experiment with ID {experiment_id} not found")

        return self._build_experiment_response(experiment)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def list_experiments(
        self,
        pagination: PaginationParams,
        sorting: SortingParams,
        search_params: SearchParams,
        project_id: int | None = None,
        experiment_type_id: int | None = None,
    ) -> ListResponse[ExperimentResponse]:
        """List all experiments with optional filters, pagination, sorting, and search."""
        query = self.db.query(Experiment)

        # Apply filters
        if project_id is not None:
            query = query.filter(Experiment.project_id == project_id)
        if experiment_type_id is not None:
            query = query.filter(Experiment.experiment_type_id == experiment_type_id)

        # Apply search filter
        if search_params.search:
            search_filter = or_(
                Experiment.name.ilike(f"%{search_params.search}%"),
                Experiment.description.ilike(f"%{search_params.search}%"),
            )
            query = query.filter(search_filter)

        # Apply sorting
        if sorting.sort_by:
            if sorting.sort_by not in Experiment.valid_sort_fields:
                raise SortingValidationError(
                    f"Invalid sort field '{sorting.sort_by}'. "
                    f"Valid fields are: {', '.join(sorted(Experiment.valid_sort_fields))}"
                )
            sort_column = getattr(Experiment, sorting.sort_by)
            query = apply_sorting(query, sort_column, sorting.sort_direction)
        else:
            query = query.order_by(Experiment.created_at.desc())

        experiments = query.offset(pagination.skip).limit(pagination.limit).all()

        data = [self._build_experiment_response(exp) for exp in experiments]

        return build_list_response(pagination, sorting, search_params, data)

    def update_experiment(
        self, experiment_id: int, experiment_update: ExperimentUpdate
    ) -> ExperimentResponse:
        """Update an experiment."""
        experiment = self.db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise NotFoundError(f"Experiment with ID {experiment_id} not found")

        if experiment_update.project_id is not None:
            project = (
                self.db.query(Project).filter(Project.id == experiment_update.project_id).first()
            )
            if not project:
                raise NotFoundError(f"Project with ID {experiment_update.project_id} not found")

        if experiment_update.experiment_type_id is not None:
            experiment_type = (
                self.db.query(ExperimentType)
                .filter(ExperimentType.id == experiment_update.experiment_type_id)
                .first()
            )
            if not experiment_type:
                raise NotFoundError(
                    f"Experiment type with ID {experiment_update.experiment_type_id} not found"
                )

        # Update fields
        if experiment_update.name is not None:
            experiment.name = experiment_update.name
        if experiment_update.experiment_type_id is not None:
            experiment.experiment_type_id = experiment_update.experiment_type_id
        if experiment_update.description is not None:
            experiment.description = experiment_update.description
        if experiment_update.project_id is not None:
            experiment.project_id = experiment_update.project_id

        self.db.commit()
        self.db.refresh(experiment)

        return self._build_experiment_response(experiment)

    def delete_experiment(self, experiment_id: int) -> None:
        """Delete an experiment."""
        experiment = self.db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise NotFoundError(f"Experiment with ID {experiment_id} not found")

        self.db.delete(experiment)
        self.db.commit()

    def attach_dataset_file(
        self, experiment_id: int, dataset_data: ExperimentAttachDataset
    ) -> DatasetFileResponse:
        """Attach a dataset file to an experiment."""
        experiment = self.db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise NotFoundError(f"Experiment with ID {experiment_id} not found")

        dataset_file_service = DatasetFileService(self.db)

        # Either use existing dataset file or create a new one
        if dataset_data.dataset_file_id is not None:
            # Use existing dataset file
            dataset_file = dataset_file_service.get_dataset_file(dataset_data.dataset_file_id)
        else:
            # Create new dataset file (path is guaranteed to be not None by validator)
            if dataset_data.path is None:
                raise ValueError("Path must be provided when dataset_file_id is not provided")
            dataset_file_create = DatasetFileCreate(path=dataset_data.path)
            dataset_file = dataset_file_service.create_dataset_file(dataset_file_create)

        # Associate dataset file with experiment and update status to in_progress
        experiment.dataset_file_id = dataset_file.id
        experiment.status = ExperimentStatus.IN_PROGRESS.value
        self.db.commit()
        self.db.refresh(experiment)

        return dataset_file

    def get_experiment_dataset_content(
        self, experiment_id: int, pagination: PaginationParams
    ) -> DatasetFileContentResponse:
        """Get paginated content from the dataset file associated with an experiment."""
        experiment = self.db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise NotFoundError(f"Experiment with ID {experiment_id} not found")

        if not experiment.dataset_file_id:
            raise NotFoundError(
                f"Experiment with ID {experiment_id} has no associated dataset file"
            )

        # Get dataset file content using DatasetFileService
        dataset_file_service = DatasetFileService(self.db)
        return dataset_file_service.get_dataset_file_content(experiment.dataset_file_id, pagination)

    def _build_experiment_response(self, experiment: Experiment) -> ExperimentResponse:
        """Build an ExperimentResponse from an Experiment model."""
        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            experiment_type_id=experiment.experiment_type_id,
            description=experiment.description,
            project_id=experiment.project_id,
            status=ExperimentStatus(experiment.status),
            current_step=experiment.current_step,
            created_at=experiment.created_at,
            updated_at=experiment.updated_at,
        )
