"""
Experiment database model.

This module defines the Experiment database model using SQLAlchemy ORM.
Experiments represent individual machine learning workflow executions within
a project, categorized by type such as credit models, fraud models, or
marketing models.

The Experiment model tracks experiment metadata including name, type,
description, and automatic timestamps. Each experiment belongs to a single
project through a foreign key relationship, enabling project-based
organization and management of ML experiments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.schemas.common.base import ExperimentStatus

if TYPE_CHECKING:
    from app.db.models.dataset_file import DatasetFile
    from app.db.models.experiment_type import ExperimentType
    from app.db.models.model_type import ModelType
    from app.db.models.project import Project


class Experiment(Base):
    """Experiment model for storing experiment information."""

    __tablename__ = "experiments"
    valid_sort_fields = {"id", "name", "created_at", "updated_at"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text(f"'{ExperimentStatus.DRAFT.value}'")
    )
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    # Public/stable identifier for ML side and external references
    _ml_experiment_id: Mapped[str] = mapped_column(
        "ml_experiment_id",
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )

    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    experiment_type_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("experiment_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model_type_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("model_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    dataset_file_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dataset_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="experiments")
    experiment_type: Mapped[ExperimentType | None] = relationship(
        "ExperimentType",
        back_populates="experiments",
    )
    model_type: Mapped[ModelType | None] = relationship(
        "ModelType",
        back_populates="experiments",
    )
    dataset_file: Mapped[DatasetFile | None] = relationship("DatasetFile")

    @property
    def ml_experiment_id(self) -> UUID:
        """Return ML experiment id as a UUID instance."""
        return UUID(cast(str, self._ml_experiment_id))
