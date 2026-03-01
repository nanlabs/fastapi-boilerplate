"""Common query parameter schemas shared across API versions."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SortDirection(StrEnum):
    """Sort direction enum."""

    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return")


class SortingParams(BaseModel):
    """Sorting parameters."""

    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")


class SearchParams(BaseModel):
    """Search parameters."""

    search: str | None = Field(default=None, description="Search term to filter results")
