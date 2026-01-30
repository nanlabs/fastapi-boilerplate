"""Coverage tests for response schema modules."""

from __future__ import annotations

from typing import cast

from app.schemas import responses as response_schemas
from app.schemas.common import ColumnType
from app.schemas.data import ColumnProfile, CorrelationMatrix, DatasetProfiling
from app.schemas.responses.get_dataset_response import GetDatasetResponse


def test_response_exports() -> None:
    """Expose response schemas in package exports."""
    assert "GetDatasetResponse" in response_schemas.__all__
    assert response_schemas.GetDatasetResponse is GetDatasetResponse


def test_get_dataset_response() -> None:
    """Create get dataset response schema."""
    correlation = CorrelationMatrix(columns=["a"], matrix=[[1.0]])
    profiling = DatasetProfiling(
        total_rows=2,
        total_columns=1,
        columns=[
            ColumnProfile(
                name="a",
                type=ColumnType.NUMERICAL,
                unique_values=2,
                missing_values=0,
                unique_percentage=100.0,
                missing_percentage=0.0,
            )
        ],
        correlation_matrix=correlation,
    )
    response = GetDatasetResponse(
        sample_dataset={"a": [1, 2]},
        profiling=profiling,
    )
    payload = response.model_dump()
    assert cast(dict, payload["sample_dataset"])["a"] == [1, 2]
