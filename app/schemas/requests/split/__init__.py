"""
Split operation schemas.

This module defines Pydantic schemas for train/test split operations.
"""

from app.schemas.requests.split.split_operation import SplitMethod, SplitOperation

__all__ = ["SplitMethod", "SplitOperation"]
