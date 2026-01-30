"""Coverage tests for load dataset request schemas."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from app.schemas.common import OperationMetadata, OperationType
from app.schemas.requests import load_dataset as load_dataset_schemas
from app.schemas.requests.load_dataset.load_dataset_operation import LoadDatasetOperation


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_load_dataset_exports() -> None:
    """Expose load dataset schemas in package exports."""
    assert "LoadDatasetOperation" in load_dataset_schemas.__all__
    assert load_dataset_schemas.LoadDatasetOperation is LoadDatasetOperation


def test_load_dataset_operation() -> None:
    """Create load dataset operation."""
    operation = LoadDatasetOperation(metadata=build_metadata(), path="data/sample.csv")
    assert operation.operation_type is OperationType.LOAD_DATASET
    assert cast(str, operation.model_dump()["path"]).endswith(".csv")
