"""Initialize database with tables and seed data.

This script manually initializes the database. Note that the database
is automatically initialized when the application starts via the lifespan
event handler in app/main.py.
"""

import logging
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.init import init_database  # noqa: E402  # pylint: disable=wrong-import-position


def _configure_logging() -> None:
    """Configure logging with Uvicorn-style formatting."""
    os.environ.setdefault("SKIP_ALEMBIC_LOG_CONFIG", "true")
    try:
        from uvicorn.logging import DefaultFormatter  # pylint: disable=import-outside-toplevel
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(DefaultFormatter(fmt="%(levelprefix)s %(message)s", use_colors=True))

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    logging.getLogger("alembic").setLevel(logging.INFO)
    logging.getLogger("alembic.runtime.migration").setLevel(logging.INFO)


_configure_logging()


def main() -> None:
    """Initialize database manually."""
    logger = logging.getLogger("uvicorn.error")
    logger.info("Manual Database Initialization")
    logger.info("Database is automatically initialized on app startup.")
    logger.info("This script is useful for manual initialization or testing.")

    try:
        init_database()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error("Error initializing database: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
