"""Project service for business logic."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.api.services.utils import apply_sorting, build_list_response
from app.db.models.project import Project


class ProjectService:
    """Service for project business logic."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session."""
        self.db = db

    def list_projects(
        self,
        pagination: PaginationParams,
        sorting: SortingParams,
        search_params: SearchParams,
    ) -> ListResponse[ProjectResponse]:
        """List all projects with pagination, sorting, and search."""
        query = self.db.query(Project)

        if search_params.search:
            search_filter = or_(
                Project.name.ilike(f"%{search_params.search}%"),
                Project.description.ilike(f"%{search_params.search}%"),
            )
            query = query.filter(search_filter)

        if sorting.sort_by:
            if sorting.sort_by not in Project.valid_sort_fields:
                raise SortingValidationError(
                    f"Invalid sort field '{sorting.sort_by}'. "
                    f"Valid fields are: {', '.join(sorted(Project.valid_sort_fields))}"
                )
            sort_column = getattr(Project, sorting.sort_by)
            query = apply_sorting(query, sort_column, sorting.sort_direction)
        else:
            query = query.order_by(Project.created_at.desc())

        projects = query.offset(pagination.skip).limit(pagination.limit).all()

        data = [self._build_project_response(project) for project in projects]

        return build_list_response(pagination, sorting, search_params, data)

    def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        """Create a new project."""
        existing_project = self.db.query(Project).filter(Project.name == project_data.name).first()
        if existing_project:
            raise ConflictError(f"Project with name '{project_data.name}' already exists")

        db_project = Project(name=project_data.name, description=project_data.description)
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)

        return self._build_project_response(db_project)

    def get_project(self, project_id: int) -> ProjectResponse:
        """Get a project by ID."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError(f"Project with ID {project_id} not found")

        return self._build_project_response(project)

    def update_project(self, project_id: int, project_update: ProjectUpdate) -> ProjectResponse:
        """Update a project."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError(f"Project with ID {project_id} not found")

        if project_update.name and project_update.name != project.name:
            existing_project = (
                self.db.query(Project).filter(Project.name == project_update.name).first()
            )
            if existing_project:
                raise ConflictError(f"Project with name '{project_update.name}' already exists")

        if project_update.name is not None:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description

        self.db.commit()
        self.db.refresh(project)

        return self._build_project_response(project)

    def delete_project(self, project_id: int) -> None:
        """Delete a project."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError(f"Project with ID {project_id} not found")

        self.db.delete(project)
        self.db.commit()

    def _build_project_response(self, project: Project) -> ProjectResponse:
        """Build a ProjectResponse from a Project model."""
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
