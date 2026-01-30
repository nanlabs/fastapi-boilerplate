"""
Base operation schemas for ML workflow requests.

This module re-exports common schemas for convenience and defines
request-specific operation schemas.
"""

from app.schemas.common import BaseOperation
from app.schemas.requests.data_enrichment import DataEnrichmentOperation
from app.schemas.requests.data_preparation import (
    DATA_TYPES_CONVERSION_MAP,
    BinningOperation,
    BinningStrategy,
    ConvertDataTypeOperation,
    DisableColumnsOperation,
    DuplicateColumnsOperation,
    DuplicateColumnsStrategy,
    EnableColumnsOperation,
    FeatureOperation,
    FeatureOperationsStrategy,
    HandleColumnMissingOperation,
    HandleColumnMissingStrategy,
    HandleInfiniteOperation,
    HandleInfiniteStrategy,
    HandleRowMissingOperation,
    HandleRowMissingStrategy,
    ValidDataTypes,
)
from app.schemas.requests.get_results import GetResultsOperation
from app.schemas.requests.load_dataset import LoadDatasetOperation
from app.schemas.requests.select_model import (
    LassoLogisticRegressionModelParameters,
    LinearRegressionModelParameters,
    ModelType,
    SelectModelOperation,
)
from app.schemas.requests.split import SplitMethod, SplitOperation
from app.schemas.requests.train_and_test_model import TrainAndTestModelOperation

# pylint: disable=duplicate-code
__all__ = [
    "BaseOperation",
    "DataEnrichmentOperation",
    "DATA_TYPES_CONVERSION_MAP",
    "BinningOperation",
    "BinningStrategy",
    "ConvertDataTypeOperation",
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
    "GetResultsOperation",
    "LassoLogisticRegressionModelParameters",
    "LinearRegressionModelParameters",
    "LoadDatasetOperation",
    "ModelType",
    "SelectModelOperation",
    "SplitMethod",
    "SplitOperation",
    "TrainAndTestModelOperation",
    "ValidDataTypes",
]
# pylint: enable=duplicate-code
