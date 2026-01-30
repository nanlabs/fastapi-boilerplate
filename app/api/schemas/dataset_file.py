"""Dataset file API schemas."""

import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.api import PaginationParams


class DatasetFileBase(BaseModel):
    """Schema for dataset file base."""

    name: str = Field(..., description="Dataset file name", min_length=1, max_length=255)
    path: str = Field(..., description="Full dataset file path", min_length=1, max_length=1000)


class DatasetFileCreate(BaseModel):
    """Schema for creating a new dataset file."""

    path: str = Field(..., description="Full dataset file path", min_length=1, max_length=1000)

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "/path/to/data.csv",
            }
        }
    )

    # pylint: enable=duplicate-code


class DatasetFileUpdate(BaseModel):
    """Schema for updating a dataset file."""

    path: str | None = Field(
        None, description="Full dataset file path", min_length=1, max_length=1000
    )

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "/path/to/data_updated.csv",
            }
        }
    )

    # pylint: enable=duplicate-code


class DatasetFileResponse(DatasetFileBase):
    """Schema for dataset file response."""

    id: int = Field(..., description="Dataset file ID")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")
    columns_size: int = Field(..., description="Number of columns in the CSV file")
    rows_size: int = Field(..., description="Number of rows in the CSV file")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "data.csv",
                "path": "/path/to/data.csv",
                "created_at": "2025-01-20T10:30:00.000000",
                "updated_at": "2025-01-20T10:30:00.000000",
                "columns_size": 3,
                "rows_size": 1000,
            }
        },
    )

    # pylint: enable=duplicate-code


class DatasetFileContentResponse(BaseModel):
    """Schema for dataset file content response."""

    columns: list[str] = Field(..., description="Column names from CSV header")
    rows: list[list[str | int | float | None]] = Field(
        ..., description="Data rows as arrays (matrix format, values in same order as columns)"
    )
    total_rows: int = Field(..., description="Total number of rows in the CSV file")
    pagination: PaginationParams = Field(..., description="Pagination parameters used")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "columns": ["id", "name", "value"],
                "rows": [
                    ["1", "Alice", "100"],
                    ["2", "Bob", "200"],
                ],
                "total_rows": 1000,
                "pagination": {"skip": 0, "limit": 100},
            }
        },
    )

    # pylint: enable=duplicate-code
