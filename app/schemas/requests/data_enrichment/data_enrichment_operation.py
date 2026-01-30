"""
Data enrichment operation schema.

This module defines the schema for data enrichment operations that add
additional features or information to datasets.
"""

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType


class DataEnrichmentOperation(BaseOperation):
    """
    Operation to enrich dataset with additional features.

    Defines external dataset inputs and join keys for enrichment tasks.
    """

    operation_type: OperationType = Field(
        default=OperationType.DATA_ENRICHMENT, description="Operation type"
    )
    external_dataset: dict[str, list] = Field(..., description="Dataset to enrich")
    external_dataset_index_column: str = Field(
        ..., description="Column to use as index in the external dataset"
    )
    index_column: str = Field(..., description="Column to use as index")

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
                    "operation_type": "data_enrichment",
                    "external_dataset": {
                        "columns": ["customer_id", "segment"],
                        "data": [[1, "gold"], [2, "silver"]],
                    },
                    "external_dataset_index_column": "customer_id",
                    "index_column": "customer_id",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
