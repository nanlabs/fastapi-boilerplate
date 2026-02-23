"""Experiments endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DatabaseError, IntegrityError

from app.api.dependencies.query_params import get_pagination, get_search, get_sorting
from app.api.exceptions import NotFoundError, SortingValidationError, ValidationError
from app.api.schemas.api import ListResponse, PaginationParams, SearchParams, SortingParams
from app.api.schemas.dataset_file import DatasetFileContentResponse, DatasetFileResponse
from app.api.schemas.experiment import (
    ExperimentAttachDataset,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentStatusesResponse,
    ExperimentUpdate,
)
from app.api.services.dependencies import get_experiment_service
from app.api.services.experiment_service import ExperimentService
from app.schemas.common.base import ExperimentStatus

logger = logging.getLogger(__name__)
router = APIRouter(tags=["experiments"])

# Error messages
MSG_DATABASE_ERROR = "Database error occurred while"
MSG_UNEXPECTED_ERROR = "An unexpected error occurred while"
MSG_DATABASE_ERROR_LISTING = f"{MSG_DATABASE_ERROR} listing experiments"
MSG_UNEXPECTED_ERROR_LISTING = f"{MSG_UNEXPECTED_ERROR} listing experiments"
MSG_DATABASE_ERROR_CREATING = f"{MSG_DATABASE_ERROR} creating experiment"
MSG_UNEXPECTED_ERROR_CREATING = f"{MSG_UNEXPECTED_ERROR} creating experiment"
MSG_DATABASE_ERROR_GETTING = f"{MSG_DATABASE_ERROR} retrieving experiment"
MSG_UNEXPECTED_ERROR_GETTING = f"{MSG_UNEXPECTED_ERROR} retrieving experiment"
MSG_DATABASE_ERROR_UPDATING = f"{MSG_DATABASE_ERROR} updating experiment"
MSG_UNEXPECTED_ERROR_UPDATING = f"{MSG_UNEXPECTED_ERROR} updating experiment"
MSG_DATABASE_ERROR_DELETING = f"{MSG_DATABASE_ERROR} deleting experiment"
MSG_UNEXPECTED_ERROR_DELETING = f"{MSG_UNEXPECTED_ERROR} deleting experiment"
MSG_DATABASE_ERROR_ATTACHING_DATASET = f"{MSG_DATABASE_ERROR} attaching dataset file to experiment"
MSG_UNEXPECTED_ERROR_ATTACHING_DATASET = (
    f"{MSG_UNEXPECTED_ERROR} attaching dataset file to experiment"
)
MSG_DATABASE_ERROR_GETTING_DATASET_CONTENT = (
    f"{MSG_DATABASE_ERROR} retrieving experiment dataset content"
)
MSG_UNEXPECTED_ERROR_GETTING_DATASET_CONTENT = (
    f"{MSG_UNEXPECTED_ERROR} retrieving experiment dataset content"
)
MSG_CONSTRAINT_VIOLATION = "Database constraint violation occurred"


@router.get(
    "/statuses",
    response_model=ExperimentStatusesResponse,
    responses={
        200: {"description": "List of experiment statuses retrieved successfully"},
    },
)
def get_experiment_statuses() -> ExperimentStatusesResponse:
    """Get all available experiment status values."""
    return ExperimentStatusesResponse(data=list(ExperimentStatus))


@router.get(
    "",
    response_model=ListResponse[ExperimentResponse],
    responses={
        200: {"description": "List of experiments retrieved successfully"},
        400: {"description": "Invalid sort field provided"},
        500: {"description": MSG_DATABASE_ERROR_LISTING},
    },
)
def list_experiments(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    service: Annotated[ExperimentService, Depends(get_experiment_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    sorting: Annotated[SortingParams, Depends(get_sorting)],
    search_params: Annotated[SearchParams, Depends(get_search)],
    project_id: int,
    experiment_type_id: int | None = None,
) -> ListResponse[ExperimentResponse]:
    """List experiments for a project with optional filters, pagination, sorting, and search."""
    try:
        return service.list_experiments(pagination, sorting, search_params, project_id)
    except SortingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error listing experiments: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_LISTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error listing experiments: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_LISTING,
        ) from exc
    # pylint: enable=duplicate-code


@router.post(
    "",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Experiment created successfully"},
        404: {"description": "Project or experiment type not found"},
        409: {"description": MSG_CONSTRAINT_VIOLATION},
        500: {"description": MSG_DATABASE_ERROR_CREATING},
    },
)
def create_experiment(
    experiment: ExperimentCreate,
    service: Annotated[ExperimentService, Depends(get_experiment_service)],
) -> ExperimentResponse:
    """Create a new experiment."""
    try:
        return service.create_experiment(experiment)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except IntegrityError as exc:
        logger.error("Database integrity error creating experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{MSG_CONSTRAINT_VIOLATION} while creating experiment",
        ) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error creating experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_CREATING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error creating experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_CREATING,
        ) from exc
    # pylint: enable=duplicate-code


@router.get(
    "/{experiment_id}",
    response_model=ExperimentResponse,
    responses={
        200: {"description": "Experiment retrieved successfully"},
        404: {"description": "Experiment not found"},
        500: {"description": MSG_DATABASE_ERROR_GETTING},
    },
)
def get_experiment(
    experiment_id: int, service: Annotated[ExperimentService, Depends(get_experiment_service)]
) -> ExperimentResponse:
    """Get an experiment by ID."""
    try:
        return service.get_experiment(experiment_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except DatabaseError as exc:
        logger.error("Database error getting experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_GETTING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error getting experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_GETTING,
        ) from exc


@router.patch(
    "/{experiment_id}",
    response_model=ExperimentResponse,
    responses={
        200: {"description": "Experiment updated successfully"},
        404: {"description": "Experiment not found"},
        409: {"description": MSG_CONSTRAINT_VIOLATION},
        500: {"description": MSG_DATABASE_ERROR_UPDATING},
    },
)
def update_experiment(
    experiment_id: int,
    experiment_update: ExperimentUpdate,
    service: Annotated[ExperimentService, Depends(get_experiment_service)],
) -> ExperimentResponse:
    """Update an experiment."""
    try:
        return service.update_experiment(experiment_id, experiment_update)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except IntegrityError as exc:
        logger.error("Database integrity error updating experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{MSG_CONSTRAINT_VIOLATION} while updating experiment",
        ) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error updating experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_UPDATING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error updating experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_UPDATING,
        ) from exc
    # pylint: enable=duplicate-code


@router.delete(
    "/{experiment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Experiment deleted successfully"},
        404: {"description": "Experiment not found"},
        500: {"description": MSG_DATABASE_ERROR_DELETING},
    },
)
def delete_experiment(
    experiment_id: int, service: Annotated[ExperimentService, Depends(get_experiment_service)]
) -> None:
    """Delete an experiment."""
    try:
        service.delete_experiment(experiment_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except DatabaseError as exc:
        logger.error("Database error deleting experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_DELETING,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error deleting experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_DELETING,
        ) from exc


@router.post(
    "/{experiment_id}/dataset",
    response_model=DatasetFileResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Dataset file attached to experiment successfully"},
        400: {
            "description": (
                "File not found, path is not a file, or invalid request "
                "(must provide path or dataset_file_id)"
            )
        },
        404: {"description": "Experiment not found or dataset file not found"},
        409: {"description": "Dataset file with this path already exists"},
        500: {"description": MSG_DATABASE_ERROR_ATTACHING_DATASET},
    },
)
def attach_dataset_to_experiment(
    experiment_id: int,
    dataset_data: ExperimentAttachDataset,
    service: Annotated[ExperimentService, Depends(get_experiment_service)],
) -> DatasetFileResponse:
    """Attach a dataset file to an experiment.

    Either provide a path to create a new dataset file, or provide
    an existing dataset_file_id to reuse an existing dataset file.
    """
    try:
        return service.attach_dataset_file(experiment_id, dataset_data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error attaching dataset to experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_ATTACHING_DATASET,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error attaching dataset to experiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_ATTACHING_DATASET,
        ) from exc
    # pylint: enable=duplicate-code


@router.get(
    "/{experiment_id}/dataset/content",
    response_model=DatasetFileContentResponse,
    responses={
        200: {"description": "Experiment dataset content retrieved successfully"},
        404: {"description": "Experiment not found or has no associated dataset file"},
        400: {"description": "Error parsing CSV file"},
        500: {"description": MSG_DATABASE_ERROR_GETTING_DATASET_CONTENT},
    },
)
def get_experiment_dataset_content(
    experiment_id: int,
    service: Annotated[ExperimentService, Depends(get_experiment_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
) -> DatasetFileContentResponse:
    """Get paginated content from the dataset file associated with an experiment."""
    try:
        return service.get_experiment_dataset_content(experiment_id, pagination)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    # pylint: disable=duplicate-code
    except DatabaseError as exc:
        logger.error("Database error getting experiment dataset content: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_DATABASE_ERROR_GETTING_DATASET_CONTENT,
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error getting experiment dataset content: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=MSG_UNEXPECTED_ERROR_GETTING_DATASET_CONTENT,
        ) from exc
    # pylint: enable=duplicate-code
