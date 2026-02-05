"""
Experiment type database model.

This module defines the ExperimentType database model using SQLAlchemy ORM.
Experiment types represent the fundamental categories of experiments,
such as "classification" and "regression". These are simple, foundational types that
categorize the nature of the experiment being performed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.experiment import Experiment


class ExperimentType(Base):
    """Experiment type model for storing experiment type information.

    Represents a fundamental category of experiments, such as
    "classification" or "regression". These types are simple identifiers that
    categorize the nature of the experiment being performed.

    Examples from seed data:
    - classification: For classification tasks
    - regression: For regression tasks
    """

    __tablename__ = "experiment_types"
    valid_sort_fields = {"id", "name"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    # Relationships
    experiments: Mapped[list[Experiment]] = relationship(
        "Experiment",
        back_populates="experiment_type",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
