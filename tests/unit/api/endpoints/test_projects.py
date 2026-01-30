"""Unit tests for app.api.endpoints.projects."""

# pylint: disable=duplicate-code

from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session

from app.api.exceptions import SortingValidationError
from app.api.services.dependencies import get_project_service
from app.api.services.project_service import ProjectService
from app.db.models.experiment import Experiment
from app.db.models.project import Project
from app.main import app


@pytest.fixture(autouse=True)
def _cleanup_projects(db_session: Session) -> None:
    """Clean up projects and experiments before each test."""
    db_session.query(Experiment).delete()
    db_session.query(Project).delete()
    db_session.commit()


class TestListProjects:
    """Test list_projects endpoint."""

    def test_list_projects_success(self, client: TestClient, db_session: Session) -> None:
        """List projects successfully."""
        project = Project(name="Test Project", description="Description")
        db_session.add(project)
        db_session.commit()

        response = client.get("/api/projects")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "sort" in data
        assert "search" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Test Project"

    def test_list_projects_empty(self, client: TestClient) -> None:
        """List projects when database is empty."""
        response = client.get("/api/projects")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []

    def test_list_projects_with_pagination(self, client: TestClient, db_session: Session) -> None:
        """List projects with pagination."""
        for i in range(5):
            project = Project(name=f"Project {i}", description="Description")
            db_session.add(project)
        db_session.commit()

        response = client.get("/api/projects?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_list_projects_with_search(self, client: TestClient, db_session: Session) -> None:
        """List projects with search filter."""
        project1 = Project(name="Machine Learning Project", description="ML project")
        project2 = Project(name="Data Analysis Project", description="Analysis project")
        db_session.add_all([project1, project2])
        db_session.commit()

        response = client.get("/api/projects?search=Machine")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Machine Learning Project"

    def test_list_projects_with_sorting(self, client: TestClient, db_session: Session) -> None:
        """List projects with sorting."""
        project1 = Project(name="Zebra Project", description="Description")
        project2 = Project(name="Alpha Project", description="Description")
        db_session.add_all([project1, project2])
        db_session.commit()

        response = client.get("/api/projects?sort_by=name&sort_direction=asc")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Alpha Project"
        assert data["data"][1]["name"] == "Zebra Project"

    def test_list_projects_sorting_validation_error(self, client: TestClient) -> None:
        """Raise 400 error when sorting by invalid field."""
        # Override service dependency to raise SortingValidationError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.list_projects.side_effect = SortingValidationError(
            "Invalid sort field 'invalid_field'. Valid fields are: id, name"
        )

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            response = client.get("/api/projects?sort_by=invalid_field")

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "detail" in data
            assert "Invalid sort field" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_projects_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.list_projects.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            response = client.get("/api/projects")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while listing projects" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_projects_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ProjectService)
        mock_service.list_projects.side_effect = ValueError("Unexpected error")

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            response = client.get("/api/projects")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while listing projects" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestCreateProject:
    """Test create_project endpoint."""

    def test_create_project_success(self, client: TestClient) -> None:
        """Create project successfully."""
        project_data = {"name": "Test Project", "description": "Test description"}

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "Test description"
        assert data["id"] is not None

    def test_create_project_without_description(self, client: TestClient) -> None:
        """Create project without description."""
        project_data = {"name": "Test Project", "description": None}

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] is None

    def test_create_project_conflict_error(self, client: TestClient, db_session: Session) -> None:
        """Raise 409 error when project name already exists."""
        project = Project(name="Existing Project", description="Description")
        db_session.add(project)
        db_session.commit()

        project_data = {"name": "Existing Project", "description": "New description"}

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "detail" in data
        assert "Project with name 'Existing Project' already exists" in data["detail"]

    def test_create_project_integrity_error(self, client: TestClient) -> None:
        """Raise 409 error when integrity error occurs."""
        # Override service dependency to raise IntegrityError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.create_project.side_effect = IntegrityError(
            "Constraint violation", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            project_data = {"name": "Test Project", "description": "Test description"}

            response = client.post("/api/projects", json=project_data)

            assert response.status_code == status.HTTP_409_CONFLICT
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while creating project" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_create_project_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.create_project.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            project_data = {"name": "Test Project", "description": "Test description"}

            response = client.post("/api/projects", json=project_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while creating project" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_create_project_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ProjectService)
        mock_service.create_project.side_effect = ValueError("Unexpected error")

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            project_data = {"name": "Test Project", "description": "Test description"}

            response = client.post("/api/projects", json=project_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while creating project" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestGetProject:
    """Test get_project endpoint."""

    def test_get_project_success(self, client: TestClient, db_session: Session) -> None:
        """Get project by ID successfully."""
        project = Project(name="Test Project", description="Description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        response = client.get(f"/api/projects/{project_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "Test Project"
        assert data["description"] == "Description"

    def test_get_project_not_found(self, client: TestClient) -> None:
        """Raise 404 error when project not found."""
        response = client.get("/api/projects/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Project with ID 999 not found" in data["detail"]

    def test_get_project_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.get_project.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            response = client.get("/api/projects/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while retrieving project" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_get_project_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ProjectService)
        mock_service.get_project.side_effect = ValueError("Unexpected error")

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            response = client.get("/api/projects/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while retrieving project" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestUpdateProject:
    """Test update_project endpoint."""

    def test_update_project_success(self, client: TestClient, db_session: Session) -> None:
        """Update project successfully."""
        project = Project(name="Old Name", description="Old description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        project_update = {"name": "New Name", "description": "New description"}

        response = client.patch(f"/api/projects/{project_id}", json=project_update)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New description"

    def test_update_project_not_found(self, client: TestClient) -> None:
        """Raise 404 error when project not found."""
        project_update = {"name": "New Name"}

        response = client.patch("/api/projects/999", json=project_update)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Project with ID 999 not found" in data["detail"]

    def test_update_project_conflict_error(self, client: TestClient, db_session: Session) -> None:
        """Raise 409 error when project name already exists."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        db_session.add_all([project1, project2])
        db_session.commit()

        project_update = {"name": "Project 2"}

        response = client.patch(f"/api/projects/{project1.id}", json=project_update)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "detail" in data
        assert "Project with name 'Project 2' already exists" in data["detail"]

    def test_update_project_integrity_error(self, client: TestClient) -> None:
        """Raise 409 error when integrity error occurs."""
        # Override service dependency to raise IntegrityError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.update_project.side_effect = IntegrityError(
            "Constraint violation", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            project_update = {"name": "New Name"}

            response = client.patch("/api/projects/1", json=project_update)

            assert response.status_code == status.HTTP_409_CONFLICT
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while updating project" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_update_project_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.update_project.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            project_update = {"name": "New Name"}

            response = client.patch("/api/projects/1", json=project_update)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while updating project" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_update_project_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ProjectService)
        mock_service.update_project.side_effect = ValueError("Unexpected error")

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            project_update = {"name": "New Name"}

            response = client.patch("/api/projects/1", json=project_update)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while updating project" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestDeleteProject:
    """Test delete_project endpoint."""

    def test_delete_project_success(self, client: TestClient, db_session: Session) -> None:
        """Delete project successfully."""
        project = Project(name="To Delete", description="Description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        response = client.delete(f"/api/projects/{project_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Verify deleted
        deleted_project = db_session.query(Project).filter(Project.id == project_id).first()
        assert deleted_project is None

    def test_delete_project_not_found(self, client: TestClient) -> None:
        """Raise 404 error when project not found."""
        response = client.delete("/api/projects/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Project with ID 999 not found" in data["detail"]

    def test_delete_project_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ProjectService)
        mock_service.delete_project.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_project_service():
            return mock_service

        app.dependency_overrides[get_project_service] = override_get_project_service

        try:
            response = client.delete("/api/projects/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while deleting project" in data["detail"]
        finally:
            app.dependency_overrides.clear()
