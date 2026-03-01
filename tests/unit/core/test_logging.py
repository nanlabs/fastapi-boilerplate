"""Tests for logging configuration."""

import json
import logging

from app.core.logging_config import JSONFormatter, configure_logging


class TestConfigureLogging:
    def test_configure_sets_root_level_info(self) -> None:
        configure_logging(debug=False)
        assert logging.getLogger().level == logging.INFO

    def test_configure_debug_sets_debug_level(self) -> None:
        configure_logging(debug=True)
        assert logging.getLogger().level == logging.DEBUG
        configure_logging(debug=False)

    def test_json_formatter_produces_valid_json(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Hello world",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["message"] == "Hello world"
        assert parsed["level"] == "INFO"
        assert "timestamp" in parsed
