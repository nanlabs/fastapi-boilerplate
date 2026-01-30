"""Common API parameters and response schemas for list endpoints."""

from enum import Enum
from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SortDirection(str, Enum):
    """Sort direction enum."""

    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of records to return"
    )


class SortingParams(BaseModel):
    """Sorting parameters."""

    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_direction: SortDirection = Field(
        default=SortDirection.ASC, description="Sort direction (asc or desc)"
    )


class SearchParams(BaseModel):
    """Search parameters."""

    search: str | None = Field(default=None, description="Search term to filter results")


class ListQueryParams(BaseModel):
    """Common query parameters for list endpoints."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of records to return"
    )
    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_direction: SortDirection = Field(
        default=SortDirection.ASC, description="Sort direction (asc or desc)"
    )
    search: str | None = Field(default=None, description="Search term to filter results")


class ListResponse[T](BaseModel):
    """Generic list response with pagination, sorting, search, and data."""

    pagination: PaginationParams = Field(..., description="Pagination parameters used")
    sort: SortingParams = Field(..., description="Sorting parameters used")
    search: SearchParams = Field(..., description="Search parameters used")
    data: list[T] = Field(..., description="List of items")
