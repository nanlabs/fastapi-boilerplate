# Contributing

## Setup

All development happens inside the Dev Container. See [Getting Started](./docs/GETTING_STARTED.md).

## Host vs Dev Container

- Host is fine for `git` operations (`status`, `add`, `commit`, `push`) and editing tools.
- Run all project commands inside Dev Container (`make test`, `make all-checks`, migrations, `make dev`).
- Host bridge command:
  `devcontainer exec --workspace-folder . make <target>`.

## Workflow

1. Create a branch from `main`.
2. Write tests first.
3. Implement.
4. Run `make all-checks` and `make test`.
5. Open a pull request.

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

- `fast-quality`: docs + lint + format checks.
- `full-quality`: strict quality checks (`make all-checks`).
- `tests`: full test suite (`make test`).
- `mega-linter`: optional gate toggled via repository variable `ENABLE_MEGA_LINTER=true`.
- Track DX impact using `docs/DX_METRICS_AND_ROLLOUT.md`.

## Documentation expectations

When behavior, contracts, or architecture change, update the relevant docs in `docs/`:

- `API.md` for endpoint contract changes.
- `ARCHITECTURE.md` for design/boundary changes.
- `DEVELOPMENT.md` for workflow/convention changes.
- `SCOPE.md` when project boundaries change.
