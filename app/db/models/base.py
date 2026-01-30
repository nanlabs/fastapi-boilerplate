"""
SQLAlchemy declarative base for database models.

This module provides the Base class that serves as the foundation for all
database models in the application. It extends SQLAlchemy's DeclarativeBase
to provide common functionality such as automatic timestamp tracking.

All database models should inherit from this Base class to ensure consistent
behavior across the application, including automatic creation and update
timestamp management.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models.

    This abstract base class provides common functionality for all database
    models, including automatic timestamp management. All models inheriting
    from this class will automatically have created_at and updated_at columns
    that are managed by the database server.

    The created_at timestamp is set automatically when a record is first created,
    and the updated_at timestamp is automatically updated whenever a record is
    modified. Both timestamps are stored with timezone information to ensure
    accurate time tracking across different time zones.
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
