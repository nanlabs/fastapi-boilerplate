"""Unit tests for app.api.endpoints.dataset_files."""

# pylint: disable=duplicate-code

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session

from app.api.services.dataset_file_service import DatasetFileService
from app.api.services.dependencies import get_dataset_file_service
from app.db.models.dataset_file import DatasetFile
from app.db.models.experiment import Experiment
from app.db.models.project import Project
from app.main import app


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
    csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")
    return csv_file


class TestListDatasetFiles:
    """Test list_dataset_files endpoint."""

    def test_list_dataset_files_success(self, client: TestClient, db_session: Session) -> None:
        """List dataset files successfully."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        response = client.get("/api/dataset-files")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "test.csv"

    def test_list_dataset_files_empty(self, client: TestClient) -> None:
        """List dataset files when database is empty."""
        response = client.get("/api/dataset-files")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []

    def test_list_dataset_files_with_pagination(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List dataset files with pagination."""
        for i in range(5):
            dataset_file = DatasetFile(name=f"file{i}.csv", path=f"/path/to/file{i}.csv")
            db_session.add(dataset_file)
        db_session.commit()

        response = client.get("/api/dataset-files?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_list_dataset_files_with_search(self, client: TestClient, db_session: Session) -> None:
        """List dataset files with search filter."""
        dataset_file1 = DatasetFile(name="test_file.csv", path="/path/to/test_file.csv")
        dataset_file2 = DatasetFile(name="other_file.csv", path="/path/to/other_file.csv")
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        response = client.get("/api/dataset-files?search=test")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "test_file.csv"

    def test_list_dataset_files_invalid_sort_field(self, client: TestClient) -> None:
        """Return error when invalid sort field is provided."""
        response = client.get("/api/dataset-files?sort_by=invalid_field")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_dataset_files_database_error(self, client: TestClient) -> None:
        """Handle database error when listing dataset files."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.list_dataset_files.side_effect = DatabaseError("DB error", None, Exception())

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get("/api/dataset-files")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_list_dataset_files_unexpected_error(self, client: TestClient) -> None:
        """Handle unexpected error when listing dataset files."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.list_dataset_files.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get("/api/dataset-files")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()


class TestCreateDatasetFile:
    """Test create_dataset_file endpoint."""

    def test_create_dataset_file_success(self, client: TestClient, temp_csv_file: Path) -> None:
        """Create dataset file successfully."""
        response = client.post("/api/dataset-files", json={"path": str(temp_csv_file)})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "test_data.csv"
        assert data["path"] == str(temp_csv_file)

    def test_create_dataset_file_file_not_found(self, client: TestClient) -> None:
        """Return error when file does not exist."""
        response = client.post("/api/dataset-files", json={"path": "/nonexistent/file.csv"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File not found" in response.json()["detail"]

    def test_create_dataset_file_path_is_directory(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Return error when path is a directory."""
        response = client.post("/api/dataset-files", json={"path": str(tmp_path)})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Path is not a file" in response.json()["detail"]

    def test_create_dataset_file_duplicate_path(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Return error when dataset file with same path already exists."""
        dataset_file = DatasetFile(name="existing.csv", path=str(temp_csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        response = client.post("/api/dataset-files", json={"path": str(temp_csv_file)})

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]

    def test_create_dataset_file_integrity_error(
        self, client: TestClient, temp_csv_file: Path
    ) -> None:
        """Handle integrity error when creating dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.create_dataset_file.side_effect = IntegrityError(
            "Integrity error", None, Exception()
        )

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.post("/api/dataset-files", json={"path": str(temp_csv_file)})
            assert response.status_code == status.HTTP_409_CONFLICT
        finally:
            app.dependency_overrides.clear()

    def test_create_dataset_file_database_error(
        self, client: TestClient, temp_csv_file: Path
    ) -> None:
        """Handle database error when creating dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.create_dataset_file.side_effect = DatabaseError("DB error", None, Exception())

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.post("/api/dataset-files", json={"path": str(temp_csv_file)})
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_create_dataset_file_unexpected_error(
        self, client: TestClient, temp_csv_file: Path
    ) -> None:
        """Handle unexpected error when creating dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.create_dataset_file.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.post("/api/dataset-files", json={"path": str(temp_csv_file)})
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()


class TestGetDatasetFile:
    """Test get_dataset_file endpoint."""

    def test_get_dataset_file_success(self, client: TestClient, db_session: Session) -> None:
        """Get dataset file successfully."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        response = client.get(f"/api/dataset-files/{dataset_file.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == dataset_file.id
        assert data["name"] == "test.csv"

    def test_get_dataset_file_not_found(self, client: TestClient) -> None:
        """Return error when dataset file not found."""
        response = client.get("/api/dataset-files/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_get_dataset_file_database_error(self, client: TestClient) -> None:
        """Handle database error when getting dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.get_dataset_file.side_effect = DatabaseError("DB error", None, Exception())

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get("/api/dataset-files/1")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_get_dataset_file_unexpected_error(self, client: TestClient) -> None:
        """Handle unexpected error when getting dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.get_dataset_file.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get("/api/dataset-files/1")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()


class TestUpdateDatasetFile:
    """Test update_dataset_file endpoint."""

    def test_update_dataset_file_success(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Update dataset file successfully."""
        dataset_file = DatasetFile(name="old.csv", path="/old/path.csv")
        db_session.add(dataset_file)
        db_session.commit()

        response = client.patch(
            f"/api/dataset-files/{dataset_file.id}",
            json={"path": str(temp_csv_file)},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["path"] == str(temp_csv_file)
        assert data["name"] == "test_data.csv"

    def test_update_dataset_file_not_found(self, client: TestClient) -> None:
        """Return error when dataset file not found."""
        response = client.patch("/api/dataset-files/999", json={"path": "/new/path.csv"})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_update_dataset_file_duplicate_path(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Return error when updating to duplicate path."""
        dataset_file1 = DatasetFile(name="file1.csv", path="/path/to/file1.csv")
        dataset_file2 = DatasetFile(name="file2.csv", path="/path/to/file2.csv")
        db_session.add_all([dataset_file1, dataset_file2])
        db_session.commit()

        # First update should work
        client.patch(f"/api/dataset-files/{dataset_file1.id}", json={"path": str(temp_csv_file)})

        # Second update to same path should fail
        response = client.patch(
            f"/api/dataset-files/{dataset_file2.id}", json={"path": str(temp_csv_file)}
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]

    def test_update_dataset_file_integrity_error(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Handle integrity error when updating dataset file."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.update_dataset_file.side_effect = IntegrityError(
            "Integrity error", None, Exception()
        )

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.patch(
                f"/api/dataset-files/{dataset_file.id}", json={"path": "/new/path.csv"}
            )
            assert response.status_code == status.HTTP_409_CONFLICT
        finally:
            app.dependency_overrides.clear()

    def test_update_dataset_file_database_error(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Handle database error when updating dataset file."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.update_dataset_file.side_effect = DatabaseError("DB error", None, Exception())

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.patch(
                f"/api/dataset-files/{dataset_file.id}", json={"path": "/new/path.csv"}
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_update_dataset_file_unexpected_error(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Handle unexpected error when updating dataset file."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.update_dataset_file.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.patch(
                f"/api/dataset-files/{dataset_file.id}", json={"path": "/new/path.csv"}
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()


class TestDeleteDatasetFile:
    """Test delete_dataset_file endpoint."""

    def test_delete_dataset_file_success(self, client: TestClient, db_session: Session) -> None:
        """Delete dataset file successfully."""
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        response = client.delete(f"/api/dataset-files/{dataset_file.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_dataset_file_not_found(self, client: TestClient) -> None:
        """Return error when dataset file not found."""
        response = client.delete("/api/dataset-files/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_delete_dataset_file_associated_with_experiment(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Return error when dataset file is associated with experiment."""
        project = Project(name="Test Project")
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add_all([project, dataset_file])
        db_session.commit()
        experiment = Experiment(
            name="Test Experiment", project_id=project.id, dataset_file_id=dataset_file.id
        )
        db_session.add(experiment)
        db_session.commit()

        response = client.delete(f"/api/dataset-files/{dataset_file.id}")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "associated with experiment" in response.json()["detail"]

    def test_delete_dataset_file_database_error(self, client: TestClient) -> None:
        """Handle database error when deleting dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.delete_dataset_file.side_effect = DatabaseError("DB error", None, Exception())

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.delete("/api/dataset-files/1")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_delete_dataset_file_unexpected_error(self, client: TestClient) -> None:
        """Handle unexpected error when deleting dataset file."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.delete_dataset_file.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.delete("/api/dataset-files/1")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()


class TestGetDatasetFileContent:
    """Test get_dataset_file_content endpoint."""

    def test_get_dataset_file_content_success(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get dataset file content successfully."""
        dataset_file = DatasetFile(name="test_data.csv", path=str(temp_csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        response = client.get(f"/api/dataset-files/{dataset_file.id}/content")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "columns" in data
        assert "rows" in data
        assert "total_rows" in data
        assert data["columns"] == ["id", "name", "value"]
        assert data["total_rows"] == 2

    def test_get_dataset_file_content_with_pagination(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get dataset file content with pagination."""
        dataset_file = DatasetFile(name="test_data.csv", path=str(temp_csv_file))
        db_session.add(dataset_file)
        db_session.commit()

        response = client.get(f"/api/dataset-files/{dataset_file.id}/content?skip=1&limit=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_rows"] == 2
        assert len(data["rows"]) == 1

    def test_get_dataset_file_content_not_found(self, client: TestClient) -> None:
        """Return error when dataset file not found."""
        response = client.get("/api/dataset-files/999/content")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_get_dataset_file_content_file_not_found(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Return error when CSV file not found."""
        dataset_file = DatasetFile(name="missing.csv", path="/nonexistent/file.csv")
        db_session.add(dataset_file)
        db_session.commit()

        response = client.get(f"/api/dataset-files/{dataset_file.id}/content")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "CSV file not found" in response.json()["detail"]

    def test_get_dataset_file_content_parse_error(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Return error when CSV file cannot be parsed."""

        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add(dataset_file)
        db_session.commit()

        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.get_dataset_file_content.side_effect = ValueError(
            "Error parsing CSV file: /path/to/test.csv"
        )

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get(f"/api/dataset-files/{dataset_file.id}/content")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        finally:
            app.dependency_overrides.clear()

    def test_get_dataset_file_content_database_error(self, client: TestClient) -> None:
        """Handle database error when getting dataset file content."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.get_dataset_file_content.side_effect = DatabaseError(
            "DB error", None, Exception()
        )

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get("/api/dataset-files/1/content")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_get_dataset_file_content_unexpected_error(self, client: TestClient) -> None:
        """Handle unexpected error when getting dataset file content."""
        mock_service = MagicMock(spec=DatasetFileService)
        mock_service.get_dataset_file_content.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_dataset_file_service] = lambda: mock_service

        try:
            response = client.get("/api/dataset-files/1/content")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()
