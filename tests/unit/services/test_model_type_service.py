"""Unit tests for app.api.services.model_type_service."""

from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import PaginationParams, SearchParams, SortDirection, SortingParams
from app.api.services.model_type_service import ModelTypeService
from app.db.models.model_type import ModelType
from app.schemas.common.base import ModelTypeStatus


@pytest.fixture(autouse=True)
def _cleanup_model_types(db_session: Session) -> None:
    """Clean up model types before each test."""
    db_session.query(ModelType).delete()
    db_session.commit()


class TestModelTypeServiceInit:
    """Test ModelTypeService initialization."""

    def test_init(self, db_session: Session) -> None:
        """Initialize service with database session."""
        service = ModelTypeService(db_session)
        assert service.db == db_session


class TestGetModelType:
    """Test get_model_type method."""

    def test_get_model_type_success(self, db_session: Session) -> None:
        """Get model type by ID successfully."""
        model_type = ModelType(
            id=1,
            name="Credit Model",
            description="Credit scoring model",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add(model_type)
        db_session.commit()
        model_type_id = model_type.id

        service = ModelTypeService(db_session)
        result = service.get_model_type(model_type_id)

        assert result.id == model_type_id
        assert result.name == "Credit Model"
        assert result.description == "Credit scoring model"
        assert result.enabled is True
        assert result.status == ModelTypeStatus.AVAILABLE

    def test_get_model_type_not_found(self, db_session: Session) -> None:
        """Raise error when model type not found."""
        service = ModelTypeService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_model_type(999)

        assert "Model type with ID 999 not found" in str(exc_info.value.message)

    def test_get_model_type_excludes_deleted(self, db_session: Session) -> None:
        """Exclude deleted model types from query."""
        model_type = ModelType(
            id=1,
            name="Deleted Model",
            description="This is deleted",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type.deleted_at = datetime.now()
        db_session.add(model_type)
        db_session.commit()

        service = ModelTypeService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_model_type(1)

        assert "Model type with ID 1 not found" in str(exc_info.value.message)


class TestListModelTypes:
    """Test list_model_types method."""

    def test_list_model_types_empty(self, db_session: Session) -> None:
        """List model types when database is empty."""
        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert result.data == []
        assert result.pagination == pagination
        assert result.sort == sorting
        assert result.search == search_params

    def test_list_model_types_with_data(self, db_session: Session) -> None:
        """List model types with existing data."""
        model_type1 = ModelType(
            id=1,
            name="Credit Model",
            description="Credit scoring",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=2,
            name="Fraud Model",
            description="Fraud detection",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name in ["Credit Model", "Fraud Model"]
        assert result.data[1].name in ["Credit Model", "Fraud Model"]

    def test_list_model_types_with_search(self, db_session: Session) -> None:
        """List model types with search filter."""
        model_type1 = ModelType(
            id=1,
            name="Credit Model",
            description="Credit scoring",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=2,
            name="Fraud Model",
            description="Fraud detection",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type3 = ModelType(
            id=3,
            name="Marketing Model",
            description="Marketing analytics",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add_all([model_type1, model_type2, model_type3])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="Credit")

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Credit Model"

    def test_list_model_types_with_sorting_by_name_asc(self, db_session: Session) -> None:
        """List model types sorted by name ascending."""
        model_type1 = ModelType(
            id=1,
            name="Zebra Model",
            description="Zebra",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=2,
            name="Alpha Model",
            description="Alpha",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Alpha Model"
        assert result.data[1].name == "Zebra Model"

    def test_list_model_types_with_sorting_by_name_desc(self, db_session: Session) -> None:
        """List model types sorted by name descending."""
        model_type1 = ModelType(
            id=1,
            name="Alpha Model",
            description="Alpha",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=2,
            name="Zebra Model",
            description="Zebra",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.DESC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Zebra Model"
        assert result.data[1].name == "Alpha Model"

    def test_list_model_types_with_sorting_by_id(self, db_session: Session) -> None:
        """List model types sorted by id."""
        model_type1 = ModelType(
            id=1,
            name="Model 1",
            description="First",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=2,
            name="Model 2",
            description="Second",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="id", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].id < result.data[1].id

    def test_list_model_types_with_invalid_sort_field(self, db_session: Session) -> None:
        """Raise error when sorting by invalid field."""
        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="invalid_field", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        with pytest.raises(SortingValidationError) as exc_info:
            service.list_model_types(pagination, sorting, search_params)

        assert "Invalid sort field 'invalid_field'" in str(exc_info.value.message)
        assert "Valid fields are:" in str(exc_info.value.message)

    def test_list_model_types_default_sort(self, db_session: Session) -> None:
        """List model types with default sort (by id ascending)."""
        model_type1 = ModelType(
            id=2,
            name="Model 2",
            description="Second",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=1,
            name="Model 1",
            description="First",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].id < result.data[1].id

    def test_list_model_types_with_pagination(self, db_session: Session) -> None:
        """List model types with pagination."""
        model_types = [
            ModelType(
                id=i,
                name=f"Model {i}",
                description=f"Description {i}",
                enabled=True,
                status=ModelTypeStatus.AVAILABLE.value,
            )
            for i in range(1, 6)
        ]
        db_session.add_all(model_types)
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=2, limit=2)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 2

    def test_list_model_types_excludes_deleted(self, db_session: Session) -> None:
        """Exclude deleted model types from list."""
        model_type1 = ModelType(
            id=1,
            name="Active Model",
            description="Active",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2 = ModelType(
            id=2,
            name="Deleted Model",
            description="Deleted",
            enabled=True,
            status=ModelTypeStatus.AVAILABLE.value,
        )
        model_type2.deleted_at = datetime.now()
        db_session.add_all([model_type1, model_type2])
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Active Model"

    def test_list_model_types_builds_response_correctly(self, db_session: Session) -> None:
        """Verify that _build_model_type_response is called correctly."""
        model_type = ModelType(
            id=1,
            name="Test Model",
            description="Test description",
            enabled=False,
            status=ModelTypeStatus.REQUEST_ACCESS.value,
        )
        db_session.add(model_type)
        db_session.commit()

        service = ModelTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_model_types(pagination, sorting, search_params)

        assert len(result.data) == 1
        response = result.data[0]
        assert response.id == 1
        assert response.name == "Test Model"
        assert response.description == "Test description"
        assert response.enabled is False
        assert response.status == ModelTypeStatus.REQUEST_ACCESS
