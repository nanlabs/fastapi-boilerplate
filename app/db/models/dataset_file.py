"""
Dataset file database model.

This module defines the DatasetFile database model using SQLAlchemy ORM.
Dataset files represent file references stored in the system, tracking the name
and full path of dataset files without actually storing the file content.
"""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class DatasetFile(Base):
    """Dataset file model for storing dataset file information."""

    __tablename__ = "dataset_files"
    valid_sort_fields = {"id", "name", "path", "created_at", "updated_at"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    path: Mapped[str] = mapped_column(String, nullable=False, index=True)
