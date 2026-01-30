"""Unit tests for app.api.services.utils."""

from unittest.mock import MagicMock

from sqlalchemy.orm import Query

from app.api.schemas.api import (
    ListResponse,
    PaginationParams,
    SearchParams,
    SortDirection,
    SortingParams,
)
from app.api.services.utils import apply_sorting, build_list_response


class TestApplySorting:
    """Test apply_sorting function."""

    def test_apply_sorting_asc(self) -> None:
        """Apply ascending sort to query."""
        mock_query = MagicMock(spec=Query)
        mock_column = MagicMock()
        mock_column.asc.return_value = "asc_order_by"
        mock_query.order_by.return_value = mock_query

        result = apply_sorting(mock_query, mock_column, SortDirection.ASC)

        mock_column.asc.assert_called_once()
        mock_query.order_by.assert_called_once_with("asc_order_by")
        assert result == mock_query

    def test_apply_sorting_desc(self) -> None:
        """Apply descending sort to query."""
        mock_query = MagicMock(spec=Query)
        mock_column = MagicMock()
        mock_column.desc.return_value = "desc_order_by"
        mock_query.order_by.return_value = mock_query

        result = apply_sorting(mock_query, mock_column, SortDirection.DESC)

        mock_column.desc.assert_called_once()
        mock_query.order_by.assert_called_once_with("desc_order_by")
        assert result == mock_query


class TestBuildListResponse:
    """Test build_list_response function."""

    def test_build_list_response(self) -> None:
        """Build ListResponse with pagination, sorting, search, and data."""
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.ASC)
        search_params = SearchParams(search="test")
        data = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]

        result = build_list_response(pagination, sorting, search_params, data)

        assert isinstance(result, ListResponse)
        assert result.pagination == pagination
        assert result.sort == sorting
        assert result.search == search_params
        assert result.data == data

    def test_build_list_response_empty_data(self) -> None:
        """Build ListResponse with empty data list."""
        pagination = PaginationParams(skip=0, limit=10)
        sorting = SortingParams(sort_by="name", sort_direction=SortDirection.DESC)
        search_params = SearchParams(search=None)
        data: list[dict[str, int]] = []

        result = build_list_response(pagination, sorting, search_params, data)

        assert isinstance(result, ListResponse)
        assert result.pagination == pagination
        assert result.sort == sorting
        assert result.search == search_params
        assert result.data == []
