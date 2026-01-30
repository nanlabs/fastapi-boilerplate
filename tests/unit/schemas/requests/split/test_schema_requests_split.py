"""Coverage tests for split request schemas."""

from __future__ import annotations

from uuid import UUID

import pytest

from app.schemas.common import OperationMetadata
from app.schemas.requests import split as split_schemas
from app.schemas.requests.split.split_operation import SplitMethod, SplitOperation


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_split_exports() -> None:
    """Expose split schemas in package exports."""
    assert "SplitMethod" in split_schemas.__all__
    assert split_schemas.SplitMethod is SplitMethod
    assert "SplitOperation" in split_schemas.__all__
    assert split_schemas.SplitOperation is SplitOperation


def test_split_operation_requires_percentage() -> None:
    """Validate manual split requires percentage."""
    with pytest.raises(ValueError, match="Percentage is required"):
        SplitOperation(
            metadata=build_metadata(),
            target_column="churn",
            method=SplitMethod.MANUAL_PERCENTAGE,
        )

    operation = SplitOperation(
        metadata=build_metadata(),
        target_column="churn",
        method=SplitMethod.MANUAL_PERCENTAGE,
        percentage=80.0,
    )
    assert operation.percentage == 80.0
