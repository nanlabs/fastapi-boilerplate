"""Tests for common parameter schemas."""

import pytest
from pydantic import ValidationError

from app.api.schemas.common.params import (
    PaginationParams,
    SearchParams,
    SortDirection,
    SortingParams,
)


def test_pagination_defaults() -> None:
    params = PaginationParams()
    assert params.skip == 0
    assert params.limit == 100


def test_pagination_validation() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(skip=-1)
    with pytest.raises(ValidationError):
        PaginationParams(limit=0)
    with pytest.raises(ValidationError):
        PaginationParams(limit=1001)


def test_sorting_defaults() -> None:
    params = SortingParams()
    assert params.sort_by is None
    assert params.sort_direction == SortDirection.ASC


def test_search_defaults() -> None:
    params = SearchParams()
    assert params.search is None
