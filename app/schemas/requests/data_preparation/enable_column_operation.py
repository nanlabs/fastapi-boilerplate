"""
Enable column operation schema for data preparation.

This module defines the schema for enabling previously disabled columns
in a dataset. Columns can be disabled to exclude them from model training
or feature engineering, and this operation allows re-enabling them when
needed.

This is a simple operation that takes a column name and marks it as
active/visible in the dataset, making it available for subsequent
operations and model training.
"""

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType
from app.schemas.common.base import DataPreparationType


class EnableColumnsOperation(BaseOperation):
    """
    Operation to enable columns.

    Marks a previously disabled column as available for processing.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.ENABLE_COLUMN_OPERATION,
        description="Data preparation sub-operation type",
    )
    column_name: str = Field(..., description="Column to enable")

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
