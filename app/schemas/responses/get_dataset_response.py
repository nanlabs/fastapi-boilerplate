"""
Get dataset response schema.

This module defines the response schema for get dataset operations,
including dataset-specific fields.
"""

from pydantic import BaseModel, Field

from app.schemas.data.profiling import DatasetProfiling


class GetDatasetResponse(BaseModel):
    """
    Response for get dataset operation.

    Returns a sample dataset and profiling results for the request.
    """

    sample_dataset: dict[str, list] = Field(..., description="Sample of the dataset")
    profiling: DatasetProfiling = Field(..., description="Profiling of the dataset")
