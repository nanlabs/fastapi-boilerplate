"""Seed data loading utilities for database initialization."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class SeedDataConfig(BaseModel):
    """Seed data configuration schema.

    Empty by default - extend this class to add your own seed data models.
    """


def _resolve_seed_data_path(seed_data_path: Path | None = None) -> Path:
    """Resolve seed data configuration path."""
    return seed_data_path or (Path.cwd() / "config" / "seed_data.yaml")


def _load_seed_data_payload(seed_data_path: Path) -> dict[str, object]:
    """Load seed data YAML payload from disk."""
    if not seed_data_path.exists():
        # Return empty config if file doesn't exist
        return {}

    try:
        with seed_data_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Seed data file contains invalid YAML: {seed_data_path}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Seed data configuration must be a YAML mapping.")

    return payload


def load_seed_data(seed_data_path: Path | None = None) -> SeedDataConfig:
    """Load and validate seed data configuration.

    Returns an empty configuration by default. Extend SeedDataConfig
    and this function to add your own seed data loading logic.
    """
    resolved_path = _resolve_seed_data_path(seed_data_path)
    payload = _load_seed_data_payload(resolved_path)

    config = SeedDataConfig.model_validate(payload)
    return config
