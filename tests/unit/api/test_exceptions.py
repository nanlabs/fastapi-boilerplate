"""Unit tests for app.api.exceptions."""

import pytest

from app.api.exceptions import (
    APIException,
    ConflictError,
    NotFoundError,
    SortingValidationError,
    ValidationError,
)


class TestAPIException:
    """Test APIException base class."""

    def test_api_exception_init(self) -> None:
        """Initialize APIException with message."""
        message = "Test error message"
        exception = APIException(message)

        assert exception.message == message
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_api_exception_inheritance(self) -> None:
        """APIException is a subclass of Exception."""
        exception = APIException("Test message")
        assert isinstance(exception, Exception)


class TestNotFoundError:
    """Test NotFoundError exception."""

    def test_not_found_error_init(self) -> None:
        """Initialize NotFoundError with message."""
        message = "Resource not found"
        exception = NotFoundError(message)

        assert exception.message == message
        assert str(exception) == message
        assert isinstance(exception, APIException)
        assert isinstance(exception, Exception)

    def test_not_found_error_usage(self) -> None:
        """Raise NotFoundError and verify message."""
        message = "Project with ID 999 not found"
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(message)

        assert exc_info.value.message == message
        assert str(exc_info.value) == message


class TestConflictError:
    """Test ConflictError exception."""

    def test_conflict_error_init(self) -> None:
        """Initialize ConflictError with message."""
        message = "Resource conflict"
        exception = ConflictError(message)

        assert exception.message == message
        assert str(exception) == message
        assert isinstance(exception, APIException)
        assert isinstance(exception, Exception)

    def test_conflict_error_usage(self) -> None:
        """Raise ConflictError and verify message."""
        message = "Project with name 'Test' already exists"
        with pytest.raises(ConflictError) as exc_info:
            raise ConflictError(message)

        assert exc_info.value.message == message
        assert str(exc_info.value) == message


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_init(self) -> None:
        """Initialize ValidationError with message."""
        message = "Validation failed"
        exception = ValidationError(message)

        assert exception.message == message
        assert str(exception) == message
        assert isinstance(exception, APIException)
        assert isinstance(exception, Exception)

    def test_validation_error_usage(self) -> None:
        """Raise ValidationError and verify message."""
        message = "Invalid input data"
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(message)

        assert exc_info.value.message == message
        assert str(exc_info.value) == message


class TestSortingValidationError:
    """Test SortingValidationError exception."""

    def test_sorting_validation_error_init(self) -> None:
        """Initialize SortingValidationError with message."""
        message = "Invalid sort field"
        exception = SortingValidationError(message)

        assert exception.message == message
        assert str(exception) == message
        assert isinstance(exception, APIException)
        assert isinstance(exception, Exception)

    def test_sorting_validation_error_usage(self) -> None:
        """Raise SortingValidationError and verify message."""
        message = "Invalid sort field 'invalid_field'. Valid fields are: id, name"
        with pytest.raises(SortingValidationError) as exc_info:
            raise SortingValidationError(message)

        assert exc_info.value.message == message
        assert str(exc_info.value) == message
