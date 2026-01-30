"""Coverage tests for train and test request schemas."""

from __future__ import annotations

from uuid import UUID

from app.schemas.common import OperationMetadata, OperationType
from app.schemas.requests import train_and_test_model as train_and_test_model_schemas
from app.schemas.requests.train_and_test_model.train_and_test_model_operation import (
    TrainAndTestModelOperation,
)


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_train_and_test_exports() -> None:
    """Expose train and test schemas in package exports."""
    assert "TrainAndTestModelOperation" in train_and_test_model_schemas.__all__
    assert train_and_test_model_schemas.TrainAndTestModelOperation is TrainAndTestModelOperation


def test_train_and_test_operation() -> None:
    """Create train and test operation."""
    operation = TrainAndTestModelOperation(metadata=build_metadata())
    assert operation.operation_type is OperationType.TRAIN_AND_TEST_MODEL
