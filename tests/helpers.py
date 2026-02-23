"""Test helper functions for creating test data."""

from sqlalchemy.orm import Session

from app.db.models.project import Project


def create_project(
    db_session: Session,
    project_name: str = "Test Project",
    description: str | None = None,
) -> Project:
    """Create and persist a project for testing."""
    project = Project(name=project_name)
    if description is not None:
        project.description = description
    db_session.add(project)
    db_session.commit()
    return project
