"""Model type API schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common.base import ModelTypeStatus


class ModelTypeResponse(BaseModel):
    """Schema for model type response.

    Represents a category of analytical models with rich metadata,
    such as "Credit Models", "Fraud Models", etc.
    """

    id: int = Field(..., description="Model type ID")
    name: str = Field(..., description="Model type name")
    description: str | None = Field(default=None, description="Model type description")
    enabled: bool = Field(..., description="Whether the model type is enabled")
    status: ModelTypeStatus = Field(..., description="Status of the model type")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Credit Models",
                "description": "Credit risk origination models",
                "enabled": True,
                "status": ModelTypeStatus.AVAILABLE.value,
            }
        },
    )
    # pylint: enable=duplicate-code
