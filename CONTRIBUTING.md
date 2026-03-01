# Contributing

## Setup

All development happens inside the Dev Container. See [Getting Started](./docs/GETTING_STARTED.md).

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

## Tests

See [Testing Guide](./docs/TESTING.md) for patterns and fixtures.
