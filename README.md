# FastAPI Boilerplate

A production-ready, opinionated FastAPI boilerplate with standard response envelopes, database migrations, structured logging, and a full Dev Container workflow.

## What's included

- **FastAPI** with versioned endpoints (`/api/v1/...`)
- **Standard response envelope** on every API response
- **SQLite** by default, ready for PostgreSQL via environment variable
- **Alembic** migrations with startup initialization
- **SQLAlchemy 2.0** ORM with typed models
- **Request ID tracing** via `X-Request-ID` header
- **Structured logging** (`DEBUG=true` text, `DEBUG=false` JSON)
- **MyPy strict** type checking
- **Ruff** linting and formatting
- **Dev Container** workflow

## Quick start

> Development happens inside the Dev Container.

```bash
# VS Code / Cursor
# Open project and choose "Reopen in Container"

# CLI alternative
devcontainer up --workspace-folder .
```

Once the container is ready:

```bash
make dev        # Server at http://localhost:8000
make test       # Run tests
make all-checks # Lint + type-check + security
```

API docs: http://localhost:8000/docs

## Documentation

| Doc | Description |
|---|---|
| [Getting Started](./docs/GETTING_STARTED.md) | Dev Container setup and first run |
| [Project Structure](./docs/PROJECT_STRUCTURE.md) | Annotated repository layout |
| [Architecture](./docs/ARCHITECTURE.md) | Decisions, patterns, and rationale |
| [API Reference](./docs/API.md) | Endpoints and response envelope |
| [Development Guide](./docs/DEVELOPMENT.md) | Add resources end-to-end |
| [Database Guide](./docs/DATABASE.md) | SQLite, PostgreSQL, migrations |
| [Configuration](./docs/CONFIGURATION.md) | Environment variables |
| [Testing Guide](./docs/TESTING.md) | Test structure and patterns |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT — see [LICENSE](./LICENSE).
