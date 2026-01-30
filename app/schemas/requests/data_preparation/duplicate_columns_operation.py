"""
Duplicate columns operation schema for data preparation.

This module defines the schema for handling duplicate columns in datasets.
When multiple columns with the same name exist, this operation allows
selecting which value to keep based on temporal information.

The operation uses a date column to determine which duplicate value is
older or newer, then applies the selected strategy to resolve the
duplication. This is particularly useful for time-series data where
the same column may appear multiple times with different timestamps.
"""

from enum import Enum

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType
from app.schemas.common.base import DataPreparationType


class DuplicateColumnsStrategy(str, Enum):
    """
    Strategies for duplicating columns.

    Defines how to resolve duplicate column values by timestamp.
    """

    OLDEST_VALUE = "oldest_value"
    NEWEST_VALUE = "newest_value"


class DuplicateColumnsOperation(BaseOperation):
    """
    Operation to duplicate columns.

    Resolves duplicated columns based on temporal selection strategy.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.DUPLICATE_COLUMNS_OPERATION,
        description="Data preparation sub-operation type",
    )

    column_name: str = Field(..., description="Column to duplicate")
    strategy: DuplicateColumnsStrategy = Field(..., description="Strategy to duplicate columns")
    date_column: str = Field(..., description="Date column to use for duplication")

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
                    "column_name": "status",
                    "strategy": "newest_value",
                    "date_column": "updated_at",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
