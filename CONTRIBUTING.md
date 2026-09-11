# Contributing

## Setup

All development happens inside the Dev Container. See [Getting Started](./docs/GETTING_STARTED.md) for setup steps and the host/container contract.

## Workflow

1. Create a branch from `main`.
2. Write tests first.
3. Implement.
4. Run `make all-checks` and `make test`.
5. Open a pull request.

Recommended local loop:

```bash
make test-unit
make autofix
make all-checks
```

## Adding a new resource

Follow [Development Guide](./docs/DEVELOPMENT.md).

## Code standards

- MyPy strict: add explicit typing.
- Ruff for lint and formatting (`make autofix` for auto-fixes).
- No endpoint-level `try/except`; add exception types in `app/core/exception_handlers.py`.
- All responses must use `APIResponse[T]`.

## Pre-commit strategy

- Local pre-commit hooks are intentionally fast (formatting/sanity checks).
- Heavy checks (`mypy`, `bandit`, full quality/test suite, mega-linter) run in CI as merge gates.
- Install local hooks (host machine): `pre-commit install`.

## Tests

See [Testing Guide](./docs/TESTING.md) for patterns and fixtures.

## CI quality gates

- `fast-quality`: docs lint + format validation (`make format-check`) — read-only, fails if code is not already formatted.
- `full-quality`: strict quality checks (`make all-checks`).
- `tests`: full test suite (`make test`).
- `mega-linter`: runs on PR/push with `.mega-linter.yml` (currently non-blocking rollout mode).

## Documentation expectations

When behavior, contracts, or architecture change, update the relevant docs in `docs/`:

- `API.md` for endpoint contract changes.
- `ARCHITECTURE.md` for design/boundary changes.
- `DEVELOPMENT.md` for workflow/convention changes.
- `README.md` (Scope section) when project boundaries change.

For a full list of available targets, see [Commands Reference](./docs/COMMANDS.md).
