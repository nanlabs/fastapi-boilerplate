"""
Split operation schema.

This module defines the schema for train/test split operations.
"""

from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import BaseOperation, OperationType


class SplitMethod(str, Enum):
    """
    Methods for train/test split.

    Defines the supported strategies for splitting datasets.
    """

    MANUAL_PERCENTAGE = "manual_percentage"


class SplitOperation(BaseOperation):
    """
    Operation to split dataset into train and test sets.

    Defines split parameters including target column and split ratio.
    """

    operation_type: OperationType = Field(
        default=OperationType.TRAIN_TEST_SPLIT, description="Operation type"
    )
    target_column: str = Field(..., description="Target column for the split")
    method: SplitMethod = Field(..., description="Method to use for splitting")
    percentage: float | None = Field(
        None, description="Percentage of dataset to include in train split", ge=0.0, le=100.0
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
                    "operation_type": "train_test_split",
                    "target_column": "churn",
                    "method": "manual_percentage",
                    "percentage": 80.0,
                }
            ]
        }
    }
    # pylint: enable=duplicate-code

    @model_validator(mode="after")
    def validate_percentage(self) -> "SplitOperation":
        """Validate that percentage is required when method is manual_percentage."""
        if self.method == SplitMethod.MANUAL_PERCENTAGE and self.percentage is None:
            raise ValueError("Percentage is required when method is manual_percentage")
        return self
