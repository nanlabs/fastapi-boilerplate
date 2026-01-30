"""Coverage tests for data preparation request schemas."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

import pytest

from app.schemas import requests as request_schemas
from app.schemas.common import BaseOperation, ColumnType, OperationMetadata, OperationType
from app.schemas.requests import data_preparation as data_preparation_schemas
from app.schemas.requests.data_preparation import (
    BinningOperation,
    BinningStrategy,
    ConvertDataTypeOperation,
    DisableColumnsOperation,
    DuplicateColumnsOperation,
    DuplicateColumnsStrategy,
    EnableColumnsOperation,
    FeatureOperation,
    FeatureOperationsStrategy,
    HandleColumnMissingOperation,
    HandleColumnMissingStrategy,
    HandleInfiniteOperation,
    HandleInfiniteStrategy,
    HandleRowMissingOperation,
    HandleRowMissingStrategy,
)


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_disable_enable_duplicate_operations() -> None:
    """Create column enable/disable/duplicate operations."""
    metadata = build_metadata()
    disabled = DisableColumnsOperation(metadata=metadata, column_name="customer_id")
    enabled = EnableColumnsOperation(metadata=metadata, column_name="customer_id")
    duplicated = DuplicateColumnsOperation(
        metadata=metadata,
        column_name="status",
        strategy=DuplicateColumnsStrategy.NEWEST_VALUE,
        date_column="updated_at",
    )
    assert disabled.operation_type is OperationType.DATA_PREPARATION
    assert enabled.column_name == "customer_id"
    assert duplicated.strategy is DuplicateColumnsStrategy.NEWEST_VALUE


def test_data_preparation_exports() -> None:
    """Expose data preparation schemas in package exports."""
    assert "BaseOperation" in request_schemas.__all__
    assert request_schemas.BaseOperation is BaseOperation
    assert "ConvertDataTypeOperation" in data_preparation_schemas.__all__
    assert data_preparation_schemas.ConvertDataTypeOperation is ConvertDataTypeOperation
    assert "DATA_TYPES_CONVERSION_MAP" in data_preparation_schemas.__all__
    assert "ValidDataTypes" in data_preparation_schemas.__all__
    assert "ConvertDataTypeOperation" in request_schemas.__all__


def test_convert_data_type_operation() -> None:
    """Create convert data type operation."""
    operation = ConvertDataTypeOperation(
        metadata=build_metadata(), column_name="signup_date", data_type=ColumnType.DATETIME
    )
    assert operation.data_type is ColumnType.DATETIME


def test_feature_operation() -> None:
    """Create feature operation with defaults."""
    operation = FeatureOperation(
        column_name_a="total_spend",
        column_name_b="total_orders",
        strategy=FeatureOperationsStrategy.DIVISION,
    )
    assert operation.operation_type is OperationType.DATA_PREPARATION


def test_binning_operation_validation() -> None:
    """Validate binning rules for manual strategy."""
    operation = BinningOperation(
        column_name_a="age",
        column_name_b="age",
        strategy=FeatureOperationsStrategy.SUM,
        binning_strategy=BinningStrategy.MANUAL,
        bins=4,
        bin_edges=[25, 40, 60],
    )
    assert operation.bins == 4

    with pytest.raises(ValueError, match="bin_edges is required"):
        BinningOperation(
            column_name_a="age",
            column_name_b="age",
            strategy=FeatureOperationsStrategy.SUM,
            binning_strategy=BinningStrategy.MANUAL,
            bins=4,
        )

    with pytest.raises(ValueError, match="bin_edges must have the same number"):
        BinningOperation(
            column_name_a="age",
            column_name_b="age",
            strategy=FeatureOperationsStrategy.SUM,
            binning_strategy=BinningStrategy.MANUAL,
            bins=4,
            bin_edges=[10],
        )

    constructed = cast(Any, BinningOperation).model_construct(
        column_name_a="age",
        column_name_b="age",
        strategy=FeatureOperationsStrategy.SUM,
        binning_strategy=BinningStrategy.MANUAL,
        bins=None,
        bin_edges=[25, 40, 60],
    )
    with pytest.raises(ValueError, match="bins is required"):
        cast(Any, BinningOperation).validate_bins(constructed)


def test_handle_column_missing_validation() -> None:
    """Validate missing column handling strategies."""
    operation = HandleColumnMissingOperation(
        metadata=build_metadata(),
        strategy=HandleColumnMissingStrategy.REPLACE_WITH_MEAN,
        column_name="annual_income",
    )
    assert operation.strategy is HandleColumnMissingStrategy.REPLACE_WITH_MEAN

    with pytest.raises(ValueError, match="Value is required"):
        HandleColumnMissingOperation(
            metadata=build_metadata(),
            strategy=HandleColumnMissingStrategy.REPLACE_WITH_VALUE,
            column_name="occupation",
        )

    with pytest.raises(ValueError, match="Value is invalid"):
        HandleColumnMissingOperation(
            metadata=build_metadata(),
            strategy=HandleColumnMissingStrategy.REPLACE_WITH_MEAN,
            column_name="occupation",
            value="unknown",
        )


def test_handle_infinite_validation() -> None:
    """Validate infinite value handling strategies."""
    with pytest.raises(ValueError, match="Value is required"):
        HandleInfiniteOperation(
            metadata=build_metadata(),
            column_name="income",
            strategy=HandleInfiniteStrategy.REPLACE_WITH_VALUE,
        )

    with pytest.raises(ValueError, match="Value is invalid"):
        HandleInfiniteOperation(
            metadata=build_metadata(),
            column_name="income",
            strategy=HandleInfiniteStrategy.CLIP,
            value=0.0,
        )

    with pytest.raises(ValueError, match="min_value and max_value are required"):
        HandleInfiniteOperation(
            metadata=build_metadata(),
            column_name="income",
            strategy=HandleInfiniteStrategy.REPLACE_WITH_RANGE,
        )

    with pytest.raises(ValueError, match="min_value is invalid"):
        HandleInfiniteOperation(
            metadata=build_metadata(),
            column_name="income",
            strategy=HandleInfiniteStrategy.DROP,
            min_value=-1.0,
        )

    operation = HandleInfiniteOperation(
        metadata=build_metadata(),
        column_name="income",
        strategy=HandleInfiniteStrategy.REPLACE_WITH_RANGE,
        min_value=-100.0,
        max_value=100.0,
    )
    assert operation.min_value == -100.0


def test_handle_row_missing_validation() -> None:
    """Validate row missing handling strategies."""
    with pytest.raises(ValueError, match="minimum_acceptable_value is required"):
        HandleRowMissingOperation(
            metadata=build_metadata(),
            strategy=HandleRowMissingStrategy.MINIMUM_ACCEPTABLE_VALUE,
        )

    with pytest.raises(ValueError, match="minimum_acceptable_value is invalid"):
        HandleRowMissingOperation(
            metadata=build_metadata(),
            strategy=HandleRowMissingStrategy.REQUIRED_COLUMNS,
            minimum_acceptable_value=50.0,
        )

    with pytest.raises(ValueError, match="required_columns is required"):
        HandleRowMissingOperation(
            metadata=build_metadata(),
            strategy=HandleRowMissingStrategy.REQUIRED_COLUMNS,
        )

    with pytest.raises(ValueError, match="columns is invalid"):
        HandleRowMissingOperation(
            metadata=build_metadata(),
            strategy=HandleRowMissingStrategy.MINIMUM_ACCEPTABLE_VALUE,
            minimum_acceptable_value=90.0,
            columns=["age"],
        )

    with pytest.raises(ValueError, match="columns must be a list"):
        constructed = cast(Any, HandleRowMissingOperation).model_construct(
            metadata=build_metadata(),
            strategy=HandleRowMissingStrategy.REQUIRED_COLUMNS,
            columns="age",
        )
        cast(Any, HandleRowMissingOperation).validate_columns_type(constructed)

    operation = HandleRowMissingOperation(
        metadata=build_metadata(),
        strategy=HandleRowMissingStrategy.REQUIRED_COLUMNS,
        columns=["age", "income"],
    )
    assert operation.columns == ["age", "income"]
