"""Global exception handlers registered in the application."""

import logging

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError, ValidationError
from app.api.schemas.common.responses import ErrorDetail, make_error_response

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, NotFoundError)
    resp = make_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        dev_code="NOT_FOUND",
        message=exc.message,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(resp))


async def conflict_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ConflictError)
    resp = make_error_response(
        status_code=status.HTTP_409_CONFLICT,
        dev_code="CONFLICT",
        message=exc.message,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=jsonable_encoder(resp))


async def sorting_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, SortingValidationError)
    resp = make_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        dev_code="INVALID_SORT_FIELD",
        message=exc.message,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(resp))


async def api_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ValidationError)
    resp = make_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        dev_code="VALIDATION_ERROR",
        message=exc.message,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(resp))


async def request_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [
        ErrorDetail(
            field=".".join(str(loc) for loc in err["loc"] if loc != "body"),
            message=err["msg"],
        )
        for err in exc.errors()
    ]
    resp = make_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        dev_code="VALIDATION_ERROR",
        message="Request validation failed",
        request_id=_request_id(request),
        errors=errors,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(resp),
    )


async def database_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Database error: %s", exc, exc_info=True)
    resp = make_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        dev_code="DATABASE_ERROR",
        message="A database error occurred",
        request_id=_request_id(request),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(resp)
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unexpected error: %s", exc, exc_info=True)
    resp = make_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        dev_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        request_id=_request_id(request),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(resp)
    )
