# FastAPI Boilerplate

[![CI](https://github.com/nanlabs/fastapi-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/nanlabs/fastapi-boilerplate/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/nanlabs/fastapi-boilerplate)](./LICENSE)
[![Powered by NaNLABS](https://img.shields.io/badge/powered%20by-NaNLABS-111827)](https://www.nanlabs.com/)

A production-ready, opinionated FastAPI boilerplate designed for teams that want to ship faster without reinventing backend foundations.

This project is **powered by NaNLABS** and built to be reusable across future APIs with strong defaults for architecture, testing, and developer experience.

## Why This Boilerplate

- Clean **versioned API structure** (`/api/v1/...`) ready for future versions.
- Consistent **APIResponse envelope** for success and error contracts.
- Built-in **request tracing** with `X-Request-ID`.
- Strong quality baseline with **Ruff**, **MyPy strict**, and **Bandit**.
- Database lifecycle covered with **SQLAlchemy + Alembic**.
- First-class **Dev Container** workflow for reproducible development.

## What You Get Out of the Box

- FastAPI with modular endpoints, dependencies, services, and schemas.
- Standardized response metadata (`request_id`, timestamps, pagination context).
- SQLite by default, PostgreSQL-ready through environment configuration.
- Structured logging (`DEBUG=true` human-readable, `DEBUG=false` JSON).
- Automated CI checks via GitHub Actions.

## Quick Start

> Development happens inside the Dev Container.

```bash
# VS Code / Cursor
# Open the project and choose "Reopen in Container"

# CLI alternative
devcontainer up --workspace-folder .
```

Once the container is ready:

```bash
make dev        # API server at http://localhost:8000
make test       # Run all tests
make all-checks # Ruff + MyPy + Bandit
```

Open API docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Documentation

| Doc | Description |
|---|---|
| [Docs Home](./docs/README.md) | Central docs index and navigation |
| [Getting Started](./docs/GETTING_STARTED.md) | Dev Container setup and first run |
| [Project Structure](./docs/PROJECT_STRUCTURE.md) | Annotated repository layout |
| [Architecture](./docs/ARCHITECTURE.md) | Design decisions and layer boundaries |
| [API Reference](./docs/API.md) | Endpoints and envelope contract |
| [Development Guide](./docs/DEVELOPMENT.md) | Add new resources end-to-end |
| [Database Guide](./docs/DATABASE.md) | SQLite, PostgreSQL, and migrations |
| [Configuration](./docs/CONFIGURATION.md) | Environment variables and runtime behavior |
| [Testing Guide](./docs/TESTING.md) | Test patterns, fixtures, and strategy |

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT — see [LICENSE](./LICENSE).
