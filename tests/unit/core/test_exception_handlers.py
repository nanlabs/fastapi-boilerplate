"""Tests for global exception handlers."""

from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError

from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError
from app.api.services.dependencies import get_project_service
from app.api.services.project_service import ProjectService
from app.main import app


def _override_service_with(exc: Exception) -> None:
    mock = MagicMock(spec=ProjectService)
    mock.list_projects.side_effect = exc
    mock.create_project.side_effect = exc
    mock.get_project.side_effect = exc
    mock.update_project.side_effect = exc
    mock.delete_project.side_effect = exc
    app.dependency_overrides[get_project_service] = lambda: mock


class TestNotFoundHandler:
    def test_not_found_returns_404_envelope(self, client: TestClient) -> None:
        _override_service_with(NotFoundError("Project with ID 99 not found"))
        try:
            resp = client.get("/api/v1/projects/99")
            assert resp.status_code == status.HTTP_404_NOT_FOUND
            data = resp.json()
            assert data["success"] is False
            assert data["dev_code"] == "NOT_FOUND"
            assert "99" in data["message"]
            assert data["data"] is None
            assert "request_id" in data["metadata"]
        finally:
            app.dependency_overrides.clear()


class TestConflictHandler:
    def test_conflict_returns_409_envelope(self, client: TestClient) -> None:
        _override_service_with(ConflictError("Project with name 'X' already exists"))
        try:
            resp = client.post("/api/v1/projects", json={"name": "X"})
            assert resp.status_code == status.HTTP_409_CONFLICT
            data = resp.json()
            assert data["success"] is False
            assert data["dev_code"] == "CONFLICT"
        finally:
            app.dependency_overrides.clear()


class TestSortingValidationHandler:
    def test_invalid_sort_returns_400_envelope(self, client: TestClient) -> None:
        _override_service_with(SortingValidationError("Invalid sort field 'bad_field'"))
        try:
            resp = client.get("/api/v1/projects?sort_by=bad_field")
            assert resp.status_code == status.HTTP_400_BAD_REQUEST
            data = resp.json()
            assert data["success"] is False
            assert data["dev_code"] == "INVALID_SORT_FIELD"
        finally:
            app.dependency_overrides.clear()


class TestDatabaseErrorHandler:
    def test_db_error_returns_500_envelope(self, client: TestClient) -> None:
        _override_service_with(DatabaseError("DB failure", None, Exception()))  # type: ignore[arg-type]
        try:
            resp = client.get("/api/v1/projects")
            assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = resp.json()
            assert data["success"] is False
            assert data["dev_code"] == "DATABASE_ERROR"
        finally:
            app.dependency_overrides.clear()


class TestUnexpectedErrorHandler:
    def test_unexpected_error_returns_500_envelope(self) -> None:
        _override_service_with(RuntimeError("Something went wrong"))
        try:
            with TestClient(app, raise_server_exceptions=False) as client:
                resp = client.get("/api/v1/projects")
            assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = resp.json()
            assert data["success"] is False
            assert data["dev_code"] == "INTERNAL_ERROR"
        finally:
            app.dependency_overrides.clear()


class TestValidationErrorHandler:
    def test_invalid_body_returns_422_envelope(self, client: TestClient) -> None:
        resp = client.post("/api/v1/projects", json={"name": ""})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = resp.json()
        assert data["success"] is False
        assert data["dev_code"] == "VALIDATION_ERROR"
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0
