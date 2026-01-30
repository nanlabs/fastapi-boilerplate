"""
Binning operation schema for data preparation.

This module defines the schema for binning operations, which transform
continuous numerical columns into discrete bins or categories. Binning
is useful for feature engineering, reducing noise in data, and creating
categorical features from numerical ones.

The operation supports multiple binning strategies including manual
binning with custom edges, frequency-based binning (equal number of
samples per bin), and width-based binning (equal interval width).
"""

from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import OperationType
from app.schemas.common.base import DataPreparationType
from app.schemas.requests.data_preparation.feature_operation import FeatureOperation


class BinningStrategy(str, Enum):
    """
    Strategies for binning.

    Defines available binning approaches for numerical features.
    """

    MANUAL = "manual"
    FREQUENCY = "frequency"
    WIDTH = "width"


class BinningOperation(FeatureOperation):
    """
    Operation to bin a column.

    Specifies binning parameters and validation for feature binning.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_PREPARATION, description="Operation type"
    )
    sub_operation_type: DataPreparationType = Field(
        default=DataPreparationType.BINNING_OPERATION,
        description="Data preparation sub-operation type",
    )
    binning_strategy: BinningStrategy = Field(..., description="Strategy to bin")
    bins: int | None = Field(..., description="Number of bins", ge=2)
    bin_edges: list[float] | None = Field(default=None, description="Bin edges", min_length=1)

    # pylint: disable=duplicate-code
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operation_type": "data_preparation",
                    "column_name_a": "age",
                    "column_name_b": "age",
                    "strategy": "sum",
                    "binning_strategy": "manual",
                    "bins": 4,
                    "bin_edges": [25.0, 40.0, 60.0],
                },
                {
                    "operation_type": "data_preparation",
                    "column_name_a": "salary",
                    "column_name_b": "salary",
                    "strategy": "sum",
                    "binning_strategy": "frequency",
                    "bins": 5,
                },
            ]
        }
    }
    # pylint: enable=duplicate-code

    @model_validator(mode="after")
    def validate_bin_edges(self) -> "BinningOperation":
        """Validate that bin_edges is required when strategy is manual."""
        if self.binning_strategy == BinningStrategy.MANUAL and self.bin_edges is None:
            raise ValueError("bin_edges is required when strategy is manual")
        if (
            self.binning_strategy == BinningStrategy.MANUAL
            and self.bins is not None
            and self.bin_edges is not None
            and len(self.bin_edges) != self.bins - 1
        ):
            raise ValueError("bin_edges must have the same number of edges as bins - 1")
        return self

    @model_validator(mode="after")
    def validate_bins(self) -> "BinningOperation":
        """Validate that bins is required when strategy is manual."""
        if self.binning_strategy == BinningStrategy.MANUAL and self.bins is None:
            raise ValueError("bins is required when strategy is manual")
        return self
