"""
Handle column missing values operation schema for data preparation.

This module defines the schema for operations that handle missing values
(NaN, None, null) in specific columns. Missing values are common in
real-world datasets and must be addressed before model training.

The operation supports multiple strategies: dropping rows with missing
values, replacing with statistical measures (mean, median, mode), replacing
with zero, or replacing with a custom value. The choice of strategy depends
on the data distribution and the importance of preserving information in
the column.
"""

from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import BaseOperation, OperationType
from app.schemas.common.base import DataPreparationType
from app.schemas.requests.data_preparation.types import ValidDataTypes


class HandleColumnMissingStrategy(str, Enum):
    """
    Strategies for handling missing values in columns.

    Defines supported approaches for imputing or dropping values.
    """

    DROP = "drop"
    REPLACE_WITH_MEAN = "replace_with_mean"
    REPLACE_WITH_MEDIAN = "replace_with_median"
    REPLACE_WITH_MODE = "replace_with_mode"
    REPLACE_WITH_ZERO = "replace_with_zero"
    REPLACE_WITH_VALUE = "replace_with_value"


class HandleColumnMissingOperation(BaseOperation):
    """
    Operation to handle missing values.

    Specifies strategy and optional replacement values for a column.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.HANDLE_COLUMN_MISSING_OPERATION,
        description="Data preparation sub-operation type",
    )
    strategy: HandleColumnMissingStrategy = Field(
        ..., description="Strategy for handling missing values"
    )
    column_name: str = Field(..., description="Field to replace missing values with")
    value: ValidDataTypes | None = Field(None, description="Value to replace missing values with")

    # pylint: disable=duplicate-code
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metadata": {
                        "model_id": "11111111-1111-1111-1111-111111111111",
                        "operation_id": "22222222-2222-2222-2222-222222222222",
                        "status": "pending",
                    },
                    "operation_type": "data_preparation",
                    "strategy": "replace_with_mean",
                    "column_name": "annual_income",
                },
                {
                    "metadata": {
                        "model_id": "11111111-1111-1111-1111-111111111111",
                        "operation_id": "33333333-3333-3333-3333-333333333333",
                        "status": "pending",
                    },
                    "operation_type": "data_preparation",
                    "strategy": "replace_with_value",
                    "column_name": "occupation",
                    "value": "unknown",
                },
            ]
        }
    }
    # pylint: enable=duplicate-code

    @model_validator(mode="after")
    def validate_replace_with_value(self) -> "HandleColumnMissingOperation":
        """Validate that value is required when strategy is replace_with_value."""
        if self.strategy == HandleColumnMissingStrategy.REPLACE_WITH_VALUE and self.value is None:
            raise ValueError("Value is required when strategy is replace_with_value")
        return self

    @model_validator(mode="after")
    def validate_value(self) -> "HandleColumnMissingOperation":
        """Validate that value is invalid when strategy is not replace_with_value."""
        if (
            self.strategy != HandleColumnMissingStrategy.REPLACE_WITH_VALUE
            and self.value is not None
        ):
            raise ValueError("Value is invalid when strategy is not replace_with_value")
        return self
