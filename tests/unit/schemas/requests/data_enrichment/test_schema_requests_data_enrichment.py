"""Coverage tests for data enrichment request schemas."""

from __future__ import annotations

from uuid import UUID

from app.schemas.common import OperationMetadata, OperationType
from app.schemas.requests import data_enrichment as data_enrichment_schemas
from app.schemas.requests.data_enrichment.data_enrichment_operation import DataEnrichmentOperation


def build_metadata() -> OperationMetadata:
    """Build metadata for tests."""
    return OperationMetadata(model_id=UUID("11111111-1111-1111-1111-111111111111"))


def test_data_enrichment_exports() -> None:
    """Expose data enrichment schemas in package exports."""
    assert "DataEnrichmentOperation" in data_enrichment_schemas.__all__
    assert data_enrichment_schemas.DataEnrichmentOperation is DataEnrichmentOperation


def test_data_enrichment_operation() -> None:
    """Create data enrichment operation with dataset dict."""
    external: dict[str, list[int | str]] = {
        "customer_id": [1, 2],
        "segment": ["gold", "silver"],
    }
    operation = DataEnrichmentOperation(
        metadata=build_metadata(),
        external_dataset=external,
        external_dataset_index_column="customer_id",
        index_column="customer_id",
    )
    assert operation.operation_type is OperationType.DATA_ENRICHMENT
    payload = operation.model_dump()
    assert payload["external_dataset"]["customer_id"] == [1, 2]
