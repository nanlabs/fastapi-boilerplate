"""Custom exceptions for API error handling."""

import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str) -> None:
        """Initialize exception with message."""
        self.message = message
        super().__init__(self.message)


class NotFoundError(APIException):
    """Exception raised when a resource is not found."""


class ConflictError(APIException):
    """Exception raised when a resource conflict occurs (e.g., duplicate name)."""


class ValidationError(APIException):
    """Exception raised when input validation fails."""


class SortingValidationError(APIException):
    """Exception raised when sorting field validation fails."""
