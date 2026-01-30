"""Pytest configuration and fixtures for FastAPI tests."""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

# Set TESTING environment variable before importing app to skip database initialization
os.environ["TESTING"] = "true"

# pylint: disable=wrong-import-position
from app.db.models.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

# pylint: enable=wrong-import-position


@pytest.fixture(scope="session", name="test_db_path")
def _test_db_path() -> Path:
    """Create a temporary database file for testing."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    return Path(db_path)


@pytest.fixture(scope="session", name="test_engine")
def _test_engine(test_db_path: Path) -> Generator[Engine]:
    """Create a test database engine."""
    test_db_url = f"sqlite:///{test_db_path}"
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    # Clean up test database file
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture(name="db_session")
def _db_session(test_engine) -> Generator[Session]:
    """Create a test database session."""
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(name="client")
def _client(db_session: Session) -> Generator[TestClient]:
    """Create a test client with database override."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()
