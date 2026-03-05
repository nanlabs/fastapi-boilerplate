"""Unit tests for app.api.services.utils."""

from unittest.mock import MagicMock

from sqlalchemy.orm import Query

from app.api.schemas.common.params import SortDirection
from app.api.services.utils import apply_sorting


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
