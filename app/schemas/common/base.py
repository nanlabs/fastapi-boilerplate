"""
Base schemas for ML operations.

This module defines the base operation class and operation type enum
that all ML operation requests inherit from.
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common.metadata import OperationMetadata


class DataPreparationType(str, Enum):
    """
    Types of data preparation operations.

    Enumerates supported workflow operations for data preparation request handling.
    """

    HANDLE_COLUMN_MISSING_OPERATION = "column_missing"
    HANDLE_ROW_MISSING_OPERATION = "row_missing"
    HANDLE_INFINITE_OPERATION = "infinite"
    CONVERT_DATA_TYPE_OPERATION = "convert_data_type"
    ENABLE_COLUMN_OPERATION = "enable_column"
    DISABLE_COLUMN_OPERATION = "disable_column"
    DUPLICATE_COLUMNS_OPERATION = "duplicates"
    FEATURE_OPERATION = "feature_operation"
    BINNING_OPERATION = "binning"


class OperationType(str, Enum):
    """
    Types of ML operations.

    Enumerates supported workflow operations for ML request handling.
    """

    LOAD_DATASET = "load_dataset"
    DATA_PREPARATION = "data_preparation"
    DATA_ENRICHMENT = "data_enrichment"
    TRAIN_TEST_SPLIT = "train_test_split"
    SELECT_MODEL = "select_model"
    TRAIN_AND_TEST_MODEL = "train_and_test_model"
    GET_MODEL = "get_model"
    GET_METRICS = "get_metrics"
    GET_RESULTS = "get_results"
    SAMPLE_DATASET = "sample_dataset"
    PROFILE_DATASET = "profile_dataset"


class BaseOperation(BaseModel):
    """
    Base class for all ML operation requests.

    Provides common metadata and operation identifiers for ML requests.
    """

    metadata: OperationMetadata = Field(..., description="Operation metadata")
    operation_type: OperationType = Field(..., description="Type of operation")


class ColumnType(str, Enum):
    """
    Types of columns.

    Defines the supported logical types for dataset columns.
    """

    DATETIME = "datetime"
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    BOOLEAN = "boolean"


class ExperimentStatus(str, Enum):
    """Status of an experiment.

    Represents the lifecycle stages of a machine learning experiment,
    from initial creation through execution to final publication or failure.
    """

    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    PUBLISHED = "published"
    FAILED = "failed"


class ModelTypeStatus(str, Enum):
    """Status of a model type.

    Represents the availability and access control status of model types
    in the system. Determines how users can access different model categories.
    """

    AVAILABLE = "available"
    REQUEST_ACCESS = "request_access"
    COMING_SOON = "coming_soon"
