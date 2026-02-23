"""Dependency functions for service injection."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.services.project_service import ProjectService
from app.db.session import get_db


def get_project_service(db: Annotated[Session, Depends(get_db)]) -> ProjectService:
    """Get ProjectService instance with injected database session."""
    return ProjectService(db)
