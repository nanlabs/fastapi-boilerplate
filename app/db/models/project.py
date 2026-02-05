"""
Project database model.

This module defines the Project database model using SQLAlchemy ORM.
Projects serve as the top-level organizational unit for workflow execution,
containing multiple experiments and providing context for analysis tasks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.experiment import Experiment


class Project(Base):
    """Project model for storing project information."""

    __tablename__ = "projects"
    valid_sort_fields = {"id", "name", "created_at", "updated_at"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    experiments: Mapped[list[Experiment]] = relationship(
        "Experiment",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
