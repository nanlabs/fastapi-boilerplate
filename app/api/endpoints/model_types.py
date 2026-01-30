"""Model types endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DatabaseError

from app.api.dependencies.query_params import get_pagination, get_search, get_sorting
from app.api.exceptions import NotFoundError, SortingValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.model_type import ModelTypeResponse
from app.api.services.dependencies import get_model_type_service
from app.api.services.model_type_service import ModelTypeService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["model-types"])

# Error messages
MSG_DATABASE_ERROR_LISTING = "Database error occurred while listing model types"
MSG_UNEXPECTED_ERROR_LISTING = "An unexpected error occurred while listing model types"
MSG_UNEXPECTED_ERROR_GETTING = "An unexpected error occurred while retrieving model type"
MSG_DATABASE_ERROR_GETTING = "Database error occurred while retrieving model type"


@router.get(
    "",
    response_model=ListResponse[ModelTypeResponse],
    responses={
        200: {"description": "List of model types retrieved successfully"},
        400: {"description": "Invalid sort field provided"},
        500: {"description": MSG_DATABASE_ERROR_LISTING},
    },
)
def list_model_types(
    service: Annotated[ModelTypeService, Depends(get_model_type_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    sorting: Annotated[SortingParams, Depends(get_sorting)],
    search_params: Annotated[SearchParams, Depends(get_search)],
) -> ListResponse[ModelTypeResponse]:
    """List all model types with pagination, sorting, and search."""
    try:
        return service.list_model_types(pagination, sorting, search_params)
    except SortingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error listing model types: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_LISTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error listing model types: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_LISTING,
        ) from exc
    # pylint: enable=duplicate-code


@router.get(
    "/{model_type_id}",
    response_model=ModelTypeResponse,
    responses={
        200: {"description": "Model type retrieved successfully"},
        404: {"description": "Model type not found"},
        500: {"description": MSG_DATABASE_ERROR_GETTING},
    },
)
def get_model_type(
    model_type_id: int,
    service: Annotated[ModelTypeService, Depends(get_model_type_service)],
) -> ModelTypeResponse:
    """Get a model type by ID."""
    try:
        return service.get_model_type(model_type_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error getting model type: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_GETTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error getting model type: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_GETTING,
        ) from exc
    # pylint: enable=duplicate-code
