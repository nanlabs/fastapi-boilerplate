"""
Data preparation operation schemas.

This module defines Pydantic schemas for all data preparation operations
that can be performed on datasets in the ML workflow.

Each operation schema inherits from BaseOperation and includes validation
logic specific to its operation type. The schemas ensure type safety and
data consistency when operations are sent from the FastAPI backend to the
ML component for execution.
"""

from app.schemas.requests.data_preparation.binning_operation import (
    BinningOperation,
    BinningStrategy,
)
from app.schemas.requests.data_preparation.convert_data_type_operation import (
    DATA_TYPES_CONVERSION_MAP,
    ConvertDataTypeOperation,
)
from app.schemas.requests.data_preparation.disable_column_operation import DisableColumnsOperation
from app.schemas.requests.data_preparation.duplicate_columns_operation import (
    DuplicateColumnsOperation,
    DuplicateColumnsStrategy,
)
from app.schemas.requests.data_preparation.enable_column_operation import EnableColumnsOperation
from app.schemas.requests.data_preparation.feature_operation import (
    FeatureOperation,
    FeatureOperationsStrategy,
)
from app.schemas.requests.data_preparation.handle_column_missing_operation import (
    HandleColumnMissingOperation,
    HandleColumnMissingStrategy,
)
from app.schemas.requests.data_preparation.handle_infinite_missing_operation import (
    HandleInfiniteOperation,
    HandleInfiniteStrategy,
)
from app.schemas.requests.data_preparation.handle_row_missing_operation import (
    HandleRowMissingOperation,
    HandleRowMissingStrategy,
)
from app.schemas.requests.data_preparation.types import ValidDataTypes

# pylint: disable=duplicate-code
__all__ = [
    "ValidDataTypes",
    "BinningOperation",
    "BinningStrategy",
    "ConvertDataTypeOperation",
    "DATA_TYPES_CONVERSION_MAP",
    "DisableColumnsOperation",
    "DuplicateColumnsOperation",
    "DuplicateColumnsStrategy",
    "EnableColumnsOperation",
    "FeatureOperation",
    "FeatureOperationsStrategy",
    "HandleColumnMissingOperation",
    "HandleColumnMissingStrategy",
    "HandleInfiniteOperation",
    "HandleInfiniteStrategy",
    "HandleRowMissingOperation",
    "HandleRowMissingStrategy",
]
# pylint: enable=duplicate-code
