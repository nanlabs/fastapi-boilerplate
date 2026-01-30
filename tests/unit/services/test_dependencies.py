"""Unit tests for app.api.services.dependencies."""

from sqlalchemy.orm import Session

from app.api.services.dependencies import (
    get_experiment_service,
    get_experiment_type_service,
    get_model_type_service,
    get_project_service,
)
from app.api.services.experiment_service import ExperimentService
from app.api.services.experiment_type_service import ExperimentTypeService
from app.api.services.model_type_service import ModelTypeService
from app.api.services.project_service import ProjectService


class TestGetProjectService:
    """Test get_project_service dependency function."""

    def test_get_project_service(self, db_session: Session) -> None:
        """Return ProjectService instance with injected database session."""
        result = get_project_service(db_session)

        assert isinstance(result, ProjectService)
        assert result.db == db_session


class TestGetExperimentTypeService:
    """Test get_experiment_type_service dependency function."""

    def test_get_experiment_type_service(self, db_session: Session) -> None:
        """Return ExperimentTypeService instance with injected database session."""
        result = get_experiment_type_service(db_session)

        assert isinstance(result, ExperimentTypeService)
        assert result.db == db_session


class TestGetModelTypeService:
    """Test get_model_type_service dependency function."""

    def test_get_model_type_service(self, db_session: Session) -> None:
        """Return ModelTypeService instance with injected database session."""
        result = get_model_type_service(db_session)

        assert isinstance(result, ModelTypeService)
        assert result.db == db_session


class TestGetExperimentService:
    """Test get_experiment_service dependency function."""

    def test_get_experiment_service(self, db_session: Session) -> None:
        """Return ExperimentService instance with injected database session."""
        result = get_experiment_service(db_session)

        assert isinstance(result, ExperimentService)
        assert result.db == db_session
