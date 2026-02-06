"""Database initialization and seed data."""

import logging
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TextIO

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from alembic import command, script
from app.core.config import settings
from app.db.models.base import Base
from app.db.seed_data import load_seed_data
from app.db.session import SESSION_LOCAL, engine

logger = logging.getLogger("uvicorn.error")

# Platform-specific imports for file locking
try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment, misc]  # Windows doesn't have fcntl

try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None  # type: ignore[assignment, misc]  # Unix doesn't have msvcrt  # pragma: no cover


def try_acquire_lock(lock_file: TextIO) -> None:
    """Try to acquire a non-blocking file lock."""
    if os.name == "nt":
        if msvcrt is None:
            raise RuntimeError("msvcrt module not available on Windows")
        try:
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)  # type: ignore[attr-defined, union-attr]  # pylint: disable=line-too-long
        except OSError as exc:
            raise BlockingIOError from exc
    else:
        if fcntl is None:
            raise RuntimeError("fcntl module not available on Unix")
        try:
            fcntl.flock(  # type: ignore[attr-defined, union-attr]
                lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB  # type: ignore[attr-defined]
            )
        except OSError as exc:
            raise BlockingIOError from exc


def release_lock(lock_file: TextIO) -> None:
    """Release a previously acquired file lock."""
    if os.name == "nt":
        if msvcrt is None:
            raise RuntimeError("msvcrt module not available on Windows")
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined, union-attr]  # pylint: disable=line-too-long
    else:
        if fcntl is None:
            raise RuntimeError("fcntl module not available on Unix")
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined, union-attr]


@contextmanager
def database_init_lock(timeout_seconds: float = 10.0) -> Iterator[bool]:
    """Serialize database initialization across processes."""
    lock_path = settings.database_path.parent / ".db_init.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    start_time = time.monotonic()
    remove_lock = False

    try:
        with open(lock_path, "a+", encoding="utf-8") as lock_file:
            while True:
                try:
                    try_acquire_lock(lock_file)
                    acquired = True
                    break
                except BlockingIOError:
                    if time.monotonic() - start_time >= timeout_seconds:
                        break
                    time.sleep(0.2)

            try:
                yield acquired
            finally:
                if acquired:
                    release_lock(lock_file)
                    remove_lock = True
    finally:
        if remove_lock:
            try:
                lock_path.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning("Failed to remove database init lock file: %s", exc)


def database_exists() -> bool:
    """Check if database file exists."""
    return settings.database_path.exists()


def tables_exist() -> bool:
    """Check if database tables exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    required_tables = list(Base.metadata.tables.keys())
    return all(table in existing_tables for table in required_tables)


def run_migrations() -> None:
    """Run Alembic migrations to create/update database schema."""
    alembic_cfg = Config("alembic.ini")

    # Check if tables exist but alembic_version doesn't (e.g., tables created manually)
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    has_alembic_version = "alembic_version" in existing_tables
    has_required_tables = tables_exist()

    # If tables exist but alembic_version doesn't, stamp the database with current revision
    if has_required_tables and not has_alembic_version:
        logger.info("Tables exist but alembic_version missing, stamping database...")
        try:
            command.stamp(alembic_cfg, "head")
            logger.info("Database stamped with current revision")
            return
        except Exception as stamp_exc:
            logger.warning("Failed to stamp database, will try upgrade: %s", stamp_exc)

    # Check if there are pending migrations before running upgrade
    try:
        script_dir = script.ScriptDirectory.from_config(alembic_cfg)
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            head_rev = script_dir.get_current_head()

            if current_rev == head_rev:
                logger.info(
                    "Database is already at head revision (%s), skipping migrations", head_rev
                )
                return
            logger.info(
                "Current revision: %s, Head revision: %s. Running migrations...",
                current_rev,
                head_rev,
            )
    except Exception as check_exc:
        logger.warning("Could not check migration status, will attempt upgrade: %s", check_exc)

    # Try to run migrations
    try:
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as exc:
        # If migration fails due to tables already existing, try to stamp instead
        error_msg = str(exc).lower()
        if "already exists" in error_msg:
            logger.warning(
                "Migration failed because tables already exist, attempting to stamp database: %s",
                exc,
            )
            try:
                # Verify tables actually exist before stamping
                if tables_exist():
                    command.stamp(alembic_cfg, "head")
                    logger.info("Database stamped with current revision")  # pragma: no cover
                    return  # pragma: no cover
                logger.error("Tables don't exist but migration failed, re-raising error")
                raise
            except Exception as stamp_exc:
                logger.error("Failed to stamp database: %s", stamp_exc)
                # If stamping also fails, check if it's because alembic_version already exists
                if "already exists" not in str(stamp_exc).lower():
                    raise

        logger.error("Failed to run database migrations: %s", exc)
        raise


def init_database() -> None:
    """Initialize database: run migrations and seed default data."""
    logger.info("Initializing database...")
    logger.info("Database path: %s", settings.database_path)
    logger.info("Database URL: %s", settings.resolved_database_url)

    settings.database_path.parent.mkdir(parents=True, exist_ok=True)

    with database_init_lock(timeout_seconds=10.0) as acquired:
        if not acquired:
            if database_exists() and tables_exist():
                logger.info("Database initialization already in progress, skipping.")
                return
            raise TimeoutError("Timed out waiting for database initialization lock.")

        run_migrations()
        logger.info("Database tables created/verified")
        seed_default_data()


def seed_default_data() -> None:
    """Load and process seed data from configuration.
    
    Extend this function to add your own seed data initialization logic.
    By default, it only validates that the seed data configuration is loadable.
    """
    try:
        # Load seed data configuration (validates it's parseable)
        load_seed_data()
        logger.info("Seed data configuration validated successfully")
    except (FileNotFoundError, ValueError) as exc:
        logger.warning("No seed data or validation error: %s", exc)
    except Exception as exc:
        logger.error("Unexpected error loading seed data: %s", exc)
        raise
