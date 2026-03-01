"""Unit tests for main application module."""

import logging
from unittest.mock import AsyncMock, patch

import pytest

import app.main
from app.core.config import settings
from app.main import lifespan


class TestConfigureLogging:
    """Test logging configuration integration."""

    def test_configure_logging_called_in_lifespan(self) -> None:
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        try:
            with patch.object(app.main, "configure_logging") as mock_configure_logging:
                mock_app = AsyncMock()

                async def _run() -> None:
                    async with lifespan(mock_app):
                        pass

                import asyncio

                asyncio.run(_run())

                mock_configure_logging.assert_called_once()
        finally:
            root_logger.handlers = original_handlers


class TestLifespan:
    """Test lifespan behavior."""

    @pytest.mark.asyncio
    async def test_lifespan_calls_init_database_when_not_testing(self) -> None:
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
            patch.object(app.main, "configure_logging") as mock_configure_logging,
        ):
            async with lifespan(mock_app):
                pass

        mock_configure_logging.assert_called_once_with(debug=settings.debug)
        mock_init_database.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_skips_init_database_when_testing(self) -> None:
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
            patch.object(app.main, "configure_logging") as mock_configure_logging,
        ):
            async with lifespan(mock_app):
                pass

        mock_configure_logging.assert_called_once_with(debug=settings.debug)
        mock_init_database.assert_not_called()

    @pytest.mark.asyncio
    async def test_lifespan_skips_init_database_when_skip_db_init(self) -> None:
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
            patch.object(app.main, "configure_logging") as mock_configure_logging,
        ):
            async with lifespan(mock_app):
                pass

        mock_configure_logging.assert_called_once_with(debug=settings.debug)
        mock_init_database.assert_not_called()
