"""Projects endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DatabaseError, IntegrityError

from app.api.dependencies.query_params import get_pagination, get_search, get_sorting
from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.api.services.dependencies import get_project_service
from app.api.services.project_service import ProjectService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["projects"])

MSG_DATABASE_ERROR = "Database error occurred while"
MSG_UNEXPECTED_ERROR = "An unexpected error occurred while"
MSG_DATABASE_ERROR_LISTING = f"{MSG_DATABASE_ERROR} listing projects"
MSG_UNEXPECTED_ERROR_LISTING = f"{MSG_UNEXPECTED_ERROR} listing projects"
MSG_DATABASE_ERROR_CREATING = f"{MSG_DATABASE_ERROR} creating project"
MSG_UNEXPECTED_ERROR_CREATING = f"{MSG_UNEXPECTED_ERROR} creating project"
MSG_DATABASE_ERROR_GETTING = f"{MSG_DATABASE_ERROR} retrieving project"
MSG_UNEXPECTED_ERROR_GETTING = f"{MSG_UNEXPECTED_ERROR} retrieving project"
MSG_DATABASE_ERROR_UPDATING = f"{MSG_DATABASE_ERROR} updating project"
MSG_UNEXPECTED_ERROR_UPDATING = f"{MSG_UNEXPECTED_ERROR} updating project"
MSG_DATABASE_ERROR_DELETING = f"{MSG_DATABASE_ERROR} deleting project"
MSG_UNEXPECTED_ERROR_DELETING = f"{MSG_UNEXPECTED_ERROR} deleting project"
MSG_CONSTRAINT_VIOLATION = "Database constraint violation occurred"


@router.get(
    "",
    response_model=ListResponse[ProjectResponse],
    responses={
        200: {"description": "List of projects retrieved successfully"},
        400: {"description": "Invalid sort field provided"},
        500: {"description": MSG_DATABASE_ERROR_LISTING},
    },
)
def list_projects(
    service: Annotated[ProjectService, Depends(get_project_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    sorting: Annotated[SortingParams, Depends(get_sorting)],
    search_params: Annotated[SearchParams, Depends(get_search)],
) -> ListResponse[ProjectResponse]:
    """List all projects with pagination, sorting, and search."""
    try:
        return service.list_projects(pagination, sorting, search_params)
    except SortingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error listing projects: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_LISTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error listing projects: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_LISTING,
        ) from exc
    # pylint: enable=duplicate-code


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Project created successfully"},
        409: {"description": "Project with this name already exists"},
        500: {"description": MSG_DATABASE_ERROR_CREATING},
    },
)
def create_project(
    project: ProjectCreate, service: Annotated[ProjectService, Depends(get_project_service)]
) -> ProjectResponse:
    """Create a new project."""
    try:
        return service.create_project(project)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except IntegrityError as exc:
        logger.error("Database integrity error creating project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=MSG_DATABASE_ERROR_CREATING,
        ) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error creating project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_CREATING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error creating project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_CREATING,
        ) from exc
    # pylint: enable=duplicate-code


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={
        200: {"description": "Project retrieved successfully"},
        404: {"description": "Project not found"},
        500: {"description": MSG_DATABASE_ERROR_GETTING},
    },
)
def get_project(
    project_id: int, service: Annotated[ProjectService, Depends(get_project_service)]
) -> ProjectResponse:
    """Get a project by ID."""
    try:
        return service.get_project(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error getting project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_GETTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error getting project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_GETTING,
        ) from exc
    # pylint: enable=duplicate-code


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={
        200: {"description": "Project updated successfully"},
        404: {"description": "Project not found"},
        409: {"description": MSG_CONSTRAINT_VIOLATION},
        500: {"description": MSG_DATABASE_ERROR_UPDATING},
    },
)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    """Update a project."""
    try:
        return service.update_project(project_id, project_update)
    # pylint: disable=duplicate-code
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except IntegrityError as exc:
        logger.error("Database integrity error updating project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=MSG_DATABASE_ERROR_UPDATING,
        ) from exc
    except DatabaseError as exc:
        logger.error("Database error updating project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_UPDATING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error updating project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_UPDATING,
        ) from exc
    # pylint: enable=duplicate-code


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Project deleted successfully"},
        404: {"description": "Project not found"},
        500: {"description": MSG_DATABASE_ERROR_DELETING},
    },
)
def delete_project(
    project_id: int, service: Annotated[ProjectService, Depends(get_project_service)]
) -> None:
    """Delete a project."""
    try:
        service.delete_project(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except DatabaseError as exc:
        logger.error("Database error deleting project: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_DELETING,
        ) from exc
