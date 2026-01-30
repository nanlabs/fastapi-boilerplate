"""Coverage-focused tests for core modules."""

from __future__ import annotations

import runpy
import sys
import types
from pathlib import Path
from typing import Any, cast

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db import models
from app.db import session as db_session
from app.db.models.base import Base


class FrozenSettings(Settings):
    """Settings variant that simulates a frozen executable."""

    _frozen = True


def test_cors_origins_empty() -> None:
    """Return empty list when CORS origins are blank."""
    settings = Settings()
    settings.cors_origins_str = " , , "
    assert settings.cors_origins == []


def test_database_path_pyinstaller_meipass(tmp_path: Path, monkeypatch) -> None:
    """Resolve database path using PyInstaller executable parent."""
    settings = FrozenSettings()
    monkeypatch.setattr(sys, "_MEIPASS", "1", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "app.exe"))

    db_path = settings.database_path

    assert db_path == tmp_path / "data" / "app.db"
    assert db_path.parent.exists()


def test_database_path_pyinstaller_no_meipass(tmp_path: Path, monkeypatch) -> None:
    """Resolve database path using current working directory."""
    settings = FrozenSettings()
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    monkeypatch.setattr(Path, "cwd", classmethod(lambda cls: tmp_path))

    db_path = settings.database_path

    assert db_path == tmp_path / "data" / "app.db"
    assert db_path.parent.exists()


def test_resolved_database_url_non_sqlite() -> None:
    """Return non-sqlite database URL unchanged."""
    url = "postgresql://user:pass@localhost/db"
    settings = Settings(database_url=url)
    assert settings.resolved_database_url == url


def test_models_exports_base() -> None:
    """Expose Base in models package exports."""
    assert models.Base is Base
    assert "Base" in models.__all__


def test_get_db_yields_session() -> None:
    """Yield a SQLAlchemy session and close on exit."""
    generator = db_session.get_db()
    db = next(generator)
    assert isinstance(db, Session)
    generator.close()


def test_main_runs_uvicorn(monkeypatch) -> None:
    """Run app.main __main__ block with patched uvicorn."""
    captured_args: list[object] = []
    captured_kwargs: dict[str, object] = {}

    def run(*args: object, **kwargs: object) -> None:
        nonlocal captured_args, captured_kwargs
        captured_args = list(args)
        captured_kwargs = kwargs

    uvicorn_module = cast(Any, types.ModuleType("uvicorn"))
    uvicorn_module.run = run
    monkeypatch.setitem(sys.modules, "uvicorn", uvicorn_module)

    sys.modules.pop("app.main", None)
    runpy.run_module("app.main", run_name="__main__")

    assert captured_args
    assert captured_args[0] == "app.main:app"
    assert "host" in captured_kwargs
    assert "port" in captured_kwargs
