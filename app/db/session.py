"""Database session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Create engine
engine = create_engine(
    settings.resolved_database_url,
    echo=settings.database_echo,
    connect_args=({"check_same_thread": False} if "sqlite" in settings.database_url else {}),
)

# Create session factory
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session]:
    """Dependency for getting database session."""
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
