"""Unit tests for app.api.services.experiment_type_service."""

import pytest
from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import PaginationParams, SearchParams, SortDirection, SortingParams
from app.api.services.experiment_type_service import ExperimentTypeService
from app.db.models.experiment_type import ExperimentType
from tests.helpers import create_experiment_type


@pytest.fixture(autouse=True)
def _cleanup_experiment_types(db_session: Session) -> None:
    """Clean up experiment types before each test."""
    db_session.query(ExperimentType).delete()
    db_session.commit()


class TestExperimentTypeServiceInit:
    """Test ExperimentTypeService initialization."""

    def test_init(self, db_session: Session) -> None:
        """Initialize service with database session."""
        service = ExperimentTypeService(db_session)
        assert service.db == db_session


class TestGetExperimentType:
    """Test get_experiment_type method."""

    def test_get_experiment_type_success(self, db_session: Session) -> None:
        """Get experiment type by ID successfully."""
        experiment_type = create_experiment_type()
        db_session.add(experiment_type)
        db_session.commit()
        experiment_type_id = experiment_type.id

        service = ExperimentTypeService(db_session)
        result = service.get_experiment_type(experiment_type_id)

        assert result.id == experiment_type_id
        assert result.name == "Classification"

    def test_get_experiment_type_not_found(self, db_session: Session) -> None:
        """Raise error when experiment type not found."""
        service = ExperimentTypeService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_experiment_type(999)

        assert "Experiment type with ID 999 not found" in str(exc_info.value.message)


class TestListExperimentTypes:
    """Test list_experiment_types method."""

    def test_list_experiment_types_empty(self, db_session: Session) -> None:
        """List experiment types when database is empty."""
        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert result.data == []
        assert result.pagination == pagination
        assert result.sort == sorting
        assert result.search == search_params

    def test_list_experiment_types_with_data(self, db_session: Session) -> None:
        """List experiment types with existing data."""
        exp_type1 = create_experiment_type(name="Classification")
        exp_type2 = create_experiment_type(name="Regression")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name in ["Classification", "Regression"]
        assert result.data[1].name in ["Classification", "Regression"]

    def test_list_experiment_types_with_search(self, db_session: Session) -> None:
        """List experiment types with search filter."""
        exp_type1 = create_experiment_type(name="Classification")
        exp_type2 = create_experiment_type(name="Regression")
        exp_type3 = create_experiment_type(name="Clustering")
        db_session.add_all([exp_type1, exp_type2, exp_type3])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="Class")

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Classification"

    def test_list_experiment_types_with_sorting_by_name_asc(self, db_session: Session) -> None:
        """List experiment types sorted by name ascending."""
        exp_type1 = create_experiment_type(name="Zebra Type")
        exp_type2 = create_experiment_type(name="Alpha Type")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Alpha Type"
        assert result.data[1].name == "Zebra Type"

    def test_list_experiment_types_with_sorting_by_name_desc(self, db_session: Session) -> None:
        """List experiment types sorted by name descending."""
        exp_type1 = create_experiment_type(name="Alpha Type")
        exp_type2 = create_experiment_type(name="Zebra Type")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.DESC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Zebra Type"
        assert result.data[1].name == "Alpha Type"

    def test_list_experiment_types_with_sorting_by_id(self, db_session: Session) -> None:
        """List experiment types sorted by id."""
        exp_type1 = create_experiment_type(name="Type 1")
        exp_type2 = create_experiment_type(name="Type 2")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="id", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].id < result.data[1].id

    def test_list_experiment_types_with_invalid_sort_field(self, db_session: Session) -> None:
        """Raise error when sorting by invalid field."""
        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="invalid_field", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        with pytest.raises(SortingValidationError) as exc_info:
            service.list_experiment_types(pagination, sorting, search_params)

        assert "Invalid sort field 'invalid_field'" in str(exc_info.value.message)

    def test_list_experiment_types_default_sort(self, db_session: Session) -> None:
        """List experiment types with default sort (by id ascending)."""
        exp_type1 = create_experiment_type(name="Type 2")
        exp_type2 = create_experiment_type(name="Type 1")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].id < result.data[1].id

    def test_list_experiment_types_with_pagination(self, db_session: Session) -> None:
        """List experiment types with pagination."""
        experiment_types = [create_experiment_type(name=f"Type {i}") for i in range(5)]
        db_session.add_all(experiment_types)
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=2, limit=2)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2

    def test_list_experiment_types_with_all_fields(self, db_session: Session) -> None:
        """List experiment types with all boolean fields set."""
        exp_type1 = create_experiment_type(name="Available Type")
        exp_type2 = create_experiment_type(name="Coming Soon Type")
        db_session.add_all([exp_type1, exp_type2])
        db_session.commit()

        service = ExperimentTypeService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiment_types(pagination, sorting, search_params)

        assert len(result.data) == 2
        for exp_type in result.data:
            assert exp_type.id is not None
            assert exp_type.name is not None
