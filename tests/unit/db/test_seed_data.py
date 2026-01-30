"""Unit tests for seed data loading utilities."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.db.seed_data import (
    get_default_experiment_types,
    get_default_model_types,
    get_status_value,
    load_seed_data,
)
from app.schemas.common.base import ModelTypeStatus


class TestLoadSeedData:
    """Test load_seed_data function."""

    def test_load_seed_data_success(self, tmp_path: Path) -> None:
        """Load seed data successfully from valid YAML file."""
        seed_file = tmp_path / "seed_data.yaml"
        seed_file.write_text(
            """
model_types:
  - id: 1
    name: "Credit Models"
    enabled: true
    status: "available"
experiment_types:
  - id: 1
    name: "classification"
"""
        )

        config = load_seed_data(seed_file)

        assert len(config.model_types) == 1
        assert config.model_types[0].id == 1
        assert config.model_types[0].name == "Credit Models"
        assert len(config.experiment_types) == 1
        assert config.experiment_types[0].id == 1
        assert config.experiment_types[0].name == "classification"

    def test_load_seed_data_file_not_found(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when seed data file does not exist."""
        non_existent_file = tmp_path / "non_existent.yaml"

        with pytest.raises(FileNotFoundError, match="Seed data file not found"):
            load_seed_data(non_existent_file)

    def test_load_seed_data_invalid_yaml(self, tmp_path: Path) -> None:
        """Raise ValueError when YAML is invalid."""
        seed_file = tmp_path / "invalid.yaml"
        # Create invalid YAML that will cause YAMLError
        seed_file.write_text("invalid: yaml: content: [unclosed bracket")

        with pytest.raises(ValueError, match="Seed data file contains invalid YAML"):
            load_seed_data(seed_file)

    def test_load_seed_data_not_dict(self, tmp_path: Path) -> None:
        """Raise ValueError when YAML payload is not a dictionary."""
        seed_file = tmp_path / "not_dict.yaml"
        seed_file.write_text("- item1\n- item2")

        with pytest.raises(ValueError, match="Seed data configuration must be a YAML mapping"):
            load_seed_data(seed_file)

    def test_load_seed_data_validation_error(self, tmp_path: Path) -> None:
        """Raise ValueError when seed data validation fails."""
        seed_file = tmp_path / "invalid_config.yaml"
        seed_file.write_text(
            """
model_types:
  - id: "not_an_int"
    name: "Test"
"""
        )

        with pytest.raises(ValueError, match="Seed data configuration is invalid"):
            load_seed_data(seed_file)

    def test_load_seed_data_duplicate_model_type_ids(self, tmp_path: Path) -> None:
        """Raise ValueError when model types have duplicate IDs."""
        seed_file = tmp_path / "duplicate_ids.yaml"
        seed_file.write_text(
            """
model_types:
  - id: 1
    name: "Type A"
    enabled: true
    status: "available"
  - id: 1
    name: "Type B"
    enabled: true
    status: "available"
experiment_types: []
"""
        )

        with pytest.raises(ValueError, match="Seed data contains duplicate IDs: 1"):
            load_seed_data(seed_file)

    def test_load_seed_data_duplicate_model_type_names(self, tmp_path: Path) -> None:
        """Raise ValueError when model types have duplicate names."""
        seed_file = tmp_path / "duplicate_names.yaml"
        seed_file.write_text(
            """
model_types:
  - id: 1
    name: "Same Name"
    enabled: true
    status: "available"
  - id: 2
    name: "Same Name"
    enabled: true
    status: "available"
experiment_types: []
"""
        )

        with pytest.raises(ValueError, match="Seed data contains duplicate names: Same Name"):
            load_seed_data(seed_file)

    def test_load_seed_data_duplicate_experiment_type_ids(self, tmp_path: Path) -> None:
        """Raise ValueError when experiment types have duplicate IDs."""
        seed_file = tmp_path / "duplicate_exp_ids.yaml"
        seed_file.write_text(
            """
model_types: []
experiment_types:
  - id: 1
    name: "Type A"
  - id: 1
    name: "Type B"
"""
        )

        with pytest.raises(ValueError, match="Seed data contains duplicate IDs: 1"):
            load_seed_data(seed_file)

    def test_load_seed_data_duplicate_experiment_type_names(self, tmp_path: Path) -> None:
        """Raise ValueError when experiment types have duplicate names."""
        seed_file = tmp_path / "duplicate_exp_names.yaml"
        seed_file.write_text(
            """
model_types: []
experiment_types:
  - id: 1
    name: "Same Name"
  - id: 2
    name: "Same Name"
"""
        )

        with pytest.raises(ValueError, match="Seed data contains duplicate names: Same Name"):
            load_seed_data(seed_file)

    def test_load_seed_data_uses_default_path(self, tmp_path: Path) -> None:
        """Use default path when seed_data_path is None."""
        default_path = tmp_path / "config" / "seed_data.yaml"
        default_path.parent.mkdir(parents=True)
        default_path.write_text(
            """
model_types: []
experiment_types: []
"""
        )

        with patch("app.db.seed_data.Path.cwd", return_value=tmp_path):
            config = load_seed_data()

        assert config is not None


class TestGetStatusValue:
    """Test get_status_value function."""

    def test_get_status_value_from_enum(self) -> None:
        """Get status value from ModelTypeStatus enum."""
        result = get_status_value(ModelTypeStatus.AVAILABLE)
        assert result == "available"

    def test_get_status_value_from_string(self) -> None:
        """Get status value from string."""
        result = get_status_value("request_access")
        assert result == "request_access"
        assert isinstance(result, str)


class TestGetDefaultModelTypes:
    """Test get_default_model_types function."""

    def test_get_default_model_types_success(self, tmp_path: Path) -> None:
        """Return model types from seed data."""
        seed_file = tmp_path / "seed_data.yaml"
        seed_file.write_text(
            """
model_types:
  - id: 1
    name: "Credit Models"
    description: "Credit risk models"
    enabled: true
    status: "available"
experiment_types: []
"""
        )

        result = get_default_model_types(seed_file)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Credit Models"
        assert result[0].description == "Credit risk models"
        assert result[0].enabled is True
        assert result[0].status == "available"

    def test_get_default_model_types_with_enum_status(self, tmp_path: Path) -> None:
        """Handle ModelTypeStatus enum in status field."""
        seed_file = tmp_path / "seed_data.yaml"
        seed_file.write_text(
            """
model_types:
  - id: 1
    name: "Credit Models"
    enabled: true
    status: "available"
experiment_types: []
"""
        )

        result = get_default_model_types(seed_file)

        assert len(result) == 1
        assert result[0].status == "available"


class TestGetDefaultExperimentTypes:
    """Test get_default_experiment_types function."""

    def test_get_default_experiment_types_success(self, tmp_path: Path) -> None:
        """Return experiment types from seed data."""
        seed_file = tmp_path / "seed_data.yaml"
        seed_file.write_text(
            """
model_types: []
experiment_types:
  - id: 1
    name: "classification"
  - id: 2
    name: "regression"
"""
        )

        result = get_default_experiment_types(seed_file)

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].name == "classification"
        assert result[1].id == 2
        assert result[1].name == "regression"

    def test_get_default_experiment_types_empty(self, tmp_path: Path) -> None:
        """Return empty list when no experiment types in seed data."""
        seed_file = tmp_path / "seed_data.yaml"
        seed_file.write_text(
            """
model_types: []
experiment_types: []
"""
        )

        result = get_default_experiment_types(seed_file)

        assert not result
