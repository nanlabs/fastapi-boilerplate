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
                "name": "Customer Insights",
                "description": "Analytics project focused on customer behavior trends",
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
                "name": "Customer Insights v2",
                "description": "Updated project with refined segmentation logic",
            }
        }
    )

    # pylint: enable=duplicate-code


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: int = Field(..., description="Project ID")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Customer Insights",
                "description": "Analytics project focused on customer behavior trends",
                "created_at": "2025-01-20T10:30:00.000000",
                "updated_at": "2025-01-20T10:30:00.000000",
            }
        },
    )

    # pylint: enable=duplicate-code
