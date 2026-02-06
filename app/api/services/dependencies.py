"""Dependency functions for service injection."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.services.dataset_file_service import DatasetFileService
from app.api.services.experiment_service import ExperimentService
from app.api.services.project_service import ProjectService
from app.db.session import get_db


def get_project_service(db: Annotated[Session, Depends(get_db)]) -> ProjectService:
    """Get ProjectService instance with injected database session."""
    return ProjectService(db)


def get_experiment_service(db: Annotated[Session, Depends(get_db)]) -> ExperimentService:
    """Get ExperimentService instance with injected database session."""
    return ExperimentService(db)


def get_dataset_file_service(db: Annotated[Session, Depends(get_db)]) -> DatasetFileService:
    """Get DatasetFileService instance with injected database session."""
    return DatasetFileService(db)
