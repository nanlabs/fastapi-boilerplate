"""Experiment type API schemas."""

from pydantic import BaseModel, ConfigDict, Field


class ExperimentTypeResponse(BaseModel):
    """Schema for experiment type response.

    Represents a fundamental category of machine learning experiments,
    such as "classification" or "regression".
    """

    id: int = Field(..., description="Experiment type ID")
    name: str = Field(..., description="Experiment type name")

    # pylint: disable=duplicate-code
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "classification",
            }
        },
    )
    # pylint: enable=duplicate-code
