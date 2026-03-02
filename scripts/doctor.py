"""Lightweight environment diagnostics for local development."""

from __future__ import annotations

import shutil
import subprocess
import sys

from app.core.config import settings


def _check_binary(name: str) -> bool:
    return shutil.which(name) is not None


def _run(cmd: list[str]) -> tuple[bool, str]:
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)  # nosec B603
        return True, output.strip()
    except Exception as exc:  # pragma: no cover - defensive fallback
        return False, str(exc)


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    checks.append(("python", _check_binary("python"), sys.version.split()[0]))
    checks.append(("uv", _check_binary("uv"), "present" if _check_binary("uv") else "missing"))
    checks.append(
        (
            "database_url",
            bool(settings.resolved_database_url),
            settings.resolved_database_url,
        )
    )

    uv_ok, uv_version = _run(["uv", "--version"])
    checks.append(("uv_version", uv_ok, uv_version))

    all_ok = True
    for name, status, detail in checks:
        marker = "OK" if status else "FAIL"
        print(f"[{marker}] {name}: {detail}")
        all_ok = all_ok and status

    if not all_ok:
        print("Environment check failed. Review items marked FAIL.")
        return 1

    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
