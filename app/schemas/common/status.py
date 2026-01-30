"""
Status enumeration for operations.

This module defines the status enum used across all ML operations
to track their execution state.
"""

from enum import Enum


class Status(str, Enum):
    """
    Status of an operation.

    Defines the lifecycle states used by ML workflow operations.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
