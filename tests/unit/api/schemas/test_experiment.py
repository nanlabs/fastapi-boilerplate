"""Unit tests for app.api.schemas.experiment."""

import datetime

import pytest
from pydantic import ValidationError

from app.api.schemas.experiment import (
    ExperimentAttachDataset,
    ExperimentBase,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentUpdate,
)
from app.schemas.common.base import ExperimentStatus


class TestExperimentBase:
    """Test ExperimentBase schema."""

    def test_experiment_base_valid(self) -> None:
        """Create valid ExperimentBase."""
        data = ExperimentBase(
            name="Test Experiment",
            project_id=1,
            description="Test description",
        )
        assert data.name == "Test Experiment"
        assert data.project_id == 1
        assert data.description == "Test description"

    def test_experiment_base_minimal(self) -> None:
        """Create ExperimentBase with minimal required fields."""
        data = ExperimentBase(
            name="Test", project_id=1, description="Test description"
        )
        assert data.name == "Test"
        assert data.project_id == 1
        assert data.description == "Test description"


class TestExperimentCreate:
    """Test ExperimentCreate schema."""

    def test_experiment_create_valid(self) -> None:
        """Create valid ExperimentCreate."""
        data = ExperimentCreate(
            name="Test Experiment",
            project_id=1,
            description="Test description",
        )
        assert data.name == "Test Experiment"
        assert data.project_id == 1

    def test_experiment_create_name_too_short(self) -> None:
        """Raise error when name is too short."""
        with pytest.raises(ValidationError):
            ExperimentCreate(
                name="", project_id=1, description="Test description"
            )

    def test_experiment_create_name_too_long(self) -> None:
        """Raise error when name is too long."""
        with pytest.raises(ValidationError):
            ExperimentCreate(
                name="x" * 256, project_id=1, description="Test description"
            )


class TestExperimentUpdate:
    """Test ExperimentUpdate schema."""

    def test_experiment_update_all_fields(self) -> None:
        """Update all fields."""
        data = ExperimentUpdate(
            name="Updated Name",
            project_id=2,
            description="Updated description",
        )
        assert data.name == "Updated Name"
        assert data.project_id == 2
        assert data.description == "Updated description"

    def test_experiment_update_partial(self) -> None:
        """Update only some fields."""
        data = ExperimentUpdate(name="Updated Name")
        assert data.name == "Updated Name"
        assert data.project_id is None
        assert data.description is None

    def test_experiment_update_empty(self) -> None:
        """Create empty update."""
        data = ExperimentUpdate()
        assert data.name is None
        assert data.project_id is None


class TestExperimentAttachDataset:
    """Test ExperimentAttachDataset schema."""

    def test_attach_dataset_with_path(self) -> None:
        """Attach dataset with path."""
        data = ExperimentAttachDataset(path="/path/to/file.csv", dataset_file_id=None)
        assert data.path == "/path/to/file.csv"
        assert data.dataset_file_id is None

    def test_attach_dataset_with_id(self) -> None:
        """Attach dataset with existing ID."""
        data = ExperimentAttachDataset(path=None, dataset_file_id=1)
        assert data.dataset_file_id == 1
        assert data.path is None

    def test_attach_dataset_neither_provided(self) -> None:
        """Raise error when neither path nor dataset_file_id is provided."""
        with pytest.raises(ValidationError) as exc_info:
            ExperimentAttachDataset(path=None, dataset_file_id=None)
        errors = exc_info.value.errors()
        assert any(
            error["type"] == "value_error" and "must be provided" in str(error["msg"]).lower()
            for error in errors
        )

    def test_attach_dataset_both_provided(self) -> None:
        """Raise error when both path and dataset_file_id are provided."""
        with pytest.raises(ValidationError) as exc_info:
            ExperimentAttachDataset(path="/path/to/file.csv", dataset_file_id=1)
        errors = exc_info.value.errors()
        assert any(
            error["type"] == "value_error"
            and (
                "both" in str(error["msg"]).lower()
                or "cannot provide both" in str(error["msg"]).lower()
            )
            for error in errors
        )

    def test_attach_dataset_invalid_id(self) -> None:
        """Raise error when dataset_file_id is invalid."""
        with pytest.raises(ValidationError):
            ExperimentAttachDataset(path=None, dataset_file_id=0)

    def test_attach_dataset_path_too_short(self) -> None:
        """Raise error when path is too short."""
        with pytest.raises(ValidationError):
            ExperimentAttachDataset(path="", dataset_file_id=None)

    def test_attach_dataset_path_too_long(self) -> None:
        """Raise error when path is too long."""
        with pytest.raises(ValidationError):
            ExperimentAttachDataset(path="x" * 1001, dataset_file_id=None)


class TestExperimentResponse:
    """Test ExperimentResponse schema."""

    def test_experiment_response_valid(self) -> None:
        """Create valid ExperimentResponse."""
        data = ExperimentResponse(
            id=1,
            name="Test Experiment",
            project_id=1,
            description="Test description",
            status=ExperimentStatus.DRAFT,
            current_step=0,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        assert data.id == 1
        assert data.name == "Test Experiment"
        assert data.project_id == 1
        assert data.status == ExperimentStatus.DRAFT
        assert data.current_step == 0
        assert isinstance(data.created_at, datetime.datetime)
        assert isinstance(data.updated_at, datetime.datetime)
