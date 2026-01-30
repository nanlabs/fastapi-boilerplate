"""Test helper functions for creating test data."""

from sqlalchemy.orm import Session

from app.db.models.dataset_file import DatasetFile
from app.db.models.experiment import Experiment
from app.db.models.experiment_type import ExperimentType
from app.db.models.project import Project


def create_experiment_type(
    name: str = "Classification",
) -> ExperimentType:
    """Create an ExperimentType instance for testing with default values."""
    return ExperimentType(name=name)


def create_project_with_dataset_and_experiment(
    db_session: Session,
    project_name: str = "Test Project",
    dataset_file_name: str = "test.csv",
    dataset_file_path: str = "/path/to/test.csv",
    experiment_name: str = "Test Experiment",
) -> tuple[Project, DatasetFile, Experiment]:
    """Create a project, dataset file, and experiment for testing."""
    project = Project(name=project_name)
    dataset_file = DatasetFile(name=dataset_file_name, path=dataset_file_path)
    db_session.add_all([project, dataset_file])
    db_session.commit()
    experiment = Experiment(
        name=experiment_name, project_id=project.id, dataset_file_id=dataset_file.id
    )
    db_session.add(experiment)
    db_session.commit()
    return project, dataset_file, experiment
