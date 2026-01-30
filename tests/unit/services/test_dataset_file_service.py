"""Unit tests for app.api.services.dataset_file_service."""

import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import polars as pl
import polars.exceptions
import pytest
from sqlalchemy.orm import Session

from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError, ValidationError
from app.api.schemas.api import PaginationParams, SearchParams, SortDirection, SortingParams
from app.api.schemas.dataset_file import DatasetFileCreate, DatasetFileUpdate
from app.api.services.dataset_file_service import DatasetFileService
from app.db.models.dataset_file import DatasetFile
from app.db.models.experiment import Experiment
from app.db.models.project import Project
from tests.helpers import create_project_with_dataset_and_experiment


@pytest.fixture(autouse=True)
def _cleanup_dataset_files(db_session: Session) -> None:
    """Clean up dataset files, experiments, and projects before each test."""
    db_session.query(Experiment).delete()
    db_session.query(DatasetFile).delete()
    db_session.query(Project).delete()
    db_session.commit()


@pytest.fixture(name="temp_csv_file")
def _temp_csv_file(tmp_path: Path) -> Path:
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300\n")
    return csv_file


@pytest.fixture(name="temp_csv_file_semicolon")
def _temp_csv_file_semicolon(tmp_path: Path) -> Path:
    """Create a temporary CSV file with semicolon separator."""
    csv_file = tmp_path / "test_data_semicolon.csv"
    csv_file.write_text("id;name;value\n1;Alice;100\n2;Bob;200\n")
    return csv_file


@pytest.fixture(name="temp_csv_file_empty")
def _temp_csv_file_empty(tmp_path: Path) -> Path:
    """Create an empty CSV file for testing."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    return csv_file


class TestDatasetFileServiceInit:
    """Test DatasetFileService initialization."""

    def test_init(self, db_session: Session) -> None:
        """Initialize service with database session."""
        service = DatasetFileService(db_session)
        assert service.db == db_session


class TestListDatasetFiles:
    """Test list_dataset_files method."""

    def test_list_dataset_files_success(self, db_session: Session) -> None:
        """List dataset files successfully."""
        dataset_file1 = DatasetFile(name="file1.csv", path="/path/to/file1.csv")
        dataset_file2 = DatasetFile(name="file2.csv", path="/path/to/file2.csv")
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_dataset_files(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name in ["file1.csv", "file2.csv"]
        assert result.pagination.skip == 0
        assert result.pagination.limit == 10

    def test_list_dataset_files_with_search(self, db_session: Session) -> None:
        """List dataset files with search filter."""
        dataset_file1 = DatasetFile(name="test_file.csv", path="/path/to/test_file.csv")
        dataset_file2 = DatasetFile(name="other_file.csv", path="/path/to/other_file.csv")
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="test")

        result = service.list_dataset_files(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "test_file.csv"

    def test_list_dataset_files_with_sorting(self, db_session: Session) -> None:
        """List dataset files with sorting."""
        dataset_file1 = DatasetFile(name="b_file.csv", path="/path/to/b_file.csv")
        dataset_file2 = DatasetFile(name="a_file.csv", path="/path/to/a_file.csv")
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_dataset_files(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "a_file.csv"
        assert result.data[1].name == "b_file.csv"

    def test_list_dataset_files_invalid_sort_field(self, db_session: Session) -> None:
        """Raise error when invalid sort field is provided."""
        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="invalid_field", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        with pytest.raises(SortingValidationError) as exc_info:
            service.list_dataset_files(pagination, sorting, search_params)

        assert "Invalid sort field" in exc_info.value.message

    def test_list_dataset_files_excludes_deleted(self, db_session: Session) -> None:
        """Exclude deleted dataset files from list."""
        dataset_file1 = DatasetFile(name="active.csv", path="/path/to/active.csv")
        dataset_file2 = DatasetFile(
            name="deleted.csv", path="/path/to/deleted.csv", deleted_at=datetime.datetime.now()
        )
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_dataset_files(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "active.csv"


class TestCreateDatasetFile:
    """Test create_dataset_file method."""

    def test_create_dataset_file_success(self, db_session: Session, temp_csv_file: Path) -> None:
        """Create dataset file successfully."""
        service = DatasetFileService(db_session)
        dataset_file_data = DatasetFileCreate(path=str(temp_csv_file))

        result = service.create_dataset_file(dataset_file_data)

        assert result.name == "test_data.csv"
        assert result.path == str(temp_csv_file)
        assert result.id is not None

        # Verify in database
        db_file = db_session.query(DatasetFile).filter(DatasetFile.id == result.id).first()
        assert db_file is not None
        assert db_file.name == "test_data.csv"

    def test_create_dataset_file_file_not_found(self, db_session: Session) -> None:
        """Raise error when file does not exist."""
        service = DatasetFileService(db_session)
        dataset_file_data = DatasetFileCreate(path="/nonexistent/file.csv")

        with pytest.raises(ValidationError) as exc_info:
            service.create_dataset_file(dataset_file_data)

        assert "File not found" in exc_info.value.message

    def test_create_dataset_file_path_is_directory(
        self, db_session: Session, tmp_path: Path
    ) -> None:
        """Raise error when path is a directory."""
        service = DatasetFileService(db_session)
        dataset_file_data = DatasetFileCreate(path=str(tmp_path))

        with pytest.raises(ValidationError) as exc_info:
            service.create_dataset_file(dataset_file_data)

        assert "Path is not a file" in exc_info.value.message

    def test_create_dataset_file_duplicate_path(
        self, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Raise error when dataset file with same path already exists."""
        existing_file = DatasetFile(name="existing.csv", path=str(temp_csv_file))
        db_session.add(existing_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        dataset_file_data = DatasetFileCreate(path=str(temp_csv_file))

        with pytest.raises(ConflictError) as exc_info:
            service.create_dataset_file(dataset_file_data)

        assert "already exists" in exc_info.value.message


class TestGetDatasetFile:
    """Test get_dataset_file method."""

    def test_get_dataset_file_success(self, db_session: Session) -> None:
        """Get dataset file successfully."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        result = service.get_dataset_file(dataset_file.id)

        assert result.id == dataset_file.id
        assert result.name == "test.csv"
        assert result.path == "/path/to/test.csv"

    def test_get_dataset_file_not_found(self, db_session: Session) -> None:
        """Raise error when dataset file not found."""
        service = DatasetFileService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_dataset_file(999)

        assert "not found" in exc_info.value.message

    def test_get_dataset_file_excludes_deleted(self, db_session: Session) -> None:
        """Exclude deleted dataset files from get."""
        dataset_file = DatasetFile(
            name="deleted.csv", path="/path/to/deleted.csv", deleted_at=datetime.datetime.now()
        )
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)

        with pytest.raises(NotFoundError):
            service.get_dataset_file(dataset_file.id)


class TestUpdateDatasetFile:
    """Test update_dataset_file method."""

    def test_update_dataset_file_success(self, db_session: Session, temp_csv_file: Path) -> None:
        """Update dataset file successfully."""
        dataset_file = DatasetFile(name="old.csv", path="/old/path.csv")
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        update_data = DatasetFileUpdate(path=str(temp_csv_file))

        result = service.update_dataset_file(dataset_file.id, update_data)

        assert result.path == str(temp_csv_file)
        assert result.name == "test_data.csv"

    def test_update_dataset_file_no_change(self, db_session: Session) -> None:
        """Update dataset file with no changes."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        update_data = DatasetFileUpdate(path=None)

        result = service.update_dataset_file(dataset_file.id, update_data)

        assert result.path == "/path/to/test.csv"
        assert result.name == "test.csv"

    def test_update_dataset_file_not_found(self, db_session: Session) -> None:
        """Raise error when dataset file not found."""
        service = DatasetFileService(db_session)
        update_data = DatasetFileUpdate(path="/new/path.csv")

        with pytest.raises(NotFoundError) as exc_info:
            service.update_dataset_file(999, update_data)

        assert "not found" in exc_info.value.message

    def test_update_dataset_file_duplicate_path(
        self, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Raise error when updating to duplicate path."""
        dataset_file1 = DatasetFile(name="file1.csv", path="/path/to/file1.csv")
        dataset_file2 = DatasetFile(name="file2.csv", path="/path/to/file2.csv")
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        service = DatasetFileService(db_session)
        update_data = DatasetFileUpdate(path=str(temp_csv_file))

        # First update should work
        service.update_dataset_file(dataset_file1.id, update_data)

        # Second update to same path should fail
        with pytest.raises(ConflictError) as exc_info:
            service.update_dataset_file(dataset_file2.id, update_data)

        assert "already exists" in exc_info.value.message


class TestDeleteDatasetFile:
    """Test delete_dataset_file method."""

    def test_delete_dataset_file_success(self, db_session: Session) -> None:
        """Delete dataset file successfully."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        service.delete_dataset_file(dataset_file.id)

        # Verify deleted
        deleted = db_session.query(DatasetFile).filter(DatasetFile.id == dataset_file.id).first()
        assert deleted is None

    def test_delete_dataset_file_not_found(self, db_session: Session) -> None:
        """Raise error when dataset file not found."""
        service = DatasetFileService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.delete_dataset_file(999)

        assert "not found" in exc_info.value.message

    def test_delete_dataset_file_associated_with_experiment(self, db_session: Session) -> None:
        """Raise error when dataset file is associated with experiment."""
        _project, dataset_file, _experiment = create_project_with_dataset_and_experiment(db_session)

        service = DatasetFileService(db_session)

        with pytest.raises(ConflictError) as exc_info:
            service.delete_dataset_file(dataset_file.id)

        assert "associated with experiment" in exc_info.value.message


class TestGetDatasetFileContent:
    """Test get_dataset_file_content method."""

    def test_get_dataset_file_content_success(
        self, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get dataset file content successfully."""
        dataset_file = DatasetFile(name="test_data.csv", path=str(temp_csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        result = service.get_dataset_file_content(dataset_file.id, pagination)

        assert result.columns == ["id", "name", "value"]
        assert result.total_rows == 3
        assert len(result.rows) == 3
        # Polars preserves types, so numeric values are int/float, not strings
        assert result.rows[0][0] in [1, "1"]  # id
        assert result.rows[0][1] == "Alice"  # name
        assert result.rows[0][2] in [100, "100"]  # value
        assert result.rows[1][0] in [2, "2"]
        assert result.rows[1][1] == "Bob"
        assert result.rows[1][2] in [200, "200"]
        assert result.rows[2][0] in [3, "3"]
        assert result.rows[2][1] == "Charlie"
        assert result.rows[2][2] in [300, "300"]

    def test_get_dataset_file_content_with_pagination(
        self, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get dataset file content with pagination."""
        dataset_file = DatasetFile(name="test_data.csv", path=str(temp_csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=1, limit=2)

        result = service.get_dataset_file_content(dataset_file.id, pagination)

        assert result.total_rows == 3
        assert len(result.rows) == 2
        # Polars preserves types, so numeric values are int/float, not strings
        assert result.rows[0][0] in [2, "2"]
        assert result.rows[0][1] == "Bob"
        assert result.rows[0][2] in [200, "200"]
        assert result.rows[1][0] in [3, "3"]
        assert result.rows[1][1] == "Charlie"
        assert result.rows[1][2] in [300, "300"]

    def test_get_dataset_file_content_semicolon_separator(
        self, db_session: Session, temp_csv_file_semicolon: Path
    ) -> None:
        """Get dataset file content with semicolon separator."""
        dataset_file = DatasetFile(
            name="test_data_semicolon.csv", path=str(temp_csv_file_semicolon)
        )
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        result = service.get_dataset_file_content(dataset_file.id, pagination)

        assert result.columns == ["id", "name", "value"]
        assert result.total_rows == 2
        assert len(result.rows) == 2

    def test_get_dataset_file_content_not_found(self, db_session: Session) -> None:
        """Raise error when dataset file not found."""
        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_dataset_file_content(999, pagination)

        assert "not found" in exc_info.value.message

    def test_get_dataset_file_content_file_not_found(self, db_session: Session) -> None:
        """Raise error when CSV file not found."""
        dataset_file = DatasetFile(name="missing.csv", path="/nonexistent/file.csv")
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_dataset_file_content(dataset_file.id, pagination)

        assert "CSV file not found" in exc_info.value.message

    def test_get_dataset_file_content_empty_file(
        self, db_session: Session, temp_csv_file_empty: Path
    ) -> None:
        """Raise error when CSV file is empty."""
        dataset_file = DatasetFile(name="empty.csv", path=str(temp_csv_file_empty))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_dataset_file_content(dataset_file.id, pagination)

        assert "CSV file is empty" in exc_info.value.message

    def test_get_dataset_file_content_with_none_values(
        self, db_session: Session, tmp_path: Path
    ) -> None:
        """Handle None values in CSV content."""
        csv_file = tmp_path / "test_none.csv"
        csv_file.write_text("id,name,value\n1,Alice,\n2,,200\n")
        dataset_file = DatasetFile(name="test_none.csv", path=str(csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        result = service.get_dataset_file_content(dataset_file.id, pagination)

        assert len(result.rows) == 2
        assert result.rows[0][2] is None  # Empty value should be None
        assert result.rows[1][1] is None  # Empty value should be None

    def test_get_dataset_file_content_with_numeric_types(
        self, db_session: Session, tmp_path: Path
    ) -> None:
        """Handle numeric types in CSV content."""
        csv_file = tmp_path / "test_numeric.csv"
        csv_file.write_text("id,value,score\n1,100,95.5\n2,200,87.3\n")
        dataset_file = DatasetFile(name="test_numeric.csv", path=str(csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        result = service.get_dataset_file_content(dataset_file.id, pagination)

        assert len(result.rows) == 2
        # Values should preserve their types (Polars may infer float for numeric columns)
        assert isinstance(result.rows[0][1], (int, float, str))  # 100
        assert isinstance(result.rows[0][2], (int, float, str))  # 95.5

    def test_get_dataset_file_content_with_complex_types(
        self, db_session: Session, tmp_path: Path
    ) -> None:
        """Handle complex types that need string conversion (covers line 215)."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name\n1,test\n")
        dataset_file = DatasetFile(name="test.csv", path=str(csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        # Mock pl.read_csv to return a DataFrame, then mock slice and to_numpy
        with patch("app.api.services.dataset_file_service.pl.read_csv") as mock_read:
            mock_df = pl.DataFrame({"id": [1], "name": ["test"]})
            mock_read.return_value = mock_df

            # Create a mock for the paginated DataFrame
            mock_paginated_df = MagicMock()

            # Create a custom object that's not int, float, str, bool, or None
            class CustomType:
                """Custom type for testing complex type conversion."""

                def __str__(self) -> str:
                    return "custom_object"

            custom_obj = CustomType()
            mock_paginated_df.to_numpy.return_value = np.array([[1, custom_obj]], dtype=object)

            # Mock the slice method on the DataFrame
            with patch.object(mock_df, "slice", return_value=mock_paginated_df):
                result = service.get_dataset_file_content(dataset_file.id, pagination)
                # The complex type should be converted to string via the else clause (line 215)
                assert len(result.rows) == 1
                assert result.rows[0][0] in [1, "1"]  # First value
                assert isinstance(result.rows[0][1], str)  # Complex type converted to string
                assert "custom_object" in result.rows[0][1]  # Should contain string representation

    def test_get_dataset_file_content_compute_error(
        self, db_session: Session, tmp_path: Path
    ) -> None:
        """Handle ComputeError when parsing CSV."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name\n1,test\n")
        dataset_file = DatasetFile(name="test.csv", path=str(csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        # Mock pl.read_csv to raise ComputeError
        with patch("app.api.services.dataset_file_service.pl.read_csv") as mock_read:
            mock_read.side_effect = polars.exceptions.ComputeError("Parse error")
            with pytest.raises(ValueError) as exc_info:
                service.get_dataset_file_content(dataset_file.id, pagination)
            assert "Error parsing CSV file" in str(exc_info.value)

    def test_get_dataset_file_content_generic_exception(
        self, db_session: Session, tmp_path: Path
    ) -> None:
        """Handle generic Exception when reading CSV."""

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name\n1,test\n")
        dataset_file = DatasetFile(name="test.csv", path=str(csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        service = DatasetFileService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        # Mock pl.read_csv to raise a generic exception
        with patch("app.api.services.dataset_file_service.pl.read_csv") as mock_read:
            mock_read.side_effect = RuntimeError("Unexpected error")
            with pytest.raises(ValueError) as exc_info:
                service.get_dataset_file_content(dataset_file.id, pagination)
            assert "Error reading CSV file" in str(exc_info.value)
