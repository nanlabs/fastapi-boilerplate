"""Unit tests for app.api.endpoints.experiments."""

# pylint: disable=too-many-lines,duplicate-code

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session

from app.api.exceptions import SortingValidationError
from app.api.services.dependencies import get_experiment_service
from app.api.services.experiment_service import ExperimentService
from app.db.models.dataset_file import DatasetFile
from app.db.models.experiment import Experiment
from app.db.models.experiment_type import ExperimentType
from app.db.models.project import Project
from app.main import app
from app.schemas.common.base import ExperimentStatus


@pytest.fixture(autouse=True)
def _cleanup_experiments(db_session: Session) -> None:
    """Clean up experiments, projects, experiment types, and dataset files before each test."""
    db_session.query(Experiment).delete()
    db_session.query(DatasetFile).delete()
    db_session.query(Project).delete()
    db_session.query(ExperimentType).delete()
    db_session.commit()


@pytest.fixture(name="temp_csv_file")
def _temp_csv_file(tmp_path: Path) -> Path:
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")
    return csv_file


class TestGetExperimentStatuses:
    """Test get_experiment_statuses endpoint."""

    def test_get_experiment_statuses_success(self, client: TestClient) -> None:
        """Get experiment statuses successfully."""
        response = client.get("/api/experiments/statuses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        # Verify all status values are present
        expected_statuses = [status.value for status in ExperimentStatus]
        assert len(data["data"]) == len(expected_statuses)
        assert set(data["data"]) == set(expected_statuses)


class TestListExperiments:
    """Test list_experiments endpoint."""

    def test_list_experiments_success(self, client: TestClient, db_session: Session) -> None:
        """List experiments successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Test Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Test description",
        )
        db_session.add(experiment)
        db_session.commit()

        response = client.get(f"/api/experiments?project_id={project.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "sort" in data
        assert "search" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Test Experiment"

    def test_list_experiments_empty(self, client: TestClient, db_session: Session) -> None:
        """List experiments when database is empty."""
        project = Project(name="Test Project", description="Description")
        db_session.add(project)
        db_session.commit()

        response = client.get(f"/api/experiments?project_id={project.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []

    def test_list_experiments_with_pagination(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List experiments with pagination."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        for i in range(5):
            experiment = Experiment(
                name=f"Experiment {i}",
                project_id=project.id,
                experiment_type_id=experiment_type.id,
                description="Description",
            )
            db_session.add(experiment)
        db_session.commit()

        response = client.get(f"/api/experiments?project_id={project.id}&skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_list_experiments_with_search(self, client: TestClient, db_session: Session) -> None:
        """List experiments with search filter."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Machine Learning Exp",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="ML experiment",
        )
        exp2 = Experiment(
            name="Data Analysis Exp",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Analysis experiment",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        response = client.get(f"/api/experiments?project_id={project.id}&search=Machine")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Machine Learning Exp"

    def test_list_experiments_with_experiment_type_filter(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List experiments filtered by experiment_type_id."""
        project = Project(name="Test Project", description="Description")
        exp_type1 = ExperimentType(
            name="Classification",
        )
        exp_type2 = ExperimentType(
            name="Regression",
        )
        db_session.add_all([project, exp_type1, exp_type2])
        db_session.commit()

        exp1 = Experiment(
            name="Exp 1",
            project_id=project.id,
            experiment_type_id=exp_type1.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Exp 2",
            project_id=project.id,
            experiment_type_id=exp_type2.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        response = client.get(
            f"/api/experiments?project_id={project.id}&experiment_type_id={exp_type1.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Exp 1"

    def test_list_experiments_sorting_validation_error(self, client: TestClient) -> None:
        """Raise 400 error when sorting by invalid field."""
        # Override service dependency to raise SortingValidationError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.list_experiments.side_effect = SortingValidationError(
            "Invalid sort field 'invalid_field'. Valid fields are: id, name"
        )

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.get("/api/experiments?project_id=1&sort_by=invalid_field")

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "detail" in data
            assert "Invalid sort field" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_experiments_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.list_experiments.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.get("/api/experiments?project_id=1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while listing experiments" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_experiments_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.list_experiments.side_effect = ValueError("Unexpected error")

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.get("/api/experiments?project_id=1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while listing experiments" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestCreateExperiment:
    """Test create_experiment endpoint."""

    def test_create_experiment_success(self, client: TestClient, db_session: Session) -> None:
        """Create experiment successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment_data = {
            "name": "Test Experiment",
            "project_id": project.id,
            "experiment_type_id": experiment_type.id,
            "description": "Test description",
        }

        response = client.post("/api/experiments", json=experiment_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Experiment"
        assert data["project_id"] == project.id
        assert data["experiment_type_id"] == experiment_type.id
        assert data["description"] == "Test description"
        assert "status" in data
        assert "current_step" in data
        assert data["current_step"] == 0

    def test_create_experiment_without_description(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Create experiment without description."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment_data = {
            "name": "Test Experiment",
            "project_id": project.id,
            "experiment_type_id": experiment_type.id,
            "description": None,
        }

        response = client.post("/api/experiments", json=experiment_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Experiment"
        assert data["description"] is None
        assert "status" in data
        assert "current_step" in data
        assert data["current_step"] == 0

    def test_create_experiment_not_found(self, client: TestClient) -> None:
        """Raise 404 error when project or experiment type not found."""
        experiment_data = {
            "name": "Test Experiment",
            "project_id": 999,
            "experiment_type_id": 1,
            "description": "Test description",
        }

        response = client.post("/api/experiments", json=experiment_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Project with ID 999 not found" in data["detail"]

    def test_create_experiment_integrity_error(self, client: TestClient) -> None:
        """Raise 409 error when integrity error occurs."""
        # Override service dependency to raise IntegrityError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.create_experiment.side_effect = IntegrityError(
            "Constraint violation", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            experiment_data = {
                "name": "Test Experiment",
                "project_id": 1,
                "experiment_type_id": 1,
                "description": "Test description",
            }

            response = client.post("/api/experiments", json=experiment_data)

            assert response.status_code == status.HTTP_409_CONFLICT
            data = response.json()
            assert "detail" in data
            assert (
                "Database constraint violation occurred while creating experiment" in data["detail"]
            )
        finally:
            app.dependency_overrides.clear()

    def test_create_experiment_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.create_experiment.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            experiment_data = {
                "name": "Test Experiment",
                "project_id": 1,
                "experiment_type_id": 1,
                "description": "Test description",
            }

            response = client.post("/api/experiments", json=experiment_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while creating experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_create_experiment_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.create_experiment.side_effect = ValueError("Unexpected error")

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            experiment_data = {
                "name": "Test Experiment",
                "project_id": 1,
                "experiment_type_id": 1,
                "description": "Test description",
            }

            response = client.post("/api/experiments", json=experiment_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while creating experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestGetExperiment:
    """Test get_experiment endpoint."""

    def test_get_experiment_success(self, client: TestClient, db_session: Session) -> None:
        """Get experiment by ID successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Test Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Test description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        response = client.get(f"/api/experiments/{experiment_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == experiment_id
        assert data["name"] == "Test Experiment"
        assert data["project_id"] == project.id
        assert data["experiment_type_id"] == experiment_type.id
        assert "status" in data
        assert "current_step" in data
        assert data["current_step"] == 0

    def test_get_experiment_not_found(self, client: TestClient) -> None:
        """Raise 404 error when experiment not found."""
        response = client.get("/api/experiments/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Experiment with ID 999 not found" in data["detail"]

    def test_get_experiment_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.get_experiment.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.get("/api/experiments/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while retrieving experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_get_experiment_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.get_experiment.side_effect = ValueError("Unexpected error")

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.get("/api/experiments/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while retrieving experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestUpdateExperiment:
    """Test update_experiment endpoint."""

    def test_update_experiment_success(self, client: TestClient, db_session: Session) -> None:
        """Update experiment successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Old Name",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Old description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        experiment_update = {"name": "New Name", "description": "New description"}

        response = client.patch(f"/api/experiments/{experiment_id}", json=experiment_update)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New description"
        assert "status" in data
        assert "current_step" in data

    def test_update_experiment_not_found(self, client: TestClient) -> None:
        """Raise 404 error when experiment not found."""
        experiment_update = {"name": "New Name"}

        response = client.patch("/api/experiments/999", json=experiment_update)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Experiment with ID 999 not found" in data["detail"]

    def test_update_experiment_integrity_error(self, client: TestClient) -> None:
        """Raise 409 error when integrity error occurs."""
        # Override service dependency to raise IntegrityError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.update_experiment.side_effect = IntegrityError(
            "Constraint violation", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            experiment_update = {"name": "New Name"}

            response = client.patch("/api/experiments/1", json=experiment_update)

            assert response.status_code == status.HTTP_409_CONFLICT
            data = response.json()
            assert "detail" in data
            assert (
                "Database constraint violation occurred while updating experiment" in data["detail"]
            )
        finally:
            app.dependency_overrides.clear()

    def test_update_experiment_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.update_experiment.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            experiment_update = {"name": "New Name"}

            response = client.patch("/api/experiments/1", json=experiment_update)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while updating experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_update_experiment_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.update_experiment.side_effect = ValueError("Unexpected error")

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            experiment_update = {"name": "New Name"}

            response = client.patch("/api/experiments/1", json=experiment_update)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while updating experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestDeleteExperiment:
    """Test delete_experiment endpoint."""

    def test_delete_experiment_success(self, client: TestClient, db_session: Session) -> None:
        """Delete experiment successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = ExperimentType(
            name="Classification",
        )
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="To Delete",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        response = client.delete(f"/api/experiments/{experiment_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Verify deleted
        deleted_experiment = (
            db_session.query(Experiment).filter(Experiment.id == experiment_id).first()
        )
        assert deleted_experiment is None

    def test_delete_experiment_not_found(self, client: TestClient) -> None:
        """Raise 404 error when experiment not found."""
        response = client.delete("/api/experiments/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Experiment with ID 999 not found" in data["detail"]

    def test_delete_experiment_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.delete_experiment.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.delete("/api/experiments/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while deleting experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_delete_experiment_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.delete_experiment.side_effect = ValueError("Unexpected error")

        def override_get_experiment_service():
            return mock_service

        app.dependency_overrides[get_experiment_service] = override_get_experiment_service

        try:
            response = client.delete("/api/experiments/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while deleting experiment" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestAttachDatasetToExperiment:
    """Test attach_dataset_to_experiment endpoint."""

    def test_attach_dataset_with_path_success(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Attach dataset file to experiment by creating new dataset file."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.post(
            f"/api/experiments/{experiment.id}/dataset",
            json={"path": str(temp_csv_file)},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "test_data.csv"

        # Verify experiment was updated
        db_session.refresh(experiment)
        assert experiment.dataset_file_id is not None
        assert experiment.status == ExperimentStatus.IN_PROGRESS.value

    def test_attach_dataset_with_existing_id_success(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Attach existing dataset file to experiment by ID."""
        project = Project(name="Test Project")
        dataset_file = DatasetFile(name="existing.csv", path="/path/to/existing.csv")
        db_session.add_all([project, dataset_file])
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.post(
            f"/api/experiments/{experiment.id}/dataset",
            json={"dataset_file_id": dataset_file.id},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == dataset_file.id

        # Verify experiment was updated
        db_session.refresh(experiment)
        assert experiment.dataset_file_id == dataset_file.id
        assert experiment.status == ExperimentStatus.IN_PROGRESS.value

    def test_attach_dataset_experiment_not_found(
        self, client: TestClient, temp_csv_file: Path
    ) -> None:
        """Return error when experiment not found."""
        response = client.post(
            "/api/experiments/999/dataset",
            json={"path": str(temp_csv_file)},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_attach_dataset_file_not_found(self, client: TestClient, db_session: Session) -> None:
        """Return error when dataset file not found."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.post(
            f"/api/experiments/{experiment.id}/dataset",
            json={"dataset_file_id": 999},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_attach_dataset_file_not_found_path(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Return error when file does not exist."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.post(
            f"/api/experiments/{experiment.id}/dataset",
            json={"path": "/nonexistent/file.csv"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File not found" in response.json()["detail"]

    def test_attach_dataset_invalid_request_no_params(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Return error when neither path nor dataset_file_id is provided."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.post(
            f"/api/experiments/{experiment.id}/dataset",
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_attach_dataset_invalid_request_both_params(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Return error when both path and dataset_file_id are provided."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.post(
            f"/api/experiments/{experiment.id}/dataset",
            json={"path": str(temp_csv_file), "dataset_file_id": 1},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_attach_dataset_database_error(self, client: TestClient, temp_csv_file: Path) -> None:
        """Handle database error when attaching dataset."""
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.attach_dataset_file.side_effect = DatabaseError("DB error", None, Exception())

        app.dependency_overrides[get_experiment_service] = lambda: mock_service

        try:
            response = client.post(
                "/api/experiments/1/dataset",
                json={"path": str(temp_csv_file)},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_attach_dataset_value_error(self, client: TestClient, db_session: Session) -> None:
        """Handle ValueError when attaching dataset (e.g., path is None bypassing validator)."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        mock_service = MagicMock(spec=ExperimentService)
        mock_service.attach_dataset_file.side_effect = ValueError("Path must be provided")

        app.dependency_overrides[get_experiment_service] = lambda: mock_service

        try:
            response = client.post(
                f"/api/experiments/{experiment.id}/dataset",
                json={"path": "/some/path.csv"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        finally:
            app.dependency_overrides.clear()

    def test_attach_dataset_unexpected_error(self, client: TestClient, temp_csv_file: Path) -> None:
        """Handle unexpected error when attaching dataset."""
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.attach_dataset_file.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_experiment_service] = lambda: mock_service

        try:
            response = client.post(
                "/api/experiments/1/dataset",
                json={"path": str(temp_csv_file)},
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()


class TestGetExperimentDatasetContent:
    """Test get_experiment_dataset_content endpoint."""

    def test_get_experiment_dataset_content_success(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get experiment dataset content successfully."""
        project = Project(name="Test Project")
        dataset_file = DatasetFile(name="test_data.csv", path=str(temp_csv_file))
        db_session.add_all([project, dataset_file])
        db_session.commit()
        experiment = Experiment(
            name="Test Experiment", project_id=project.id, dataset_file_id=dataset_file.id
        )
        db_session.add(experiment)
        db_session.commit()

        response = client.get(f"/api/experiments/{experiment.id}/dataset/content")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "columns" in data
        assert "rows" in data
        assert "total_rows" in data
        assert data["columns"] == ["id", "name", "value"]
        assert data["total_rows"] == 2

    def test_get_experiment_dataset_content_with_pagination(
        self, client: TestClient, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get experiment dataset content with pagination."""
        project = Project(name="Test Project")
        dataset_file = DatasetFile(name="test_data.csv", path=str(temp_csv_file))
        db_session.add_all([project, dataset_file])
        db_session.commit()
        experiment = Experiment(
            name="Test Experiment", project_id=project.id, dataset_file_id=dataset_file.id
        )
        db_session.add(experiment)
        db_session.commit()

        response = client.get(f"/api/experiments/{experiment.id}/dataset/content?skip=1&limit=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_rows"] == 2
        assert len(data["rows"]) == 1

    def test_get_experiment_dataset_content_experiment_not_found(self, client: TestClient) -> None:
        """Return error when experiment not found."""
        response = client.get("/api/experiments/999/dataset/content")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_get_experiment_dataset_content_no_dataset(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Return error when experiment has no associated dataset file."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        response = client.get(f"/api/experiments/{experiment.id}/dataset/content")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "has no associated dataset file" in response.json()["detail"]

    def test_get_experiment_dataset_content_database_error(self, client: TestClient) -> None:
        """Handle database error when getting experiment dataset content."""
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.get_experiment_dataset_content.side_effect = DatabaseError(
            "DB error", None, Exception()
        )

        app.dependency_overrides[get_experiment_service] = lambda: mock_service

        try:
            response = client.get("/api/experiments/1/dataset/content")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()

    def test_get_experiment_dataset_content_value_error(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Handle ValueError when getting experiment dataset content."""
        project = Project(name="Test Project")
        dataset_file = DatasetFile(name="test.csv", path="/path/to/test.csv")
        db_session.add_all([project, dataset_file])
        db_session.commit()
        experiment = Experiment(
            name="Test Experiment", project_id=project.id, dataset_file_id=dataset_file.id
        )
        db_session.add(experiment)
        db_session.commit()

        mock_service = MagicMock(spec=ExperimentService)
        mock_service.get_experiment_dataset_content.side_effect = ValueError("Error parsing CSV")

        app.dependency_overrides[get_experiment_service] = lambda: mock_service

        try:
            response = client.get(f"/api/experiments/{experiment.id}/dataset/content")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        finally:
            app.dependency_overrides.clear()

    def test_get_experiment_dataset_content_unexpected_error(self, client: TestClient) -> None:
        """Handle unexpected error when getting experiment dataset content."""
        mock_service = MagicMock(spec=ExperimentService)
        mock_service.get_experiment_dataset_content.side_effect = Exception("Unexpected error")

        app.dependency_overrides[get_experiment_service] = lambda: mock_service

        try:
            response = client.get("/api/experiments/1/dataset/content")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            app.dependency_overrides.clear()
