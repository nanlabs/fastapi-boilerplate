"""
Load dataset operation schema.

This module defines the schema for loading datasets from file paths.
"""

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType


class LoadDatasetOperation(BaseOperation):
    """
    Operation to load a dataset from a file path.

    NOTE: Only clean the dataset when this operation is performed.
    """

    operation_type: OperationType = Field(
        default=OperationType.LOAD_DATASET, description="Operation type"
    )
    path: str = Field(..., description="Path to the dataset file (CSV)")

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
                    "operation_type": "load_dataset",
                    "path": "data/iris.csv",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
