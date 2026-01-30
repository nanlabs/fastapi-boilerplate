"""Unit tests for app.api.endpoints.model_types."""

# pylint: disable=duplicate-code

from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.api.exceptions import SortingValidationError
from app.api.services.dependencies import get_model_type_service
from app.api.services.model_type_service import ModelTypeService
from app.db.models.model_type import ModelType
from app.main import app


@pytest.fixture(autouse=True)
def _cleanup_model_types(db_session: Session) -> None:
    """Clean up model types before each test."""
    db_session.query(ModelType).delete()
    db_session.commit()


class TestListModelTypes:
    """Test list_model_types endpoint."""

    def test_list_model_types_success(self, client: TestClient, db_session: Session) -> None:
        """List model types successfully."""
        model_type = ModelType(name="Credit Models", description="Credit risk models", enabled=True)
        db_session.add(model_type)
        db_session.commit()

        response = client.get("/api/model-types")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "sort" in data
        assert "search" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Credit Models"

    def test_list_model_types_empty(self, client: TestClient) -> None:
        """List model types when database is empty."""
        response = client.get("/api/model-types")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []

    def test_list_model_types_with_pagination(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List model types with pagination."""
        for i in range(5):
            model_type = ModelType(name=f"Type {i}", enabled=True)
            db_session.add(model_type)
        db_session.commit()

        response = client.get("/api/model-types?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    def test_list_model_types_with_search(self, client: TestClient, db_session: Session) -> None:
        """List model types with search filter."""
        model_type1 = ModelType(name="Credit Models", enabled=True)
        model_type2 = ModelType(name="Fraud Models", enabled=True)
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        response = client.get("/api/model-types?search=Credit")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Credit Models"

    def test_list_model_types_with_sorting(self, client: TestClient, db_session: Session) -> None:
        """List model types with sorting."""
        model_type1 = ModelType(name="Zebra Type", enabled=True)
        model_type2 = ModelType(name="Alpha Type", enabled=True)
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        response = client.get("/api/model-types?sort_by=name&sort_direction=asc")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Alpha Type"
        assert data["data"][1]["name"] == "Zebra Type"

    def test_list_model_types_sorting_validation_error(self, client: TestClient) -> None:
        """Raise 400 error when sorting by invalid field."""
        # Override service dependency to raise SortingValidationError
        mock_service = MagicMock(spec=ModelTypeService)
        mock_service.list_model_types.side_effect = SortingValidationError(
            "Invalid sort field 'invalid_field'. Valid fields are: id, name"
        )

        def override_get_model_type_service():
            return mock_service

        app.dependency_overrides[get_model_type_service] = override_get_model_type_service

        try:
            response = client.get("/api/model-types?sort_by=invalid_field")

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "detail" in data
            assert "Invalid sort field" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_model_types_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ModelTypeService)
        mock_service.list_model_types.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_model_type_service():
            return mock_service

        app.dependency_overrides[get_model_type_service] = override_get_model_type_service

        try:
            response = client.get("/api/model-types")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while listing model types" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_list_model_types_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ModelTypeService)
        mock_service.list_model_types.side_effect = ValueError("Unexpected error")

        def override_get_model_type_service():
            return mock_service

        app.dependency_overrides[get_model_type_service] = override_get_model_type_service

        try:
            response = client.get("/api/model-types")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while listing model types" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestGetModelType:
    """Test get_model_type endpoint."""

    def test_get_model_type_success(self, client: TestClient, db_session: Session) -> None:
        """Get model type by ID successfully."""
        model_type = ModelType(name="Credit Models", description="Credit risk models", enabled=True)
        db_session.add(model_type)
        db_session.commit()
        model_type_id = model_type.id

        response = client.get(f"/api/model-types/{model_type_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == model_type_id
        assert data["name"] == "Credit Models"

    def test_get_model_type_not_found(self, client: TestClient) -> None:
        """Raise 404 error when model type not found."""
        response = client.get("/api/model-types/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Model type with ID 999 not found" in data["detail"]

    def test_get_model_type_database_error(self, client: TestClient) -> None:
        """Raise 500 error when database error occurs."""
        # Override service dependency to raise DatabaseError
        mock_service = MagicMock(spec=ModelTypeService)
        mock_service.get_model_type.side_effect = DatabaseError(
            "Database error", None, Exception()
        )  # type: ignore[arg-type]

        def override_get_model_type_service():
            return mock_service

        app.dependency_overrides[get_model_type_service] = override_get_model_type_service

        try:
            response = client.get("/api/model-types/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Database error occurred while retrieving model type" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_get_model_type_unexpected_error(self, client: TestClient) -> None:
        """Raise 500 error when unexpected error occurs."""
        # Override service dependency to raise generic Exception
        mock_service = MagicMock(spec=ModelTypeService)
        mock_service.get_model_type.side_effect = ValueError("Unexpected error")

        def override_get_model_type_service():
            return mock_service

        app.dependency_overrides[get_model_type_service] = override_get_model_type_service

        try:
            response = client.get("/api/model-types/1")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "An unexpected error occurred while retrieving model type" in data["detail"]
        finally:
            app.dependency_overrides.clear()
