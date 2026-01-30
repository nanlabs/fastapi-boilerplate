"""
Handle row missing values operation schema for data preparation.

This module defines the schema for operations that handle missing values
at the row level. Unlike column-level missing value handling, this
operation evaluates entire rows and can drop or filter rows based on
missing value criteria.

The operation supports two strategies: minimum acceptable value (drops
rows where values fall below a threshold) and required columns (drops
rows where specific required columns have missing values). This is useful
for data quality control and ensuring that training data meets minimum
completeness requirements.
"""

from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import BaseOperation, OperationType
from app.schemas.common.base import DataPreparationType


class HandleRowMissingStrategy(str, Enum):
    """
    Strategies for handling missing values in rows.

    Defines supported approaches for row-level missing data rules.
    """

    MINIMUM_ACCEPTABLE_VALUE = "minimum_acceptable_value"
    REQUIRED_COLUMNS = "required_columns"


class HandleRowMissingOperation(BaseOperation):
    """
    Operation to handle missing values in rows.

    Specifies row-level missing value strategy and validation parameters.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.HANDLE_ROW_MISSING_OPERATION,
        description="Data preparation sub-operation type",
    )
    strategy: HandleRowMissingStrategy = Field(
        ..., description="Strategy for handling missing values in rows"
    )
    minimum_acceptable_value: float | None = Field(
        None, description="Minimum acceptable value for missing values", ge=0.0, le=100.0
    )
    columns: list[str] | None = Field(None, description="Columns to check for missing values")

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
                    "strategy": "minimum_acceptable_value",
                    "minimum_acceptable_value": 95.0,
                },
                {
                    "metadata": {
                        "model_id": "11111111-1111-1111-1111-111111111111",
                        "operation_id": "33333333-3333-3333-3333-333333333333",
                        "status": "pending",
                    },
                    "operation_type": "data_preparation",
                    "strategy": "required_columns",
                    "columns": ["age", "income"],
                },
            ]
        }
    }
    # pylint: enable=duplicate-code

    @model_validator(mode="after")
    def validate_minimum_acceptable_value(self) -> "HandleRowMissingOperation":
        """Validate minimum_acceptable_value is required for strategy."""
        if (
            self.strategy == HandleRowMissingStrategy.MINIMUM_ACCEPTABLE_VALUE
            and self.minimum_acceptable_value is None
        ):
            raise ValueError(
                "minimum_acceptable_value is required when strategy is minimum_acceptable_value"
            )
        return self

    @model_validator(mode="after")
    def validate_minimum_value_usage(self) -> "HandleRowMissingOperation":
        """Validate minimum_acceptable_value is invalid when strategy is required_columns."""
        if (
            self.strategy != HandleRowMissingStrategy.MINIMUM_ACCEPTABLE_VALUE
            and self.minimum_acceptable_value is not None
        ):
            raise ValueError(
                "minimum_acceptable_value is invalid when strategy is required_columns"
            )
        return self

    @model_validator(mode="after")
    def validate_required_columns(self) -> "HandleRowMissingOperation":
        """Validate that required_columns is required when strategy is required_columns."""
        if self.strategy == HandleRowMissingStrategy.REQUIRED_COLUMNS and self.columns is None:
            raise ValueError("required_columns is required when strategy is required_columns")
        return self

    @model_validator(mode="after")
    def validate_columns(self) -> "HandleRowMissingOperation":
        """Validate that columns is invalid when strategy is not required_columns."""
        if self.strategy != HandleRowMissingStrategy.REQUIRED_COLUMNS and self.columns is not None:
            raise ValueError("columns is invalid when strategy is not required_columns")
        return self

    @model_validator(mode="after")
    def validate_columns_type(self) -> "HandleRowMissingOperation":
        """Validate that columns is a list of strings."""
        if self.columns is not None and not isinstance(self.columns, list):
            raise ValueError("columns must be a list of strings")
        return self
