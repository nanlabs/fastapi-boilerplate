"""
Select model operation schema.

This module defines the schema for model selection operations in ML workflows.
It includes parameter schemas for different model types (linear regression,
lasso logistic regression) and the main operation schema for selecting and
configuring models for training.
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import BaseOperation, OperationType


class ModelType(str, Enum):
    """
    Types of models available for selection.

    Defines the supported model identifiers for selection requests.
    """

    LINEAR_REGRESSION = "linear_regression"
    LASSO_LOGISTIC_REGRESSION = "lasso_logistic_regression"


class LinearRegressionModelParameters(BaseModel):
    """
    Parameters for linear regression model configuration.

    This schema defines the configuration parameters required to initialize
    and configure a linear regression model, including bias handling and
    tolerance settings for convergence.
    """

    bias: bool = Field(..., description="Whether to fit the intercept for the model")
    tolerance: float = Field(..., description="Tolerance for the model", ge=0.0, le=1.0)


class LassoLogisticRegressionModelParameters(BaseModel):
    """
    Parameters for lasso logistic regression model configuration.

    This schema defines the configuration parameters required to initialize
    and configure a lasso logistic regression model, including regularization
    strength, iteration limits, and convergence tolerance settings.
    """

    bias: bool = Field(..., description="Whether to fit the intercept for the model")
    tolerance: float = Field(..., description="Tolerance for the model", ge=0.0, le=1.0)
    max_iter: int = Field(..., description="Maximum number of iterations for the model")
    inverse_regularization_strength: float = Field(
        ...,
        alias="c",
        description="Inverse of regularization strength for the model",
        ge=0.0,
    )


AvailableParameters = LinearRegressionModelParameters | LassoLogisticRegressionModelParameters


class SelectModelOperation(BaseOperation):
    """
    Operation to select and configure a machine learning model.

    This operation allows selecting a model type and providing its configuration
    parameters. The model type determines which parameter schema should be used,
    and the model_parameters field contains the specific configuration for the
    selected model type.
    """

    operation_type: OperationType = Field(
        default=OperationType.SELECT_MODEL, description="Operation type"
    )
    model_type: ModelType = Field(..., description="Type of model to select")
    model_parameters: AvailableParameters = Field(..., description="Parameters for the model")

    # pylint: disable=duplicate-code
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metadata": {
                        "model_id": "11111111-1111-1111-1111-111111111111",
                        "operation_id": "22222222-2222-2222-2222-222222222222",
                        "status": "pending",
                    },
                    "operation_type": "select_model",
                    "model_type": "linear_regression",
                    "model_parameters": {"bias": True, "tolerance": 0.001},
                },
                {
                    "metadata": {
                        "model_id": "11111111-1111-1111-1111-111111111111",
                        "operation_id": "33333333-3333-3333-3333-333333333333",
                        "status": "pending",
                    },
                    "operation_type": "select_model",
                    "model_type": "lasso_logistic_regression",
                    "model_parameters": {
                        "bias": True,
                        "tolerance": 0.01,
                        "max_iter": 500,
                        "c": 1.0,
                    },
                },
            ]
        }
    }
    # pylint: enable=duplicate-code
