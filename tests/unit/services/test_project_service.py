"""Unit tests for app.api.services.project_service."""

import pytest
from sqlalchemy.orm import Session

from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError
from app.api.schemas.api import PaginationParams, SearchParams, SortDirection, SortingParams
from app.api.schemas.project import ProjectCreate, ProjectUpdate
from app.api.services.project_service import ProjectService
from app.db.models.experiment import Experiment
from app.db.models.project import Project


@pytest.fixture(autouse=True)
def _cleanup_projects(db_session: Session) -> None:
    """Clean up projects and experiments before each test."""
    db_session.query(Experiment).delete()
    db_session.query(Project).delete()
    db_session.commit()


class TestProjectServiceInit:
    """Test ProjectService initialization."""

    def test_init(self, db_session: Session) -> None:
        """Initialize service with database session."""
        service = ProjectService(db_session)
        assert service.db == db_session


class TestListProjects:
    """Test list_projects method."""

    def test_list_projects_empty(self, db_session: Session) -> None:
        """List projects when database is empty."""
        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_projects(pagination, sorting, search_params)

        assert result.data == []
        assert result.pagination == pagination
        assert result.sort == sorting
        assert result.search == search_params

    def test_list_projects_with_data(self, db_session: Session) -> None:
        """List projects with existing data."""
        project1 = Project(name="Project 1", description="Description 1")
        project2 = Project(name="Project 2", description="Description 2")
        db_session.add_all([project1, project2])
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name in ["Project 1", "Project 2"]
        assert result.data[1].name in ["Project 1", "Project 2"]

    def test_list_projects_with_search(self, db_session: Session) -> None:
        """List projects with search filter."""
        project1 = Project(name="Analytics", description="Analytics project")
        project2 = Project(name="Data Analysis", description="Analysis project")
        project3 = Project(name="Web App", description="Web application")
        db_session.add_all([project1, project2, project3])
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="Machine")

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Analytics"

    def test_list_projects_with_search_in_description(self, db_session: Session) -> None:
        """List projects with search matching description."""
        project1 = Project(name="Search Test A", description="Analytics project")
        project2 = Project(name="Search Test B", description="Data analysis")
        db_session.add_all([project1, project2])
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="Learning")

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 1
        assert result.data[0].name == "Search Test A"

    def test_list_projects_with_sorting_by_name_asc(self, db_session: Session) -> None:
        """List projects sorted by name ascending."""
        project1 = Project(name="Zebra Project", description="Description")
        project2 = Project(name="Alpha Project", description="Description")
        db_session.add_all([project1, project2])
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Alpha Project"
        assert result.data[1].name == "Zebra Project"

    def test_list_projects_with_sorting_by_name_desc(self, db_session: Session) -> None:
        """List projects sorted by name descending."""
        project1 = Project(name="Alpha Project", description="Description")
        project2 = Project(name="Zebra Project", description="Description")
        db_session.add_all([project1, project2])
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.DESC)
        search_params = SearchParams(search=None)

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].name == "Zebra Project"
        assert result.data[1].name == "Alpha Project"

    def test_list_projects_with_sorting_by_id(self, db_session: Session) -> None:
        """List projects sorted by id."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        db_session.add_all([project1, project2])
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="id", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 2
        assert result.data[0].id < result.data[1].id

    def test_list_projects_with_invalid_sort_field(self, db_session: Session) -> None:
        """Raise error when sorting by invalid field."""
        service = ProjectService(db_session)
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="invalid_field", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        with pytest.raises(SortingValidationError) as exc_info:
            service.list_projects(pagination, sorting, search_params)

        assert "Invalid sort field 'invalid_field'" in str(exc_info.value.message)

    def test_list_projects_with_pagination(self, db_session: Session) -> None:
        """List projects with pagination."""
        projects = [Project(name=f"Project {i}", description="Description") for i in range(5)]
        db_session.add_all(projects)
        db_session.commit()

        service = ProjectService(db_session)
        pagination = PaginationParams(skip=2, limit=2)
        sorting = SortingParams(sort_by=None, sort_direction=SortDirection.ASC)
        search_params = SearchParams(search=None)

        result = service.list_projects(pagination, sorting, search_params)

        assert len(result.data) == 2


class TestCreateProject:
    """Test create_project method."""

    def test_create_project_success(self, db_session: Session) -> None:
        """Create project successfully."""
        service = ProjectService(db_session)
        project_data = ProjectCreate(name="New Project", description="New description")

        result = service.create_project(project_data)

        assert result.name == "New Project"
        assert result.description == "New description"
        assert result.id is not None
        assert result.experiments_count == 0

        # Verify in database
        db_project = db_session.query(Project).filter(Project.id == result.id).first()
        assert db_project is not None
        assert db_project.name == "New Project"

    def test_create_project_without_description(self, db_session: Session) -> None:
        """Create project without description."""
        service = ProjectService(db_session)
        project_data = ProjectCreate(name="New Project", description=None)

        result = service.create_project(project_data)

        assert result.name == "New Project"
        assert result.description is None

    def test_create_project_conflict(self, db_session: Session) -> None:
        """Raise error when creating project with duplicate name."""
        existing_project = Project(name="Existing Project", description="Description")
        db_session.add(existing_project)
        db_session.commit()

        service = ProjectService(db_session)
        project_data = ProjectCreate(name="Existing Project", description="New description")

        with pytest.raises(ConflictError) as exc_info:
            service.create_project(project_data)

        assert "Project with name 'Existing Project' already exists" in str(exc_info.value.message)


class TestGetProject:
    """Test get_project method."""

    def test_get_project_success(self, db_session: Session) -> None:
        """Get project by ID successfully."""
        project = Project(name="Test Project", description="Test description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        service = ProjectService(db_session)
        result = service.get_project(project_id)

        assert result.id == project_id
        assert result.name == "Test Project"
        assert result.description == "Test description"

    def test_get_project_not_found(self, db_session: Session) -> None:
        """Raise error when project not found."""
        service = ProjectService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_project(999)

        assert "Project with ID 999 not found" in str(exc_info.value.message)


class TestUpdateProject:
    """Test update_project method."""

    def test_update_project_name(self, db_session: Session) -> None:
        """Update project name."""
        project = Project(name="Old Name", description="Description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        service = ProjectService(db_session)
        project_update = ProjectUpdate(name="New Name", description=None)

        result = service.update_project(project_id, project_update)

        assert result.name == "New Name"
        assert result.description == "Description"

    def test_update_project_description(self, db_session: Session) -> None:
        """Update project description."""
        project = Project(name="Project Name", description="Old description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        service = ProjectService(db_session)
        project_update = ProjectUpdate(name=None, description="New description")

        result = service.update_project(project_id, project_update)

        assert result.name == "Project Name"
        assert result.description == "New description"

    def test_update_project_both_fields(self, db_session: Session) -> None:
        """Update both project name and description."""
        project = Project(name="Old Name", description="Old description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        service = ProjectService(db_session)
        project_update = ProjectUpdate(name="New Name", description="New description")

        result = service.update_project(project_id, project_update)

        assert result.name == "New Name"
        assert result.description == "New description"

    def test_update_project_same_name(self, db_session: Session) -> None:
        """Update project with same name should succeed."""
        project = Project(name="Project Name", description="Description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        service = ProjectService(db_session)
        project_update = ProjectUpdate(name="Project Name", description="New description")

        result = service.update_project(project_id, project_update)

        assert result.name == "Project Name"
        assert result.description == "New description"

    def test_update_project_not_found(self, db_session: Session) -> None:
        """Raise error when updating non-existent project."""
        service = ProjectService(db_session)
        project_update = ProjectUpdate(name="New Name", description="New description")

        with pytest.raises(NotFoundError) as exc_info:
            service.update_project(999, project_update)

        assert "Project with ID 999 not found" in str(exc_info.value.message)

    def test_update_project_name_conflict(self, db_session: Session) -> None:
        """Raise error when updating to duplicate name."""
        project1 = Project(name="Project 1", description="Description")
        project2 = Project(name="Project 2", description="Description")
        db_session.add_all([project1, project2])
        db_session.commit()
        project_id = project1.id

        service = ProjectService(db_session)
        project_update = ProjectUpdate(name="Project 2", description=None)

        with pytest.raises(ConflictError) as exc_info:
            service.update_project(project_id, project_update)

        assert "Project with name 'Project 2' already exists" in str(exc_info.value.message)


class TestDeleteProject:
    """Test delete_project method."""

    def test_delete_project_success(self, db_session: Session) -> None:
        """Delete project successfully."""
        project = Project(name="To Delete", description="Description")
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        service = ProjectService(db_session)
        service.delete_project(project_id)

        # Verify deleted
        deleted_project = db_session.query(Project).filter(Project.id == project_id).first()
        assert deleted_project is None

    def test_delete_project_not_found(self, db_session: Session) -> None:
        """Raise error when deleting non-existent project."""
        service = ProjectService(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            service.delete_project(999)

        assert "Project with ID 999 not found" in str(exc_info.value.message)
