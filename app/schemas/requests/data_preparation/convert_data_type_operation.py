"""
Convert data type operation schema for data preparation.

This module defines the schema for converting the data type of columns
in a dataset. Data type conversion is essential for ensuring that columns
have the correct type for ML algorithms, which often require specific
data types (e.g., numerical features must be numeric, categorical features
must be strings or integers).

The operation supports conversion to datetime, categorical, numerical,
and boolean types. A conversion map defines which source types are valid
for each target type, ensuring type safety and preventing invalid
conversions that could lead to data loss or errors.
"""

import datetime

from pydantic import Field

from app.schemas.common import BaseOperation, ColumnType, OperationType
from app.schemas.common.base import DataPreparationType

DATA_TYPES_CONVERSION_MAP = {
    ColumnType.DATETIME: str,
    ColumnType.CATEGORICAL: str | bool | float | int | datetime.datetime,
    ColumnType.NUMERICAL: str | bool | float | int | datetime.datetime,
    ColumnType.BOOLEAN: str | bool | float | int | datetime.datetime,
}


class ConvertDataTypeOperation(BaseOperation):
    """
    Operation to convert data type.

    Defines column name and target type for conversion operations.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.CONVERT_DATA_TYPE_OPERATION,
        description="Data preparation sub-operation type",
    )
    column_name: str = Field(..., description="Column to convert data type of")
    data_type: ColumnType = Field(..., description="Data type to convert to")

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
                    "column_name": "signup_date",
                    "data_type": "datetime",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
