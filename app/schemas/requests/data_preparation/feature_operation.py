"""
Feature operation schema for data preparation.

This module defines the schema for feature engineering operations that
combine two columns using arithmetic operations. These operations create
new derived features from existing columns, which can improve model
performance by capturing relationships between variables.

Supported operations include basic arithmetic: addition, subtraction,
multiplication, and division. The operation takes two column names as
input and applies the specified strategy to create a new feature.
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import OperationType
from app.schemas.common.base import DataPreparationType


class FeatureOperationsStrategy(str, Enum):
    """
    Strategies for feature operations.

    Defines arithmetic operations for feature engineering.
    """

    MULTIPLICATION = "multiplication"
    SUM = "sum"
    SUBTRACTION = "subtraction"
    DIVISION = "division"


class FeatureOperation(BaseModel):
    """
    Operation to perform feature engineering.

    Defines input columns and strategy for derived features.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.FEATURE_OPERATION,
        description="Data preparation sub-operation type",
    )
    column_name_a: str = Field(..., description="First column to apply operation to")
    column_name_b: str = Field(..., description="Second column to apply operation to")
    strategy: FeatureOperationsStrategy = Field(..., description="Strategy to apply")

    # pylint: disable=duplicate-code
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operation_type": "data_preparation",
                    "column_name_a": "total_spend",
                    "column_name_b": "total_orders",
                    "strategy": "division",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
