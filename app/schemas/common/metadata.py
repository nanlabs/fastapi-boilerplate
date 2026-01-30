"""
Operation metadata schema.

This module defines the metadata structure used to track operations,
including operation ID, status, timestamps, and messages.
"""

import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from app.schemas.common.status import Status


class OperationMetadata(BaseModel):
    """
    Metadata for tracking operations.

    Stores identifiers, status, and timestamps for workflow execution.
    """

    model_id: UUID = Field(..., description="ID of the model")
    operation_id: UUID = Field(default_factory=uuid4, description="Unique operation ID")
    status: Status = Field(default=Status.PENDING, description="Operation status")
    msg: str | None = Field(None, description="Operation message")
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        description="Creation timestamp",
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        description="Last update timestamp",
    )

    @model_validator(mode="after")
    def update_timestamp_on_change(self) -> "OperationMetadata":
        """Automatically update updated_at when any field changes."""
        self.updated_at = datetime.datetime.now(datetime.UTC)
        return self
