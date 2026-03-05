"""Project endpoints for API v1."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies.query_params import get_pagination, get_search, get_sorting
from app.api.schemas.common.params import PaginationParams, SearchParams, SortingParams
from app.api.schemas.common.responses import APIResponse, make_item_response, make_list_response
from app.api.schemas.v1.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.api.services.dependencies import get_project_service
from app.api.services.project_service import ProjectService

router = APIRouter()


@router.get(
    "",
    response_model=APIResponse[list[ProjectResponse]],
    responses={
        200: {"description": "List of projects retrieved successfully"},
        400: {"description": "Invalid sort field"},
    },
)
def list_projects(
    request: Request,
    service: Annotated[ProjectService, Depends(get_project_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    sorting: Annotated[SortingParams, Depends(get_sorting)],
    search_params: Annotated[SearchParams, Depends(get_search)],
) -> APIResponse[list[ProjectResponse]]:
    """List all projects with pagination, sorting, and search."""
    result = service.list_projects(pagination, sorting, search_params)
    return make_list_response(
        data=result.data,
        total=result.total,
        pagination=pagination,
        sorting=sorting,
        search=search_params,
        dev_code="PROJECTS_LISTED",
        message="Projects retrieved successfully",
        request_id=getattr(request.state, "request_id", "unknown"),
    )


@router.post(
    "",
    response_model=APIResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Project created successfully"},
        409: {"description": "Project with this name already exists"},
    },
)
def create_project(
    request: Request,
    project: ProjectCreate,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> APIResponse[ProjectResponse]:
    """Create a new project."""
    created = service.create_project(project)
    return make_item_response(
        data=created,
        dev_code="PROJECT_CREATED",
        message="Project created successfully",
        request_id=getattr(request.state, "request_id", "unknown"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/{project_id}",
    response_model=APIResponse[ProjectResponse],
    responses={
        200: {"description": "Project retrieved successfully"},
        404: {"description": "Project not found"},
    },
)
def get_project(
    request: Request,
    project_id: int,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> APIResponse[ProjectResponse]:
    """Get a project by ID."""
    project = service.get_project(project_id)
    return make_item_response(
        data=project,
        dev_code="PROJECT_RETRIEVED",
        message="Project retrieved successfully",
        request_id=getattr(request.state, "request_id", "unknown"),
    )


@router.patch(
    "/{project_id}",
    response_model=APIResponse[ProjectResponse],
    responses={
        200: {"description": "Project updated successfully"},
        404: {"description": "Project not found"},
        409: {"description": "Project name conflict"},
    },
)
def update_project(
    request: Request,
    project_id: int,
    project_update: ProjectUpdate,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> APIResponse[ProjectResponse]:
    """Update a project."""
    updated = service.update_project(project_id, project_update)
    return make_item_response(
        data=updated,
        dev_code="PROJECT_UPDATED",
        message="Project updated successfully",
        request_id=getattr(request.state, "request_id", "unknown"),
    )


@router.delete(
    "/{project_id}",
    response_model=APIResponse[None],
    responses={
        200: {"description": "Project deleted successfully"},
        404: {"description": "Project not found"},
    },
)
def delete_project(
    request: Request,
    project_id: int,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> APIResponse[None]:
    """Delete a project."""
    service.delete_project(project_id)
    return make_item_response(
        data=None,
        dev_code="PROJECT_DELETED",
        message="Project deleted successfully",
        request_id=getattr(request.state, "request_id", "unknown"),
    )
