"""Dependencies for query parameters."""

from typing import Annotated

from fastapi import Query

from app.api.schemas.api import PaginationParams, SearchParams, SortDirection, SortingParams


def get_pagination(
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Maximum number of records to return")
    ] = 100,
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(skip=skip, limit=limit)


def get_sorting(
    sort_by: Annotated[str | None, Query(description="Field to sort by")] = None,
    sort_direction: Annotated[
        SortDirection, Query(description="Sort direction (asc or desc)")
    ] = SortDirection.ASC,
) -> SortingParams:
    """Get sorting parameters."""
    return SortingParams(sort_by=sort_by, sort_direction=sort_direction)


def get_search(
    search: Annotated[str | None, Query(description="Search term to filter results")] = None,
) -> SearchParams:
    """Get search parameter."""
    return SearchParams(search=search)
