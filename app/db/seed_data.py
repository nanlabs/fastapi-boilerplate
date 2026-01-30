"""Seed data loading utilities for database initialization."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from app.db.models.experiment_type import ExperimentType
from app.db.models.model_type import ModelType
from app.schemas.common.base import ModelTypeStatus
from app.schemas.data.experiment_type import ExperimentType as ExperimentTypeSchema
from app.schemas.data.model_type import ModelType as ModelTypeSchema


class SeedDataConfig(BaseModel):
    """Seed data configuration schema."""

    model_types: list[ModelTypeSchema] = Field(default_factory=list)
    experiment_types: list[ExperimentTypeSchema] = Field(default_factory=list)


def _resolve_seed_data_path(seed_data_path: Path | None = None) -> Path:
    """Resolve seed data configuration path."""
    return seed_data_path or (Path.cwd() / "config" / "seed_data.yaml")


def _load_seed_data_payload(seed_data_path: Path) -> dict:
    """Load seed data YAML payload from disk."""
    if not seed_data_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {seed_data_path}")

    try:
        with seed_data_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Seed data file contains invalid YAML: {seed_data_path}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Seed data configuration must be a YAML mapping.")

    return payload


# pylint: disable=too-many-locals
def load_seed_data(seed_data_path: Path | None = None) -> SeedDataConfig:
    """Load and validate seed data configuration."""
    resolved_path = _resolve_seed_data_path(seed_data_path)
    payload = _load_seed_data_payload(resolved_path)

    try:
        config = SeedDataConfig.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Seed data configuration is invalid.") from exc

    # Validate unique IDs and names for model_types
    model_type_ids = [mt.id for mt in config.model_types]
    model_type_names = [mt.name for mt in config.model_types]
    model_seen_ids: set[int] = set()
    model_seen_names: set[str] = set()
    duplicate_ids: set[int] = set()
    duplicate_names: set[str] = set()

    for model_type_id in model_type_ids:
        if model_type_id in model_seen_ids:
            duplicate_ids.add(model_type_id)
        model_seen_ids.add(model_type_id)

    for model_type_name in model_type_names:
        if model_type_name in model_seen_names:
            duplicate_names.add(model_type_name)
        model_seen_names.add(model_type_name)

    # Validate unique IDs and names for experiment_types
    exp_type_ids = [et.id for et in config.experiment_types]
    exp_type_names = [et.name for et in config.experiment_types]
    exp_seen_ids: set[int] = set()
    exp_seen_names: set[str] = set()

    for exp_type_id in exp_type_ids:
        if exp_type_id in exp_seen_ids:
            duplicate_ids.add(exp_type_id)
        exp_seen_ids.add(exp_type_id)

    for exp_type_name in exp_type_names:
        if exp_type_name in exp_seen_names:
            duplicate_names.add(exp_type_name)
        exp_seen_names.add(exp_type_name)

    if duplicate_ids:
        duplicate_ids_list = ", ".join(sorted(str(did) for did in duplicate_ids))
        raise ValueError(f"Seed data contains duplicate IDs: {duplicate_ids_list}")

    if duplicate_names:
        duplicate_names_list = ", ".join(sorted(duplicate_names))
        raise ValueError(f"Seed data contains duplicate names: {duplicate_names_list}")

    return config


def get_status_value(status: ModelTypeStatus | str) -> str:
    """Get status value from enum or string."""
    if isinstance(status, ModelTypeStatus):
        return status.value
    return str(status)


def get_default_model_types(seed_data_path: Path | None = None) -> list[ModelType]:
    """Return model types from seed data configuration."""
    config = load_seed_data(seed_data_path)
    result: list[ModelType] = []

    for model_type in config.model_types:
        result.append(
            ModelType(
                id=model_type.id,
                name=model_type.name,
                description=model_type.description,
                enabled=model_type.enabled,
                status=get_status_value(model_type.status),
            )
        )

    return result


def get_default_experiment_types(seed_data_path: Path | None = None) -> list[ExperimentType]:
    """Return experiment types from seed data configuration."""
    config = load_seed_data(seed_data_path)
    result: list[ExperimentType] = []

    for experiment_type in config.experiment_types:
        result.append(
            ExperimentType(
                id=experiment_type.id,
                name=experiment_type.name,
            )
        )

    return result
