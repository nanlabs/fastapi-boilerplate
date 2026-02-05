"""
Model type database model.

This module defines the ModelType database model using SQLAlchemy ORM.
Model types represent different categories of analytical models available
in the system, such as "Credit Models", "Fraud Models", "Marketing Models", etc.
Each model type has metadata including a description and enabled status.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.schemas.common.base import ModelTypeStatus

if TYPE_CHECKING:
    from app.db.models.experiment import Experiment


class ModelType(Base):
    """Model type model for storing model type information.

    Represents a category of analytical models with rich metadata. Each
    model type has a name, optional multiline description, and enabled status.
    """

    __tablename__ = "model_types"
    valid_sort_fields = {"id", "name"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text(f"'{ModelTypeStatus.AVAILABLE.value}'")
    )

    # Relationships
    experiments: Mapped[list[Experiment]] = relationship(
        "Experiment",
        back_populates="model_type",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
