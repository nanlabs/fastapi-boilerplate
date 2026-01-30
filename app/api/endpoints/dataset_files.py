"""Dataset files endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DatabaseError, IntegrityError

from app.api.dependencies.query_params import get_pagination, get_search, get_sorting
from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError, ValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.dataset_file import (
    DatasetFileContentResponse,
    DatasetFileCreate,
    DatasetFileResponse,
    DatasetFileUpdate,
)
from app.api.services.dataset_file_service import DatasetFileService
from app.api.services.dependencies import get_dataset_file_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dataset-files"])

MSG_DATABASE_ERROR = "Database error occurred while"
MSG_UNEXPECTED_ERROR = "An unexpected error occurred while"
MSG_DATABASE_ERROR_LISTING = f"{MSG_DATABASE_ERROR} listing dataset files"
MSG_UNEXPECTED_ERROR_LISTING = f"{MSG_UNEXPECTED_ERROR} listing dataset files"
MSG_DATABASE_ERROR_CREATING = f"{MSG_DATABASE_ERROR} creating dataset file"
MSG_UNEXPECTED_ERROR_CREATING = f"{MSG_UNEXPECTED_ERROR} creating dataset file"
MSG_DATABASE_ERROR_GETTING = f"{MSG_DATABASE_ERROR} retrieving dataset file"
MSG_UNEXPECTED_ERROR_GETTING = f"{MSG_UNEXPECTED_ERROR} retrieving dataset file"
MSG_DATABASE_ERROR_UPDATING = f"{MSG_DATABASE_ERROR} updating dataset file"
MSG_UNEXPECTED_ERROR_UPDATING = f"{MSG_UNEXPECTED_ERROR} updating dataset file"
MSG_DATABASE_ERROR_DELETING = f"{MSG_DATABASE_ERROR} deleting dataset file"
MSG_UNEXPECTED_ERROR_DELETING = f"{MSG_UNEXPECTED_ERROR} deleting dataset file"
MSG_DATABASE_ERROR_GETTING_CONTENT = f"{MSG_DATABASE_ERROR} retrieving dataset file content"
MSG_UNEXPECTED_ERROR_GETTING_CONTENT = f"{MSG_UNEXPECTED_ERROR} retrieving dataset file content"
MSG_CONSTRAINT_VIOLATION = "Database constraint violation occurred"


@router.get(
    "",
    response_model=ListResponse[DatasetFileResponse],
    responses={
        200: {"description": "List of dataset files retrieved successfully"},
        400: {"description": "Invalid sort field provided"},
        500: {"description": MSG_DATABASE_ERROR_LISTING},
    },
)
def list_dataset_files(
    service: Annotated[DatasetFileService, Depends(get_dataset_file_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    sorting: Annotated[SortingParams, Depends(get_sorting)],
    search_params: Annotated[SearchParams, Depends(get_search)],
) -> ListResponse[DatasetFileResponse]:
    """List all dataset files with pagination, sorting, and search."""
    try:
        return service.list_dataset_files(pagination, sorting, search_params)
    except SortingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error listing dataset files: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_LISTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error listing dataset files: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_LISTING,
        ) from exc
    # pylint: enable=duplicate-code


@router.post(
    "",
    response_model=DatasetFileResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Dataset file created successfully"},
        400: {"description": "File not found or path is not a file"},
        409: {"description": "Dataset file with this path already exists"},
        500: {"description": MSG_DATABASE_ERROR_CREATING},
    },
)
def create_dataset_file(
    dataset_file: DatasetFileCreate,
    service: Annotated[DatasetFileService, Depends(get_dataset_file_service)],
) -> DatasetFileResponse:
    """Create a new dataset file."""
    try:
        return service.create_dataset_file(dataset_file)
    # pylint: disable=duplicate-code
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except IntegrityError as exc:
        logger.error("Database integrity error creating dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=MSG_DATABASE_ERROR_CREATING,
        ) from exc
    except DatabaseError as exc:
        logger.error("Database error creating dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_CREATING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error creating dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_CREATING,
        ) from exc
    # pylint: enable=duplicate-code


@router.get(
    "/{dataset_file_id}",
    response_model=DatasetFileResponse,
    responses={
        200: {"description": "Dataset file retrieved successfully"},
        404: {"description": "Dataset file not found"},
        500: {"description": MSG_DATABASE_ERROR_GETTING},
    },
)
def get_dataset_file(
    dataset_file_id: int,
    service: Annotated[DatasetFileService, Depends(get_dataset_file_service)],
) -> DatasetFileResponse:
    """Get a dataset file by ID."""
    try:
        return service.get_dataset_file(dataset_file_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error getting dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_GETTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error getting dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_GETTING,
        ) from exc
    # pylint: enable=duplicate-code


@router.patch(
    "/{dataset_file_id}",
    response_model=DatasetFileResponse,
    responses={
        200: {"description": "Dataset file updated successfully"},
        404: {"description": "Dataset file not found"},
        409: {"description": MSG_CONSTRAINT_VIOLATION},
        500: {"description": MSG_DATABASE_ERROR_UPDATING},
    },
)
def update_dataset_file(
    dataset_file_id: int,
    dataset_file_update: DatasetFileUpdate,
    service: Annotated[DatasetFileService, Depends(get_dataset_file_service)],
) -> DatasetFileResponse:
    """Update a dataset file."""
    try:
        return service.update_dataset_file(dataset_file_id, dataset_file_update)
    # pylint: disable=duplicate-code
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except IntegrityError as exc:
        logger.error("Database integrity error updating dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=MSG_DATABASE_ERROR_UPDATING,
        ) from exc
    except DatabaseError as exc:
        logger.error("Database error updating dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_UPDATING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error updating dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_UPDATING,
        ) from exc
    # pylint: enable=duplicate-code


@router.delete(
    "/{dataset_file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Dataset file deleted successfully"},
        404: {"description": "Dataset file not found"},
        409: {"description": "Dataset file is associated with an experiment and cannot be deleted"},
        500: {"description": MSG_DATABASE_ERROR_DELETING},
    },
)
def delete_dataset_file(
    dataset_file_id: int,
    service: Annotated[DatasetFileService, Depends(get_dataset_file_service)],
) -> None:
    """Delete a dataset file."""
    try:
        service.delete_dataset_file(dataset_file_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error deleting dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_DELETING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error deleting dataset file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_DELETING,
        ) from exc
    # pylint: enable=duplicate-code


@router.get(
    "/{dataset_file_id}/content",
    response_model=DatasetFileContentResponse,
    responses={
        200: {"description": "Dataset file content retrieved successfully"},
        404: {"description": "Dataset file not found or CSV file not found"},
        400: {"description": "Error parsing CSV file"},
        500: {"description": MSG_DATABASE_ERROR_GETTING_CONTENT},
    },
)
def get_dataset_file_content(
    dataset_file_id: int,
    service: Annotated[DatasetFileService, Depends(get_dataset_file_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
) -> DatasetFileContentResponse:
    """Get paginated content from a dataset file CSV."""
    try:
        return service.get_dataset_file_content(dataset_file_id, pagination)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error getting dataset file content: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_GETTING_CONTENT,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error getting dataset file content: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_GETTING_CONTENT,
        ) from exc
    # pylint: enable=duplicate-code
