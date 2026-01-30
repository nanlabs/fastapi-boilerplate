"""
Handle infinite values operation schema for data preparation.

This module defines the schema for operations that handle infinite values
(positive or negative infinity) in numerical columns. Infinite values can
occur due to division by zero, mathematical operations, or data quality
issues, and they need to be handled before model training.

The operation supports multiple strategies: dropping rows with infinite
values, clipping values to a specified range, replacing with a constant
value, or replacing with values within a specified range. Each strategy
has specific validation requirements to ensure data integrity.
"""

from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import BaseOperation, OperationType
from app.schemas.common.base import DataPreparationType
from app.schemas.requests.data_preparation.types import ValidDataTypes


class HandleInfiniteStrategy(str, Enum):
    """
    Strategies for handling infinite values.

    Defines supported approaches for filtering or replacing values.
    """

    DROP = "drop"
    CLIP = "clip"
    REPLACE_WITH_VALUE = "replace_with_value"
    REPLACE_WITH_RANGE = "replace_with_range"


class HandleInfiniteOperation(BaseOperation):
    """
    Operation to handle infinite values.

    Specifies strategy and replacement bounds for infinite values.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.HANDLE_INFINITE_OPERATION,
        description="Data preparation sub-operation type",
    )
    strategy: HandleInfiniteStrategy = Field(
        ..., description="Strategy for handling infinite values"
    )
    value: ValidDataTypes | None = Field(None, description="Value to replace infinite values with")
    min_value: ValidDataTypes | None = Field(
        None, description="Minimum value to clip infinite values to"
    )
    max_value: ValidDataTypes | None = Field(
        None, description="Maximum value to clip infinite values to"
    )

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
                    "column_name": "annual_income",
                    "strategy": "replace_with_value",
                    "value": 0.0,
                },
                {
                    "metadata": {
                        "model_id": "11111111-1111-1111-1111-111111111111",
                        "operation_id": "33333333-3333-3333-3333-333333333333",
                        "status": "pending",
                    },
                    "operation_type": "data_preparation",
                    "column_name": "occupation",
                    "strategy": "replace_with_range",
                    "min_value": -1000.0,
                    "max_value": 1000.0,
                },
            ]
        }
    }
    # pylint: enable=duplicate-code

    @model_validator(mode="after")
    def validate_replace_with_value(self) -> "HandleInfiniteOperation":
        """Validate that value is required when strategy is replace_with_value."""
        if self.strategy == HandleInfiniteStrategy.REPLACE_WITH_VALUE and self.value is None:
            raise ValueError("Value is required when strategy is replace_with_value")
        return self

    @model_validator(mode="after")
    def validate_value(self) -> "HandleInfiniteOperation":
        """Validate that value is invalid when strategy is not replace_with_value."""
        if self.strategy != HandleInfiniteStrategy.REPLACE_WITH_VALUE and self.value is not None:
            raise ValueError("Value is invalid when strategy is not replace_with_value")
        return self

    @model_validator(mode="after")
    def validate_replace_with_range(self) -> "HandleInfiniteOperation":
        """Validate min_value and max_value are required for replace_with_range."""
        if (
            self.strategy == HandleInfiniteStrategy.REPLACE_WITH_RANGE
            and self.min_value is None
            and self.max_value is None
        ):
            raise ValueError(
                "min_value and max_value are required when strategy is replace_with_range"
            )
        return self

    @model_validator(mode="after")
    def validate_min_value(self) -> "HandleInfiniteOperation":
        """Validate that min_value is invalid when strategy is not replace_with_range."""
        if self.strategy != HandleInfiniteStrategy.REPLACE_WITH_RANGE and (
            self.min_value is not None or self.max_value is not None
        ):
            raise ValueError("min_value is invalid when strategy is not replace_with_range")
        return self
