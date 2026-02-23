"""
Project database model.

This module defines the Project database model using SQLAlchemy ORM.
Projects serve as a top-level organizational unit for API resources.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Project(Base):
    """Project model for storing project information."""

    __tablename__ = "projects"
    valid_sort_fields = {"id", "name", "created_at", "updated_at"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
