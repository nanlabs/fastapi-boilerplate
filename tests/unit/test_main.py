"""Unit tests for main application module."""

# pylint: disable=duplicate-code

import logging
from unittest.mock import AsyncMock, patch

import pytest

import app.main
from app.main import _configure_logging, lifespan


class TestConfigureLogging:
    """Test _configure_logging function."""

    def test_configure_logging_sets_basic_config_when_no_handlers(self) -> None:
        """Configure basic logging when root logger has no handlers."""
        # Remove all handlers from root logger
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers.clear()

        try:
            with patch("logging.basicConfig") as mock_basic_config:
                _configure_logging()
                mock_basic_config.assert_called_once_with(level=logging.INFO)
        finally:
            # Restore original handlers
            root_logger.handlers = original_handlers

    def test_configure_logging_skips_when_handlers_exist(self) -> None:
        """Skip basic config when root logger already has handlers."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]

        # Ensure there's at least one handler
        if not root_logger.handlers:
            handler = logging.StreamHandler()
            root_logger.addHandler(handler)

        try:
            with patch("logging.basicConfig") as mock_basic_config:
                _configure_logging()
                mock_basic_config.assert_not_called()
        finally:
            # Restore original handlers
            root_logger.handlers = original_handlers


class TestLifespan:
    """Test lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_calls_init_database_when_not_testing(self) -> None:
        """Call init_database when TESTING and SKIP_DB_INIT are not set to 'true'."""
        mock_app = AsyncMock()

        def mock_getenv(key: str, default: str | None = None) -> str | None:
            if key == "TESTING":
                return None
            if key == "SKIP_DB_INIT":
                return None
            return default

        with (
            patch("os.getenv", side_effect=mock_getenv),
            patch.object(app.main, "init_database") as mock_init_database,
            patch.object(app.main, "_configure_logging") as mock_configure_logging,
        ):
            async with lifespan(mock_app):
                pass

        mock_configure_logging.assert_called_once()
        mock_init_database.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_skips_init_database_when_testing(self) -> None:
        """Skip init_database when TESTING is set to 'true'."""
        mock_app = AsyncMock()

        def mock_getenv(key: str, default: str | None = None) -> str | None:
            if key == "TESTING":
                return "true"
            if key == "SKIP_DB_INIT":
                return None
            return default

        with (
            patch("os.getenv", side_effect=mock_getenv),
            patch.object(app.main, "init_database") as mock_init_database,
            patch.object(app.main, "_configure_logging") as mock_configure_logging,
        ):
            async with lifespan(mock_app):
                pass

        mock_configure_logging.assert_called_once()
        mock_init_database.assert_not_called()

    @pytest.mark.asyncio
    async def test_lifespan_skips_init_database_when_skip_db_init(self) -> None:
        """Skip init_database when SKIP_DB_INIT is set to 'true'."""
        mock_app = AsyncMock()

        def mock_getenv(key: str, default: str | None = None) -> str | None:
            if key == "TESTING":
                return None
            if key == "SKIP_DB_INIT":
                return "true"
            return default

        with (
            patch("os.getenv", side_effect=mock_getenv),
            patch.object(app.main, "init_database") as mock_init_database,
            patch.object(app.main, "_configure_logging") as mock_configure_logging,
        ):
            async with lifespan(mock_app):
                pass

        mock_configure_logging.assert_called_once()
        mock_init_database.assert_not_called()
