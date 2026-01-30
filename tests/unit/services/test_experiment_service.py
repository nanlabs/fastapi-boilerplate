"""Unit tests for app.api.services.experiment_service."""

# pylint: disable=too-many-lines,duplicate-code

from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import PaginationParams, SearchParams, SortDirection, SortingParams
from app.api.schemas.experiment import ExperimentAttachDataset, ExperimentCreate, ExperimentUpdate
from app.api.services.experiment_service import ExperimentService
from app.db.models.dataset_file import DatasetFile
from app.db.models.experiment import Experiment
from app.db.models.experiment_type import ExperimentType
from app.db.models.project import Project
from app.schemas.common.base import ExperimentStatus
from tests.helpers import create_experiment_type, create_project_with_dataset_and_experiment


@pytest.fixture(autouse=True)
def _cleanup_experiments(db_session: Session) -> None:
    """Clean up experiments, projects, experiment types, and dataset files before each test."""
    db_session.query(Experiment).delete()
    db_session.query(DatasetFile).delete()
    db_session.query(Project).delete()
    db_session.query(ExperimentType).delete()
    db_session.commit()


@pytest.fixture(name="temp_csv_file")
def _temp_csv_file(tmp_path: Path) -> Path:
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")
    return csv_file


class TestExperimentServiceInit:
    """Test ExperimentService initialization."""

    def test_init(self, db_session: Session) -> None:
        """Initialize service with database session."""
        service = ExperimentService(db_session)
        assert service.db == db_session


class TestCreateExperiment:
    """Test create_experiment method."""

    def test_create_experiment_success(self, db_session: Session) -> None:
        """Create experiment successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        service = ExperimentService(db_session)
        experiment_data = ExperimentCreate(
            name="Test Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Test description",
        )

        result = service.create_experiment(experiment_data)

        assert result.name == "Test Experiment"
        assert result.project_id == project.id
        assert result.experiment_type_id == experiment_type.id
        assert result.description == "Test description"
        assert result.id is not None
        assert result.status is not None
        assert result.current_step == 0

        # Verify in database
        db_experiment = db_session.query(Experiment).filter(Experiment.id == result.id).first()
        assert db_experiment is not None
        assert db_experiment.name == "Test Experiment"

    def test_create_experiment_without_description(self, db_session: Session) -> None:
        """Create experiment without description."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        service = ExperimentService(db_session)
        experiment_data = ExperimentCreate(
            name="Test Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description=None,
        )

        result = service.create_experiment(experiment_data)

        assert result.name == "Test Experiment"
        assert result.description is None

    def test_create_experiment_project_not_found(self, db_session: Session) -> None:
        """Raise error when project not found."""
        experiment_type = create_experiment_type()
        db_session.add(experiment_type)
        db_session.commit()

        service = ExperimentService(db_session)
        experiment_data = ExperimentCreate(
            name="Test Experiment",
            project_id=999,
            experiment_type_id=experiment_type.id,
            description="Test description",
        )

        with pytest.raises(NotFoundError) as exc_info:
            service.create_experiment(experiment_data)

        assert "Project with ID 999 not found" in str(exc_info.value.message)

    def test_create_experiment_type_not_found(self, db_session: Session) -> None:
        """Raise error when experiment type not found."""
        project = Project(name="Test Project", description="Description")
        db_session.add(project)
        db_session.commit()

        service = ExperimentService(db_session)
        experiment_data = ExperimentCreate(
            name="Test Experiment",
            project_id=project.id,
            experiment_type_id=999,
            description="Test description",
        )

        with pytest.raises(NotFoundError) as exc_info:
            service.create_experiment(experiment_data)

        assert "Experiment type with ID 999 not found" in str(exc_info.value.message)


class TestGetExperiment:
    """Test get_experiment method."""

    def test_get_experiment_success(self, db_session: Session) -> None:
        """Get experiment by ID successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Test Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Test description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        result = service.get_experiment(experiment_id)

        assert result.id == experiment_id
        assert result.name == "Test Experiment"
        assert result.project_id == project.id
        assert result.experiment_type_id == experiment_type.id
        assert result.status is not None
        assert result.current_step == 0
        # Verify ml_experiment_id property returns UUID (access from model, not response)
        db_experiment = db_session.query(Experiment).filter(Experiment.id == experiment_id).first()
        assert db_experiment is not None
        assert isinstance(db_experiment.ml_experiment_id, UUID)
        # Verify the UUID can be converted back to string (round-trip test)
        assert str(db_experiment.ml_experiment_id) == str(UUID(str(db_experiment.ml_experiment_id)))

    def test_get_experiment_not_found(self, db_session: Session) -> None:
        """Raise error when experiment not found."""
        service = ExperimentService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_experiment(999)

        assert "Experiment with ID 999 not found" in str(exc_info.value.message)


class TestListExperiments:
    """Test list_experiments method."""

    def test_list_experiments_empty(self, db_session: Session) -> None:
        """List experiments when database is empty."""
        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert result.data == []
        assert result.pagination == pagination
        assert result.sort == sorting
        assert result.search == search_params

    def test_list_experiments_with_data(self, db_session: Session) -> None:
        """List experiments with existing data."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Experiment 1",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description 1",
        )
        exp2 = Experiment(
            name="Experiment 2",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description 2",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name in ["Experiment 1", "Experiment 2"]
        assert result.data[1].name in ["Experiment 1", "Experiment 2"]

    def test_list_experiments_with_search(self, db_session: Session) -> None:
        """List experiments with search filter."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Machine Learning Exp",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="ML experiment",
        )
        exp2 = Experiment(
            name="Data Analysis Exp",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Analysis experiment",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="Machine")

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Machine Learning Exp"

    def test_list_experiments_with_search_in_description(self, db_session: Session) -> None:
        """List experiments with search matching description."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Search Test A",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Machine Learning experiment",
        )
        exp2 = Experiment(
            name="Search Test B",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Data analysis",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="Learning")

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Search Test A"

    def test_list_experiments_with_project_filter(self, db_session: Session) -> None:
        """List experiments filtered by project_id."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project1, project2, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Exp 1",
            project_id=project1.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Exp 2",
            project_id=project2.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(
            pagination, sorting, search_params, project_id=project1.id
        )

        assert len(result.data) == 1
        assert result.data[0].name == "Exp 1"
        assert result.data[0].project_id == project1.id

    def test_list_experiments_with_experiment_type_filter(self, db_session: Session) -> None:
        """List experiments filtered by experiment_type_id."""
        project = Project(name="Test Project", description="Description")
        exp_type1 = create_experiment_type(name="Classification")
        exp_type2 = create_experiment_type(name="Regression")
        db_session.add_all([project, exp_type1, exp_type2])
        db_session.commit()

        exp1 = Experiment(
            name="Exp 1",
            project_id=project.id,
            experiment_type_id=exp_type1.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Exp 2",
            project_id=project.id,
            experiment_type_id=exp_type2.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(
            pagination, sorting, search_params, experiment_type_id=exp_type1.id
        )

        assert len(result.data) == 1
        assert result.data[0].name == "Exp 1"
        assert result.data[0].experiment_type_id == exp_type1.id

    def test_list_experiments_with_both_filters(self, db_session: Session) -> None:
        """List experiments filtered by both project_id and experiment_type_id."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        exp_type1 = create_experiment_type(name="Classification")
        exp_type2 = create_experiment_type(name="Regression")
        db_session.add_all([project1, project2, exp_type1, exp_type2])
        db_session.commit()

        exp1 = Experiment(
            name="Exp 1",
            project_id=project1.id,
            experiment_type_id=exp_type1.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Exp 2",
            project_id=project1.id,
            experiment_type_id=exp_type2.id,
            description="Description",
        )
        exp3 = Experiment(
            name="Exp 3",
            project_id=project2.id,
            experiment_type_id=exp_type1.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2, exp3])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(
            pagination,
            sorting,
            search_params,
            project_id=project1.id,
            experiment_type_id=exp_type1.id,
        )

        assert len(result.data) == 1
        assert result.data[0].name == "Exp 1"
        assert result.data[0].project_id == project1.id
        assert result.data[0].experiment_type_id == exp_type1.id

    def test_list_experiments_with_sorting_by_name_asc(self, db_session: Session) -> None:
        """List experiments sorted by name ascending."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Zebra Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Alpha Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Alpha Experiment"
        assert result.data[1].name == "Zebra Experiment"

    def test_list_experiments_with_sorting_by_name_desc(self, db_session: Session) -> None:
        """List experiments sorted by name descending."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Alpha Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Zebra Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.DESC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Zebra Experiment"
        assert result.data[1].name == "Alpha Experiment"

    def test_list_experiments_with_sorting_by_id(self, db_session: Session) -> None:
        """List experiments sorted by id."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Experiment 1",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        exp2 = Experiment(
            name="Experiment 2",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add_all([exp1, exp2])
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="id", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].id < result.data[1].id

    def test_list_experiments_with_invalid_sort_field(self, db_session: Session) -> None:
        """Raise error when sorting by invalid field."""
        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="invalid_field", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        with pytest.raises(SortingValidationError) as exc_info:
            service.list_experiments(pagination, sorting, search_params)

        assert "Invalid sort field 'invalid_field'" in str(exc_info.value.message)

    def test_list_experiments_default_sort(self, db_session: Session) -> None:
        """List experiments with default sort (by created_at descending)."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        exp1 = Experiment(
            name="Experiment 1",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(exp1)
        db_session.commit()
        exp1_id = exp1.id

        exp2 = Experiment(
            name="Experiment 2",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(exp2)
        db_session.commit()
        exp2_id = exp2.id

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 2
        # Verify both experiments are returned
        result_ids = {exp.id for exp in result.data}
        assert result_ids == {exp1_id, exp2_id}
        # Verify sort is descending (most recent first) - created_at should be >= for first item
        assert result.data[0].created_at >= result.data[1].created_at

    def test_list_experiments_with_pagination(self, db_session: Session) -> None:
        """List experiments with pagination."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiments = [
            Experiment(
                name=f"Experiment {i}",
                project_id=project.id,
                experiment_type_id=experiment_type.id,
                description="Description",
            )
            for i in range(5)
        ]
        db_session.add_all(experiments)
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=2, limit=2)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_experiments(pagination, sorting, search_params)

        assert len(result.data) == 2


class TestUpdateExperiment:
    """Test update_experiment method."""

    def test_update_experiment_name(self, db_session: Session) -> None:
        """Update experiment name."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Old Name",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(name="New Name", description=None)

        result = service.update_experiment(experiment_id, experiment_update)

        assert result.name == "New Name"
        assert result.description == "Description"
        assert result.project_id == project.id

    def test_update_experiment_description(self, db_session: Session) -> None:
        """Update experiment description."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Experiment Name",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Old description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(name=None, description="New description")

        result = service.update_experiment(experiment_id, experiment_update)

        assert result.name == "Experiment Name"
        assert result.description == "New description"

    def test_update_experiment_both_fields(self, db_session: Session) -> None:
        """Update both experiment name and description."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Old Name",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Old description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(name="New Name", description="New description")

        result = service.update_experiment(experiment_id, experiment_update)

        assert result.name == "New Name"
        assert result.description == "New description"

    def test_update_experiment_project_id(self, db_session: Session) -> None:
        """Update experiment project_id."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project1, project2, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Experiment",
            project_id=project1.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(project_id=project2.id)

        result = service.update_experiment(experiment_id, experiment_update)

        assert result.project_id == project2.id
        assert result.name == "Experiment"

    def test_update_experiment_type_id(self, db_session: Session) -> None:
        """Update experiment experiment_type_id."""
        project = Project(name="Test Project", description="Description")
        exp_type1 = create_experiment_type(name="Classification")
        exp_type2 = create_experiment_type(name="Regression")
        db_session.add_all([project, exp_type1, exp_type2])
        db_session.commit()

        experiment = Experiment(
            name="Experiment",
            project_id=project.id,
            experiment_type_id=exp_type1.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(experiment_type_id=exp_type2.id)

        result = service.update_experiment(experiment_id, experiment_update)

        assert result.experiment_type_id == exp_type2.id
        assert result.name == "Experiment"

    def test_update_experiment_all_fields(self, db_session: Session) -> None:
        """Update all experiment fields."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        exp_type1 = create_experiment_type(name="Classification")
        exp_type2 = create_experiment_type(name="Regression")
        db_session.add_all([project1, project2, exp_type1, exp_type2])
        db_session.commit()

        experiment = Experiment(
            name="Old Name",
            project_id=project1.id,
            experiment_type_id=exp_type1.id,
            description="Old description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(
            name="New Name",
            project_id=project2.id,
            experiment_type_id=exp_type2.id,
            description="New description",
        )

        result = service.update_experiment(experiment_id, experiment_update)

        assert result.name == "New Name"
        assert result.project_id == project2.id
        assert result.experiment_type_id == exp_type2.id
        assert result.description == "New description"

    def test_update_experiment_not_found(self, db_session: Session) -> None:
        """Raise error when updating non-existent experiment."""
        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(name="New Name", description="New description")

        with pytest.raises(NotFoundError) as exc_info:
            service.update_experiment(999, experiment_update)

        assert "Experiment with ID 999 not found" in str(exc_info.value.message)

    def test_update_experiment_project_not_found(self, db_session: Session) -> None:
        """Raise error when updating to non-existent project."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(project_id=999)

        with pytest.raises(NotFoundError) as exc_info:
            service.update_experiment(experiment_id, experiment_update)

        assert "Project with ID 999 not found" in str(exc_info.value.message)

    def test_update_experiment_type_not_found(self, db_session: Session) -> None:
        """Raise error when updating to non-existent experiment type."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="Experiment",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        experiment_update = ExperimentUpdate(experiment_type_id=999)

        with pytest.raises(NotFoundError) as exc_info:
            service.update_experiment(experiment_id, experiment_update)

        assert "Experiment type with ID 999 not found" in str(exc_info.value.message)


class TestDeleteExperiment:
    """Test delete_experiment method."""

    def test_delete_experiment_success(self, db_session: Session) -> None:
        """Delete experiment successfully."""
        project = Project(name="Test Project", description="Description")
        experiment_type = create_experiment_type()
        db_session.add_all([project, experiment_type])
        db_session.commit()

        experiment = Experiment(
            name="To Delete",
            project_id=project.id,
            experiment_type_id=experiment_type.id,
            description="Description",
        )
        db_session.add(experiment)
        db_session.commit()
        experiment_id = experiment.id

        service = ExperimentService(db_session)
        service.delete_experiment(experiment_id)

        # Verify deleted
        deleted_experiment = (
            db_session.query(Experiment).filter(Experiment.id == experiment_id).first()
        )
        assert deleted_experiment is None

    def test_delete_experiment_not_found(self, db_session: Session) -> None:
        """Raise error when deleting non-existent experiment."""
        service = ExperimentService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.delete_experiment(999)

        assert "Experiment with ID 999 not found" in str(exc_info.value.message)


class TestAttachDatasetFile:
    """Test attach_dataset_file method."""

    def test_attach_dataset_file_with_path(self, db_session: Session, temp_csv_file: Path) -> None:
        """Attach dataset file to experiment by creating new dataset file."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        service = ExperimentService(db_session)
        dataset_data = ExperimentAttachDataset(path=str(temp_csv_file), dataset_file_id=None)

        result = service.attach_dataset_file(experiment.id, dataset_data)

        assert result.name == "test_data.csv"
        assert result.path == str(temp_csv_file)

        # Verify experiment was updated
        db_session.refresh(experiment)
        assert experiment.dataset_file_id == result.id
        assert experiment.status == ExperimentStatus.IN_PROGRESS.value

    def test_attach_dataset_file_with_existing_id(self, db_session: Session) -> None:
        """Attach existing dataset file to experiment by ID."""
        project = Project(name="Test Project")
        dataset_file = DatasetFile(name="existing.csv", path="/path/to/existing.csv")
        db_session.add_all([project, dataset_file])
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        service = ExperimentService(db_session)
        dataset_data = ExperimentAttachDataset(path=None, dataset_file_id=dataset_file.id)

        result = service.attach_dataset_file(experiment.id, dataset_data)

        assert result.id == dataset_file.id

        # Verify experiment was updated
        db_session.refresh(experiment)
        assert experiment.dataset_file_id == dataset_file.id
        assert experiment.status == ExperimentStatus.IN_PROGRESS.value

    def test_attach_dataset_file_experiment_not_found(
        self, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Raise error when experiment not found."""
        service = ExperimentService(db_session)
        dataset_data = ExperimentAttachDataset(path=str(temp_csv_file), dataset_file_id=None)

        with pytest.raises(NotFoundError) as exc_info:
            service.attach_dataset_file(999, dataset_data)

        assert "Experiment with ID 999 not found" in str(exc_info.value.message)

    def test_attach_dataset_file_dataset_not_found(self, db_session: Session) -> None:
        """Raise error when dataset file not found."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        service = ExperimentService(db_session)
        dataset_data = ExperimentAttachDataset(path=None, dataset_file_id=999)

        with pytest.raises(NotFoundError) as exc_info:
            service.attach_dataset_file(experiment.id, dataset_data)

        assert "Dataset file with ID 999 not found" in str(exc_info.value.message)

    def test_attach_dataset_file_path_none_bypass_validator(self, db_session: Session) -> None:
        """Test path None check when validator is bypassed."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        service = ExperimentService(db_session)
        # Create a mock that bypasses Pydantic validation
        dataset_data = Mock(spec=ExperimentAttachDataset)
        dataset_data.dataset_file_id = None
        dataset_data.path = None

        with pytest.raises(ValueError) as exc_info:
            service.attach_dataset_file(experiment.id, dataset_data)
        assert "Path must be provided" in str(exc_info.value)


class TestGetExperimentDatasetContent:
    """Test get_experiment_dataset_content method."""

    def test_get_experiment_dataset_content_success(
        self, db_session: Session, temp_csv_file: Path
    ) -> None:
        """Get experiment dataset content successfully."""
        _project, _dataset_file, experiment = create_project_with_dataset_and_experiment(
            db_session, dataset_file_name="test_data.csv", dataset_file_path=str(temp_csv_file)
        )

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        result = service.get_experiment_dataset_content(experiment.id, pagination)

        assert result.columns == ["id", "name", "value"]
        assert result.total_rows == 2
        assert len(result.rows) == 2

    def test_get_experiment_dataset_content_experiment_not_found(self, db_session: Session) -> None:
        """Raise error when experiment not found."""
        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_experiment_dataset_content(999, pagination)

        assert "Experiment with ID 999 not found" in str(exc_info.value.message)

    def test_get_experiment_dataset_content_no_dataset(self, db_session: Session) -> None:
        """Raise error when experiment has no associated dataset file."""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()
        experiment = Experiment(name="Test Experiment", project_id=project.id)
        db_session.add(experiment)
        db_session.commit()

        service = ExperimentService(db_session)
        pagination = PaginationParams(skip=0, limit=10)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_experiment_dataset_content(experiment.id, pagination)

        assert "has no associated dataset file" in str(exc_info.value.message)
