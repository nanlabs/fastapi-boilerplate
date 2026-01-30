"""Coverage tests for get results request schemas."""

from __future__ import annotations

from uuid import UUID

from app.schemas.common import OperationMetadata, OperationType
from app.schemas.requests import get_results as get_results_schemas
from app.schemas.requests.get_results.get_results_operation import GetResultsOperation


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_get_results_exports() -> None:
    """Expose get results schemas in package exports."""
    assert "GetResultsOperation" in get_results_schemas.__all__
    assert get_results_schemas.GetResultsOperation is GetResultsOperation


def test_get_results_operation() -> None:
    """Create get results operation."""
    operation = GetResultsOperation(metadata=build_metadata())
    assert operation.operation_type is OperationType.GET_RESULTS
