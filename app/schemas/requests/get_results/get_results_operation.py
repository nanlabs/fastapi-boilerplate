"""
Get results operation schema.

This module defines the schema for get results operations.
"""

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType


class GetResultsOperation(BaseOperation):
    """
    Operation to get results.

    Defines the request for retrieving computed workflow results.
    """

    operation_type: OperationType = Field(
        default=OperationType.GET_RESULTS, description="Operation type"
    )

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
                    "operation_type": "get_results",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
