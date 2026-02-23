"""Unit tests for app.api.services.dependencies."""

from sqlalchemy.orm import Session

from app.api.services.dependencies import get_project_service
from app.api.services.project_service import ProjectService


class TestGetProjectService:
    """Test get_project_service dependency function."""

    def test_get_project_service(self, db_session: Session) -> None:
        """Return ProjectService instance with injected database session."""
        result = get_project_service(db_session)

        assert isinstance(result, ProjectService)
        assert result.db == db_session
