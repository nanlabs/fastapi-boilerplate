"""Project API schemas."""

import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Schema for project base."""

    name: str = Field(..., description="Project name", min_length=1, max_length=255)
    description: str | None = Field(None, description="Project description", max_length=1000)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Customer Churn Prediction",
                "description": "ML project to predict customer churn using historical data",
            }
        }
    )

    # pylint: enable=duplicate-code


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = Field(None, description="Project name", min_length=1, max_length=255)
    description: str | None = Field(None, description="Project description", max_length=1000)

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Customer Churn Prediction v2",
                "description": "Updated ML project with improved features",
            }
        }
    )

    # pylint: enable=duplicate-code


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: int = Field(..., description="Project ID")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")
    experiments_count: int = Field(default=0, description="Number of experiments")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Customer Churn Prediction",
                "description": "ML project to predict customer churn using historical data",
                "created_at": "2025-01-20T10:30:00.000000",
                "updated_at": "2025-01-20T10:30:00.000000",
                "experiments_count": 5,
            }
        },
    )

    # pylint: enable=duplicate-code
