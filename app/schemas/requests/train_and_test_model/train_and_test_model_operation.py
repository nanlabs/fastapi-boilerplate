"""
Train model operation schema.

This module defines the schema for training machine learning models.
It includes the operation schema for training a model and the parameters
for the model.
"""

from pydantic import Field

from app.schemas.common import BaseOperation, OperationType


class TrainAndTestModelOperation(BaseOperation):
    """
    Operation to train and test a model.

    Defines the request for executing training and evaluation workflows.
    """

    operation_type: OperationType = Field(
        default=OperationType.TRAIN_AND_TEST_MODEL, description="Operation type"
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
                    "operation_type": "train_and_test_model",
                }
            ]
        }
    }
    # pylint: enable=duplicate-code
