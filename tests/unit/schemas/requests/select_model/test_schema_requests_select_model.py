"""Coverage tests for select model request schemas."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from app.schemas.common import OperationMetadata
from app.schemas.requests import select_model as select_model_schemas
from app.schemas.requests.select_model.select_model_operation import (
    LassoLogisticRegressionModelParameters,
    LinearRegressionModelParameters,
    ModelType,
    SelectModelOperation,
)


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_select_model_exports() -> None:
    """Expose select model schemas in package exports."""
    assert "ModelType" in select_model_schemas.__all__
    assert select_model_schemas.ModelType is ModelType
    assert "LinearRegressionModelParameters" in select_model_schemas.__all__
    assert "LassoLogisticRegressionModelParameters" in select_model_schemas.__all__
    assert "SelectModelOperation" in select_model_schemas.__all__
    assert select_model_schemas.SelectModelOperation is SelectModelOperation


def test_select_model_operation_linear_regression() -> None:
    """Parse parameters for linear regression model."""
    operation = SelectModelOperation(
        metadata=build_metadata(),
        model_type=ModelType.LINEAR_REGRESSION,
        model_parameters=LinearRegressionModelParameters(bias=True, tolerance=0.001),
    )
    payload = operation.model_dump()
    assert payload["model_type"] is ModelType.LINEAR_REGRESSION
    assert cast(dict, payload["model_parameters"])["tolerance"] == 0.001


def test_select_model_operation_lasso_logistic() -> None:
    """Parse parameters for lasso logistic regression model."""
    operation = SelectModelOperation(
        metadata=build_metadata(),
        model_type=ModelType.LASSO_LOGISTIC_REGRESSION,
        model_parameters=LassoLogisticRegressionModelParameters(
            bias=True,
            tolerance=0.01,
            max_iter=500,
            c=1.0,
        ),
    )
    payload = operation.model_dump()
    assert payload["model_type"] is ModelType.LASSO_LOGISTIC_REGRESSION
    assert cast(dict, payload["model_parameters"])["max_iter"] == 500
