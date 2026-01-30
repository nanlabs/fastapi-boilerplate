"""Utility functions for services."""

from typing import Any

from sqlalchemy.orm import Query

from app.api.schemas.api import (
    ListResponse,
    PaginationParams,
    SearchParams,
    SortDirection,
    SortingParams,
)


def apply_sorting(query: Query, sort_column: Any, sort_direction: SortDirection) -> Query:
    """Apply sorting to a query based on sort column and direction."""
    if sort_direction == SortDirection.DESC:
        return query.order_by(sort_column.desc())
    return query.order_by(sort_column.asc())


def build_list_response[
    T
](
    pagination: PaginationParams,
    sorting: SortingParams,
    search_params: SearchParams,
    data: list[T],
) -> ListResponse[T]:
    """Build a ListResponse from pagination, sorting, search, and data."""
    return ListResponse(
        pagination=pagination,
        sort=sorting,
        search=search_params,
        data=data,
    )
