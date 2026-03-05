"""Unit tests for app.api.dependencies.query_params."""

from app.api.dependencies.query_params import get_pagination, get_search, get_sorting
from app.api.schemas.common.params import (
    PaginationParams,
    SearchParams,
    SortDirection,
    SortingParams,
)


class TestGetPagination:
    """Test get_pagination dependency function."""

    def test_get_pagination_defaults(self) -> None:
        """Return PaginationParams with default values."""
        result = get_pagination()

        assert isinstance(result, PaginationParams)
        assert result.skip == 0
        assert result.limit == 100

    def test_get_pagination_custom_values(self) -> None:
        """Return PaginationParams with custom values."""
        result = get_pagination(skip=10, limit=50)

        assert isinstance(result, PaginationParams)
        assert result.skip == 10
        assert result.limit == 50

    def test_get_pagination_zero_skip(self) -> None:
        """Return PaginationParams with zero skip."""
        result = get_pagination(skip=0, limit=25)

        assert isinstance(result, PaginationParams)
        assert result.skip == 0
        assert result.limit == 25


class TestGetSorting:
    """Test get_sorting dependency function."""

    def test_get_sorting_defaults(self) -> None:
        """Return SortingParams with default values."""
        result = get_sorting()

        assert isinstance(result, SortingParams)
        assert result.sort_by is None
        assert result.sort_direction == SortDirection.ASC

    def test_get_sorting_with_sort_by(self) -> None:
        """Return SortingParams with sort_by field."""
        result = get_sorting(sort_by="name")

        assert isinstance(result, SortingParams)
        assert result.sort_by == "name"
        assert result.sort_direction == SortDirection.ASC

    def test_get_sorting_asc_direction(self) -> None:
        """Return SortingParams with ascending direction."""
        result = get_sorting(sort_by="id", sort_direction=SortDirection.ASC)

        assert isinstance(result, SortingParams)
        assert result.sort_by == "id"
        assert result.sort_direction == SortDirection.ASC

    def test_get_sorting_desc_direction(self) -> None:
        """Return SortingParams with descending direction."""
        result = get_sorting(sort_by="name", sort_direction=SortDirection.DESC)

        assert isinstance(result, SortingParams)
        assert result.sort_by == "name"
        assert result.sort_direction == SortDirection.DESC

    def test_get_sorting_none_sort_by(self) -> None:
        """Return SortingParams with None sort_by."""
        result = get_sorting(sort_by=None, sort_direction=SortDirection.DESC)

        assert isinstance(result, SortingParams)
        assert result.sort_by is None
        assert result.sort_direction == SortDirection.DESC


class TestGetSearch:
    """Test get_search dependency function."""

    def test_get_search_default(self) -> None:
        """Return SearchParams with default None value."""
        result = get_search()

        assert isinstance(result, SearchParams)
        assert result.search is None

    def test_get_search_with_term(self) -> None:
        """Return SearchParams with search term."""
        result = get_search(search="test query")

        assert isinstance(result, SearchParams)
        assert result.search == "test query"

    def test_get_search_none(self) -> None:
        """Return SearchParams with explicit None."""
        result = get_search(search=None)

        assert isinstance(result, SearchParams)
        assert result.search is None

    def test_get_search_empty_string(self) -> None:
        """Return SearchParams with empty string."""
        result = get_search(search="")

        assert isinstance(result, SearchParams)
        assert result.search == ""
