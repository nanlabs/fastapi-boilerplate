"""Database initialization and seed data."""

import logging
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from typing import TextIO

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from alembic import command, script
from app.core.config import settings
from app.db.models.base import Base
from app.db.models.experiment_type import ExperimentType
from app.db.models.model_type import ModelType as ModelTypeDB
from app.db.seed_data import get_default_experiment_types, get_default_model_types, get_status_value
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
    """Synchronize model types and experiment types from seed data configuration with database."""
    db: Session = SESSION_LOCAL()
    try:
        # Synchronize model types
        logger.info("Synchronizing model types from seed data...")
        synchronize_model_types(db, get_default_model_types())

        # Synchronize experiment types
        logger.info("Synchronizing experiment types from seed data...")
        synchronize_experiment_types(db, get_default_experiment_types())
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Error loading seed data: %s", exc)
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        logger.error("Database error during seed data synchronization: %s", exc)
        db.rollback()
        raise
    except Exception as exc:
        logger.error("Unexpected error during seed data synchronization: %s", exc)
        db.rollback()
        raise
    finally:
        db.close()


def synchronize_model_types(db: Session, yaml_types: list) -> None:
    """Synchronize model types from YAML configuration."""
    yaml_types_by_id = {model_type.id: model_type for model_type in yaml_types}
    all_existing_types = db.query(ModelTypeDB).all()
    all_existing_types_by_id = {model_type.id: model_type for model_type in all_existing_types}
    existing_types = [
        model_type for model_type in all_existing_types if model_type.deleted_at is None
    ]
    existing_types_by_id = {model_type.id: model_type for model_type in existing_types}
    counts = {"created": 0, "updated": 0, "unchanged": 0, "deleted": 0}

    for yaml_type in yaml_types:
        existing_type = existing_types_by_id.get(yaml_type.id)

        if existing_type is None:
            existing_by_id = all_existing_types_by_id.get(yaml_type.id)
            if existing_by_id:
                was_deleted = existing_by_id.deleted_at is not None
                existing_by_id.name = yaml_type.name
                existing_by_id.description = yaml_type.description
                existing_by_id.enabled = yaml_type.enabled
                existing_by_id.status = get_status_value(yaml_type.status)
                existing_by_id.deleted_at = None
                counts["updated"] += 1
                if was_deleted:
                    logger.info("Restoring model type: %s (ID: %d)", yaml_type.name, yaml_type.id)
                else:  # pragma: no cover
                    logger.info(  # pragma: no cover
                        "Updating model type by ID: %s (ID: %d)",
                        yaml_type.name,
                        yaml_type.id,  # pragma: no cover
                    )
            else:
                db.add(yaml_type)
                counts["created"] += 1
                logger.info("Creating model type: %s (ID: %d)", yaml_type.name, yaml_type.id)
        else:
            needs_update = (
                existing_type.name != yaml_type.name
                or existing_type.description != yaml_type.description
                or existing_type.enabled != yaml_type.enabled
                or existing_type.status != get_status_value(yaml_type.status)
            )

            if needs_update:
                existing_type.name = yaml_type.name
                existing_type.description = yaml_type.description
                existing_type.enabled = yaml_type.enabled
                existing_type.status = get_status_value(yaml_type.status)
                counts["updated"] += 1
                logger.info("Updating model type: %s (ID: %d)", yaml_type.name, yaml_type.id)
            else:
                counts["unchanged"] += 1

    for existing_type in existing_types:
        if existing_type.id not in yaml_types_by_id:
            if existing_type.deleted_at is None:
                existing_type.deleted_at = datetime.now()
                counts["deleted"] += 1
                logger.info(
                    "Logically deleting model type: %s (ID: %d)",
                    existing_type.name,
                    existing_type.id,
                )

    db.commit()

    logger.info(
        "Model types synchronization complete: %d created, %d updated, %d unchanged, %d deleted",
        counts["created"],
        counts["updated"],
        counts["unchanged"],
        counts["deleted"],
    )


def _build_yaml_mappings(
    yaml_types: list[ExperimentType],
) -> tuple[dict[int | None, ExperimentType], dict[str, ExperimentType]]:
    """Build mappings from YAML types by ID and name."""
    yaml_types_by_id: dict[int | None, ExperimentType] = {}
    yaml_types_by_name: dict[str, ExperimentType] = {}
    for exp_type in yaml_types:
        if exp_type.id is not None:
            yaml_types_by_id[exp_type.id] = exp_type
        yaml_types_by_name[exp_type.name] = exp_type
    return yaml_types_by_id, yaml_types_by_name


def _get_existing_experiment_types(
    db: Session,
) -> tuple[
    list[ExperimentType],
    dict[int, ExperimentType],
    dict[int, ExperimentType],
    dict[str, ExperimentType],
]:
    """Get existing experiment types from database and build lookup dictionaries."""
    all_existing_types = db.query(ExperimentType).all()
    all_existing_types_by_id = {exp_type.id: exp_type for exp_type in all_existing_types}
    existing_types = [exp_type for exp_type in all_existing_types if exp_type.deleted_at is None]
    existing_types_by_id = {exp_type.id: exp_type for exp_type in existing_types}
    existing_types_by_name = {exp_type.name: exp_type for exp_type in existing_types}
    return existing_types, all_existing_types_by_id, existing_types_by_id, existing_types_by_name


def _update_experiment_type_by_name(
    existing_by_name: ExperimentType,
    yaml_type: ExperimentType,
    counts: dict[str, int],
) -> None:
    """Update experiment type found by name."""
    if existing_by_name.name != yaml_type.name:  # pragma: no cover
        existing_by_name.name = yaml_type.name  # pragma: no cover
    existing_by_name.deleted_at = None
    counts["updated"] += 1
    logger.info(
        "Updating experiment type by name: %s (existing ID: %d, YAML ID: %s)",
        yaml_type.name,
        existing_by_name.id,
        yaml_type.id if yaml_type.id is not None else "None",
    )


def _restore_or_update_experiment_type_by_id(
    existing_by_id: ExperimentType,
    yaml_type: ExperimentType,
    counts: dict[str, int],
) -> None:
    """Restore or update experiment type found by ID in all existing types."""
    was_deleted = existing_by_id.deleted_at is not None
    existing_by_id.name = yaml_type.name
    existing_by_id.deleted_at = None
    counts["updated"] += 1
    if was_deleted:
        logger.info("Restoring experiment type: %s (ID: %d)", yaml_type.name, yaml_type.id)
    else:  # pragma: no cover
        logger.info(  # pragma: no cover
            "Updating experiment type by ID: %s (ID: %d)",  # pragma: no cover
            yaml_type.name,  # pragma: no cover
            yaml_type.id,  # pragma: no cover
        )


def _create_new_experiment_type(
    db: Session, yaml_type: ExperimentType, counts: dict[str, int]
) -> None:
    """Create a new experiment type."""
    db.add(yaml_type)
    counts["created"] += 1
    logger.info(
        "Creating experiment type: %s (ID: %s)",
        yaml_type.name,
        yaml_type.id if yaml_type.id is not None else "auto",
    )


def _update_existing_experiment_type(
    existing_type: ExperimentType, yaml_type: ExperimentType, counts: dict[str, int]
) -> None:
    """Update an existing experiment type found by ID."""
    needs_update = existing_type.name != yaml_type.name
    if needs_update:
        existing_type.name = yaml_type.name
        counts["updated"] += 1
        logger.info("Updating experiment type: %s (ID: %d)", yaml_type.name, yaml_type.id)
    else:
        counts["unchanged"] += 1


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _process_yaml_experiment_type(
    db: Session,
    yaml_type: ExperimentType,
    all_existing_types_by_id: dict[int, ExperimentType],
    existing_types_by_id: dict[int, ExperimentType],
    existing_types_by_name: dict[str, ExperimentType],
    counts: dict[str, int],
) -> None:
    """Process a single YAML experiment type (create or update)."""
    existing_type = None
    if yaml_type.id is not None:
        existing_type = existing_types_by_id.get(yaml_type.id)

    if existing_type is None:
        existing_by_name = existing_types_by_name.get(yaml_type.name)
        if existing_by_name:
            _update_experiment_type_by_name(existing_by_name, yaml_type, counts)
        elif yaml_type.id is not None and yaml_type.id in all_existing_types_by_id:
            existing_by_id = all_existing_types_by_id[yaml_type.id]
            _restore_or_update_experiment_type_by_id(existing_by_id, yaml_type, counts)
        else:
            _create_new_experiment_type(db, yaml_type, counts)
    else:
        _update_existing_experiment_type(existing_type, yaml_type, counts)


def _mark_experiment_types_for_deletion(
    existing_types: list[ExperimentType],
    yaml_types_by_id: dict[int | None, ExperimentType],
    yaml_types_by_name: dict[str, ExperimentType],
    counts: dict[str, int],
) -> None:
    """Mark experiment types for deletion if they're not in YAML."""
    for existing_type in existing_types:
        should_delete = True
        if existing_type.id is not None and existing_type.id in yaml_types_by_id:
            should_delete = False
        elif existing_type.name in yaml_types_by_name:
            should_delete = False

        if should_delete and existing_type.deleted_at is None:
            existing_type.deleted_at = datetime.now()
            counts["deleted"] += 1
            logger.info(
                "Logically deleting experiment type: %s (ID: %d)",
                existing_type.name,
                existing_type.id,
            )


def synchronize_experiment_types(db: Session, yaml_types: list[ExperimentType]) -> None:
    """Synchronize experiment types from YAML configuration."""
    yaml_types_by_id, yaml_types_by_name = _build_yaml_mappings(yaml_types)
    existing_types, all_existing_types_by_id, existing_types_by_id, existing_types_by_name = (
        _get_existing_experiment_types(db)
    )
    counts = {"created": 0, "updated": 0, "unchanged": 0, "deleted": 0}

    for yaml_type in yaml_types:
        _process_yaml_experiment_type(
            db,
            yaml_type,
            all_existing_types_by_id,
            existing_types_by_id,
            existing_types_by_name,
            counts,
        )

    _mark_experiment_types_for_deletion(
        existing_types, yaml_types_by_id, yaml_types_by_name, counts
    )

    db.commit()

    logger.info(
        "Experiment types synchronization complete: %d created, %d updated, "
        "%d unchanged, %d deleted",
        counts["created"],
        counts["updated"],
        counts["unchanged"],
        counts["deleted"],
    )
