"""Unit tests for app.api.endpoints.experiment_types."""

# pylint: disable=duplicate-code

from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.api.exceptions import SortingValidationError
from app.api.services.dependencies import get_experiment_type_service
from app.api.services.experiment_type_service import ExperimentTypeService
from app.db.models.experiment_type import ExperimentType
from app.main import app


@pytest.fixture(autouse=True)
def _cleanup_experiment_types(db_session: Session) -> None:
    """Clean up experiment types before each test."""
    db_session.query(ExperimentType).delete()
    db_session.commit()


class TestListExperimentTypes:
    """Test list_experiment_types endpoint."""

    def test_list_experiment_types_success(self, client: TestClient, db_session: Session) -> None:
        """List experiment types successfully."""
        experiment_type = ExperimentType(name="Classification")
        db_session.add(experiment_type)
        db_session.commit()

        response = client.get("/api/experiment-types")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "sort" in data
        assert "search" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Classification"

    def test_list_experiment_types_empty(self, client: TestClient) -> None:
        """List experiment types when database is empty."""
        response = client.get("/api/experiment-types")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []

    def test_list_experiment_types_with_pagination(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List experiment types with pagination."""
        for i in range(5):
            experiment_type = ExperimentType(name=f"Type {i}")
            db_session.add(experiment_type)
        db_session.commit()

        response = client.get("/api/experiment-types?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_list_experiment_types_with_search(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List experiment types with search filter."""
        exp_type1 = ExperimentType(name="Classification")
        exp_type2 = ExperimentType(name="Regression")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        response = client.get("/api/experiment-types?search=Class")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Classification"

    def test_list_experiment_types_with_sorting(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List experiment types with sorting."""
        exp_type1 = ExperimentType(name="Zebra Type")
        exp_type2 = ExperimentType(name="Alpha Type")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        response = client.get("/api/experiment-types?sort_by=name&sort_direction=asc")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Alpha Type"
        assert data["data"][1]["name"] == "Zebra Type"

    def test_list_experiment_types_sorting_validation_error(self, client: TestClient) -> None:
        """Raise 400 error when sorting by invalid field."""
        # Override service dependency to raise SortingValidationError
        mock_service = MagicMock(spec=ExperimentTypeService)
        mock_service.list_experiment_types.side_effect = SortingValidationError(
            "Invalid sort field 'invalid_field'. Valid fields are: id, name"
        )

        def override_get_experiment_type_service():
            return mock_service

        app.dependency_overrides[get_experiment_type_service] = override_get_experiment_type_service

        try:
            response = client.get("/api/experiment-types?sort_by=invalid_field")

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "detail" in data
            assert "Invalid sort field" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_experiment_types_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentTypeService)
        mock_service.list_experiment_types.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_type_service():
            return mock_service

        app.dependency_overrides[get_experiment_type_service] = override_get_experiment_type_service

        try:
            response = client.get("/api/experiment-types")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while listing experiment types" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_experiment_types_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentTypeService)
        mock_service.list_experiment_types.side_effect = ValueError("Unexpected error")

        def override_get_experiment_type_service():
            return mock_service

        app.dependency_overrides[get_experiment_type_service] = override_get_experiment_type_service

        try:
            response = client.get("/api/experiment-types")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while listing experiment types" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestGetExperimentType:
    """Test get_experiment_type endpoint."""

    def test_get_experiment_type_success(self, client: TestClient, db_session: Session) -> None:
        """Get experiment type by ID successfully."""
        experiment_type = ExperimentType(name="Classification")
        db_session.add(experiment_type)
        db_session.commit()
        experiment_type_id = experiment_type.id

        response = client.get(f"/api/experiment-types/{experiment_type_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == experiment_type_id
        assert data["name"] == "Classification"

    def test_get_experiment_type_not_found(self, client: TestClient) -> None:
        """Raise 404 error when experiment type not found."""
        response = client.get("/api/experiment-types/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Experiment type with ID 999 not found" in data["detail"]

    def test_get_experiment_type_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ExperimentTypeService)
        mock_service.get_experiment_type.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_experiment_type_service():
            return mock_service

        app.dependency_overrides[get_experiment_type_service] = override_get_experiment_type_service

        try:
            response = client.get("/api/experiment-types/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while retrieving experiment type" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_get_experiment_type_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ExperimentTypeService)
        mock_service.get_experiment_type.side_effect = ValueError("Unexpected error")

        def override_get_experiment_type_service():
            return mock_service

        app.dependency_overrides[get_experiment_type_service] = override_get_experiment_type_service

        try:
            response = client.get("/api/experiment-types/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while retrieving experiment type" in data["detail"]
        finally:
            app.dependency_overrides.clear()
