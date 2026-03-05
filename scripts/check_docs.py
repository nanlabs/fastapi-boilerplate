"""Validate internal markdown links in repository docs."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_GLOB = ["README.md", "docs/*.md", "config/*.md", "CONTRIBUTING.md"]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for pattern in MARKDOWN_GLOB:
        files.extend(REPO_ROOT.glob(pattern))
    return sorted(set(files))


def _is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:"))


def _normalize_target(link: str, base_file: Path) -> Path | None:
    target = link.strip()
    if not target or target.startswith("#"):
        return None
    if _is_external(target):
        return None

    target = target.split("#", maxsplit=1)[0].strip()
    if not target:
        return None

    if target.startswith("/"):
        return REPO_ROOT / target.lstrip("/")
    return (base_file.parent / target).resolve()


def main() -> int:
    failures: list[str] = []

    for md_file in _iter_markdown_files():
        content = md_file.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(content):
            raw_link = match.group(1).strip()
            target = _normalize_target(raw_link, md_file)
            if target is None:
                continue
            if not target.exists():
                rel_file = md_file.relative_to(REPO_ROOT)
                failures.append(f"{rel_file}: broken link '{raw_link}'")

    if failures:
        print("Documentation link check failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("Documentation links look good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
