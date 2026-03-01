"""Utility functions for services."""

from typing import Any

from sqlalchemy.orm import Query

from app.api.schemas.common.params import SortDirection


def apply_sorting(query: Query[Any], sort_column: Any, sort_direction: SortDirection) -> Query[Any]:
    """Apply sorting to a query based on sort column and direction."""
    if sort_direction == SortDirection.DESC:
        return query.order_by(sort_column.desc())
    return query.order_by(sort_column.asc())
