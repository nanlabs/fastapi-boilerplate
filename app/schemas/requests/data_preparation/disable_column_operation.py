"""
Disable column operation schema for data preparation.

This module defines the schema for disabling columns in a dataset.
Disabling a column excludes it from model training and feature engineering
operations without removing it from the dataset entirely.

This operation is useful for temporarily excluding columns that are not
relevant for a specific model or experiment, such as ID columns, metadata
fields, or columns that cause issues in the ML pipeline. Disabled columns
can be re-enabled later if needed.
"""

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType
from app.schemas.common.base import DataPreparationType


class DisableColumnsOperation(BaseOperation):
    """
    Operation to disable columns.

    Marks a column as excluded from training and feature operations.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.DISABLE_COLUMN_OPERATION,
        description="Data preparation sub-operation type",
    )
    column_name: str = Field(..., description="Column to disable")

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
                    "column_name": "customer_id",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
