# Commands Reference 🧰

This page is the quick reference for all `make` targets in this repository.

All project commands run inside the Dev Container.

If you are on host terminal, use:

```bash
devcontainer exec --workspace-folder . make <target>
```

## Setup and environment

```bash
make install         # Install production dependencies with uv
make install-dev     # Install development dependencies with uv
make bootstrap       # install-dev + init-db + doctor + check-docs
make doctor          # Validate local development environment
make clean           # Remove caches and build artifacts
make help            # Show grouped command help
```

## Running the API

```bash
make run             # Run FastAPI server (no reload)
make dev             # Run FastAPI server with auto-reload
make init-db         # Initialize database (migrations + seed hook)
```

## Testing

```bash
make test            # Full test suite
make test-unit       # Unit tests only
make test-integration# Integration tests only
make test-coverage   # Tests with coverage report
```

## Code quality

```bash
make lint            # Ruff lint checks
make format          # Ruff formatter
make autofix         # Ruff --fix + format
make type-check      # MyPy strict checks
make check-docs      # Validate markdown links
make all-checks      # Ruff + format --check + MyPy + Bandit + docs
```

## Migrations

```bash
make migration-create MESSAGE="add users table"
make migration-upgrade
make migration-upgrade-to REVISION="revision_id"
make migration-downgrade
make migration-downgrade-to REVISION="revision_id"
make migration-current
make migration-show
make migration-history
make migration-stamp REVISION="revision_id"
make migration-merge REVISIONS="rev1,rev2" MESSAGE="merge heads"
```

## Suggested workflows

Daily local loop:

```bash
make test-unit
make autofix
make all-checks
```

Before opening a PR:

```bash
make test
make all-checks
```

## Related docs

- `GETTING_STARTED.md` for first run steps.
- `DEVELOPMENT.md` for resource implementation workflow.
- `DATABASE.md` for migration policy and troubleshooting.
