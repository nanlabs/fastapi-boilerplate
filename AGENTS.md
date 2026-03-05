# AGENTS.md — Context for AI assistants

## Project

FastAPI boilerplate. Python 3.13, uv, Ruff, MyPy strict.

## Key rules

- All development happens inside the Dev Container.
- Run `make test` and `make all-checks` before committing.
- Do not add `try/except` blocks in endpoints; exceptions are handled globally in `app/core/exception_handlers.py`.
- Every API response uses `APIResponse[T]` from `app/api/schemas/common/responses.py`.
- New resources go in `app/api/endpoints/v1/`, `app/api/schemas/v1/`, and `app/api/services/`.
- Follow TDD when implementing changes.

## Architecture

```text
app/api/endpoints/v1/     HTTP handlers (thin, no business logic)
app/api/schemas/v1/       Pydantic request/response schemas
app/api/schemas/common/   Shared envelope and param schemas
app/api/services/         Business logic (no versioning)
app/api/dependencies/     FastAPI Depends factories
app/core/                 Config, middleware, logging, exception handlers
app/db/                   SQLAlchemy models, session, migrations
```

## Commands

```bash
make dev              # Dev server
make test             # All tests
make all-checks       # Lint + mypy + bandit
make migration-create # New alembic migration
```

## Full docs

See `docs/`.
