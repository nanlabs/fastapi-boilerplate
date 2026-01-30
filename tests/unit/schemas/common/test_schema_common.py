"""Coverage tests for common schema modules."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from app.schemas import common as common_schemas
from app.schemas.common import BaseOperation, OperationMetadata, OperationType, Status


def test_common_exports() -> None:
    """Expose common schemas in package exports."""
    assert "BaseOperation" in common_schemas.__all__
    assert common_schemas.BaseOperation is BaseOperation
    assert common_schemas.OperationType is OperationType
    assert common_schemas.Status is Status


def test_operation_metadata_updates_timestamp() -> None:
    """Update timestamps when metadata changes."""
    model_id = UUID("11111111-1111-1111-1111-111111111111")
    metadata = OperationMetadata(model_id=model_id)
    updated = metadata.model_copy(update={"status": Status.COMPLETED})
    assert updated.updated_at >= metadata.updated_at
    assert updated.updated_at >= updated.created_at


def test_base_operation_initialization() -> None:
    """Initialize base operation with metadata."""
    model_id = UUID("11111111-1111-1111-1111-111111111111")
    metadata = OperationMetadata(model_id=model_id)
    operation = BaseOperation(metadata=metadata, operation_type=OperationType.LOAD_DATASET)
    payload = operation.model_dump()
    assert payload["operation_type"] is OperationType.LOAD_DATASET
    assert cast(dict, payload["metadata"])["model_id"] == model_id
