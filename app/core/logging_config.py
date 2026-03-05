"""Structured logging configuration."""

import json
import logging
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, str] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id:
            log_data["request_id"] = str(request_id)

        method = getattr(record, "method", None)
        if method:
            log_data["method"] = str(method)

        path = getattr(record, "path", None)
        if path:
            log_data["path"] = str(path)

        status_code = getattr(record, "status_code", None)
        if status_code:
            log_data["status_code"] = str(status_code)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging(debug: bool = False) -> None:
    """Configure application logging.

    Uses JSON output in production and human-readable output in development.
    """
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler()
    if debug:
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    else:
        handler.setFormatter(JSONFormatter())

    root_logger.addHandler(handler)
    root_logger.setLevel(level)
