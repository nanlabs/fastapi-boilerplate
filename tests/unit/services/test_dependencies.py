"""Unit tests for app.api.services.dependencies."""

from sqlalchemy.orm import Session

from app.api.services.dependencies import (
    get_experiment_service,
    get_project_service,
)
from app.api.services.experiment_service import ExperimentService
from app.api.services.project_service import ProjectService


class TestGetProjectService:
    """Test get_project_service dependency function."""

    def test_get_project_service(self, db_session: Session) -> None:
        """Return ProjectService instance with injected database session."""
        result = get_project_service(db_session)

        assert isinstance(result, ProjectService)
        assert result.db == db_session


class TestGetExperimentService:
    """Test get_experiment_service dependency function."""

    def test_get_experiment_service(self, db_session: Session) -> None:
        """Return ExperimentService instance with injected database session."""
        result = get_experiment_service(db_session)

        assert isinstance(result, ExperimentService)
        assert result.db == db_session
