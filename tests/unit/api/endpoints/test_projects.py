"""Unit tests for app.api.endpoints.v1.projects."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.project import Project


@pytest.fixture(autouse=True)
def _cleanup_projects(db_session: Session) -> None:
    db_session.query(Project).delete()
    db_session.commit()


class TestListProjects:
    def test_list_projects_success(self, client: TestClient, db_session: Session) -> None:
        project = Project(name="Test Project", description="Description")
        db_session.add(project)
        db_session.commit()

        response = client.get("/api/v1/projects")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["dev_code"] == "PROJECTS_LISTED"
        assert body["metadata"]["request_id"]
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Test Project"
        assert body["metadata"]["pagination"]["total"] == 1

    def test_list_projects_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/projects")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"] == []
        assert body["metadata"]["pagination"]["total"] == 0

    def test_list_projects_with_pagination(self, client: TestClient, db_session: Session) -> None:
        for idx in range(5):
            db_session.add(Project(name=f"Project {idx}", description="Description"))
        db_session.commit()

        response = client.get("/api/v1/projects?skip=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert len(body["data"]) == 2
        assert body["metadata"]["pagination"]["skip"] == 2
        assert body["metadata"]["pagination"]["limit"] == 2
        assert body["metadata"]["pagination"]["total"] == 5

    def test_list_projects_invalid_sort_returns_envelope(self, client: TestClient) -> None:
        response = client.get("/api/v1/projects?sort_by=invalid_field")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = response.json()
        assert body["success"] is False
        assert body["dev_code"] == "INVALID_SORT_FIELD"
        assert body["data"] is None


class TestCreateProject:
    def test_create_project_success(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "Test description"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["success"] is True
        assert body["dev_code"] == "PROJECT_CREATED"
        assert body["data"]["name"] == "Test Project"

    def test_create_project_conflict(self, client: TestClient, db_session: Session) -> None:
        db_session.add(Project(name="Existing Project", description="Description"))
        db_session.commit()

        response = client.post(
            "/api/v1/projects",
            json={"name": "Existing Project", "description": "Other"},
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        body = response.json()
        assert body["success"] is False
        assert body["dev_code"] == "CONFLICT"
        assert body["data"] is None


class TestGetProject:
    def test_get_project_success(self, client: TestClient, db_session: Session) -> None:
        project = Project(name="Test Project", description="Description")
        db_session.add(project)
        db_session.commit()

        response = client.get(f"/api/v1/projects/{project.id}")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["dev_code"] == "PROJECT_RETRIEVED"
        assert body["data"]["id"] == project.id

    def test_get_project_not_found(self, client: TestClient) -> None:
        response = client.get("/api/v1/projects/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        body = response.json()
        assert body["success"] is False
        assert body["dev_code"] == "NOT_FOUND"
        assert body["data"] is None


class TestUpdateProject:
    def test_update_project_success(self, client: TestClient, db_session: Session) -> None:
        project = Project(name="Old Name", description="Old description")
        db_session.add(project)
        db_session.commit()

        response = client.patch(
            f"/api/v1/projects/{project.id}",
            json={"name": "New Name", "description": "New description"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["dev_code"] == "PROJECT_UPDATED"
        assert body["data"]["name"] == "New Name"


class TestDeleteProject:
    def test_delete_project_success(self, client: TestClient, db_session: Session) -> None:
        project = Project(name="To Delete", description="Description")
        db_session.add(project)
        db_session.commit()

        response = client.delete(f"/api/v1/projects/{project.id}")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["dev_code"] == "PROJECT_DELETED"
        assert body["data"] is None

        deleted_project = db_session.query(Project).filter(Project.id == project.id).first()
        assert deleted_project is None
