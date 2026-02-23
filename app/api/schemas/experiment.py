"""Experiment API schemas."""

import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common.base import ExperimentStatus


class ExperimentBase(BaseModel):
    """Schema for experiment base."""

    name: str = Field(..., description="Experiment name", min_length=1, max_length=255)
    description: str | None = Field(None, description="Experiment description", max_length=1000)
    project_id: int = Field(..., description="Project ID")


class ExperimentCreate(ExperimentBase):
    """Schema for creating a new experiment."""

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Baseline Analysis Run",
                "description": "Initial run to establish baseline performance metrics",
                "project_id": 1,
            }
        }
    )

    # pylint: enable=duplicate-code


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment."""

    name: str | None = Field(
        default=None, description="Experiment name", min_length=1, max_length=255
    )
    description: str | None = Field(
        default=None, description="Experiment description", max_length=1000
    )
    project_id: int | None = Field(default=None, description="Project ID")
    status: ExperimentStatus | None = Field(default=None, description="Experiment status")
    current_step: int | None = Field(default=None, description="Current step", ge=0)


class ExperimentAttachDataset(BaseModel):
    """Schema for attaching a dataset file to an experiment.

    Either provide a path to create a new dataset file, or provide
    an existing dataset_file_id to reuse an existing dataset file.
    """

    path: str | None = Field(
        None,
        description="Full dataset file path to create a new dataset file",
        min_length=1,
        max_length=1000,
    )
    dataset_file_id: int | None = Field(
        None, description="ID of an existing dataset file to attach", gt=0
    )

    @model_validator(mode="after")
    def validate_exactly_one_provided(self) -> "ExperimentAttachDataset":
        """Validate that exactly one of path or dataset_file_id is provided."""
        has_path = self.path is not None
        has_id = self.dataset_file_id is not None

        if not has_path and not has_id:
            raise ValueError("Either 'path' or 'dataset_file_id' must be provided")
        if has_path and has_id:
            raise ValueError("Cannot provide both 'path' and 'dataset_file_id'. Provide only one")
        return self

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "path": "/path/to/data.csv",
                },
                {
                    "dataset_file_id": 1,
                },
            ]
        }
    )

    # pylint: enable=duplicate-code


class ExperimentResponse(ExperimentBase):
    """Schema for experiment response."""

    id: int = Field(..., description="Experiment ID")
    status: ExperimentStatus = Field(..., description="Experiment status")
    current_step: int = Field(..., description="Current step in the experiment process")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Baseline Analysis Run",
                "description": "Initial run to establish baseline performance metrics",
                "project_id": 1,
                "status": "draft",
                "current_step": 0,
                "created_at": "2025-01-20T11:00:00.000000",
                "updated_at": "2025-01-20T11:00:00.000000",
            }
        },
    )

    # pylint: enable=duplicate-code


class ExperimentStatusesResponse(BaseModel):
    """Schema for experiment statuses response."""

    data: list[ExperimentStatus] = Field(
        ..., description="List of available experiment status values"
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"data": [status.value for status in ExperimentStatus]}}
    )
