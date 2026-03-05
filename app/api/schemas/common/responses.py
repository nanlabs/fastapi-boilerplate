"""Standard API response envelope used by all endpoints."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.api.schemas.common.params import PaginationParams, SearchParams, SortingParams


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    skip: int
    limit: int
    total: int


class ResponseMetadata(BaseModel):
    """Metadata attached to every API response."""

    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    pagination: PaginationMeta | None = None
    sort: SortingParams | None = None
    search: SearchParams | None = None


class ErrorDetail(BaseModel):
    """A single validation or business error."""

    field: str | None = None
    message: str


class APIResponse[T](BaseModel):
    """Universal response envelope for all API endpoints."""

    success: bool
    status_code: int
    dev_code: str
    message: str
    data: T | None
    errors: list[ErrorDetail] = Field(default_factory=list)
    metadata: ResponseMetadata


def make_item_response(
    data: Any,
    dev_code: str,
    message: str,
    request_id: str,
    status_code: int = 200,
) -> APIResponse[Any]:
    """Build a success response for a single resource."""
    return APIResponse(
        success=True,
        status_code=status_code,
        dev_code=dev_code,
        message=message,
        data=data,
        errors=[],
        metadata=ResponseMetadata(
            request_id=request_id,
            timestamp=datetime.now(UTC),
        ),
    )


def make_list_response(
    data: list[Any],
    total: int,
    pagination: PaginationParams,
    sorting: SortingParams,
    search: SearchParams,
    dev_code: str,
    message: str,
    request_id: str,
) -> APIResponse[list[Any]]:
    """Build a success response for a list of resources."""
    return APIResponse(
        success=True,
        status_code=200,
        dev_code=dev_code,
        message=message,
        data=data,
        errors=[],
        metadata=ResponseMetadata(
            request_id=request_id,
            timestamp=datetime.now(UTC),
            pagination=PaginationMeta(
                skip=pagination.skip,
                limit=pagination.limit,
                total=total,
            ),
            sort=sorting,
            search=search,
        ),
    )


def make_error_response(
    status_code: int,
    dev_code: str,
    message: str,
    request_id: str,
    errors: list[ErrorDetail] | None = None,
) -> APIResponse[None]:
    """Build an error response."""
    return APIResponse(
        success=False,
        status_code=status_code,
        dev_code=dev_code,
        message=message,
        data=None,
        errors=errors or [],
        metadata=ResponseMetadata(
            request_id=request_id,
            timestamp=datetime.now(UTC),
        ),
    )
