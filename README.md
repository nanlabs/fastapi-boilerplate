# FastAPI Boilerplate

[![CI](https://github.com/nanlabs/fastapi-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/nanlabs/fastapi-boilerplate/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/nanlabs/fastapi-boilerplate)](./LICENSE)
[![Powered by NaNLABS](https://img.shields.io/badge/powered%20by-NaNLABS-111827)](https://www.nanlabs.com/)

Opinionated FastAPI template for teams that want a strong backend baseline from day zero: clear layering, consistent API contracts, strict quality checks, and reproducible local setup.

## Who This Is For

Use this boilerplate when you need:

- a production-minded REST API foundation with versioned endpoints,
- strict coding standards (`Ruff`, `MyPy strict`, `Bandit`),
- consistent envelope responses (`APIResponse[T]`) across success and errors,
- low-friction onboarding through a Dev Container-first workflow.

## What This Boilerplate Is Not

- Not a batteries-included product framework (auth, queues, cache, multi-tenant are extension points).
- Not an async-first ORM setup (current default uses SQLAlchemy sync sessions).
- Not tied to a specific cloud provider or deployment platform.

See `docs/SCOPE.md` for explicit in-scope/out-of-scope boundaries.

## Core Principles

- Thin endpoints, business logic in services.
- No endpoint-level `try/except`; error mapping is centralized.
- Stable machine-readable `dev_code` values for clients.
- Test-first mindset and mandatory checks before merge.

## Quick Start (10-15 minutes)

Development happens inside the Dev Container.

```bash
# VS Code / Cursor
# Open project, then choose "Reopen in Container"

# CLI alternative
devcontainer up --workspace-folder .
```

If a `make` command fails with "must run inside the Dev Container", follow the setup above first.

## Host vs Dev Container

Use this as the default working model:

- Host machine: editor, AI tooling, and `git` commands (`status/add/commit/push`).
- Dev Container: application runtime and project commands (`make test`, `make all-checks`, migrations, `make dev`).

Bridge command when working from host terminal:

```bash
devcontainer exec --workspace-folder . make <target>
```

Inside the container:

```bash
make install-dev
make init-db
make dev
```

Validate setup:

```bash
curl -s http://localhost:8000/ping
curl -s http://localhost:8000/api/v1/healthz
make test
make all-checks
```

Open docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Documentation Map

| Doc | Why read it |
|---|---|
| [Docs Home](./docs/README.md) | Choose your learning path |
| [Scope](./docs/SCOPE.md) | Understand boundaries and extension points |
| [Getting Started](./docs/GETTING_STARTED.md) | First run and environment setup |
| [Golden Path](./docs/GOLDEN_PATH.md) | Recommended end-to-end flow for your first feature |
| [Development Guide](./docs/DEVELOPMENT.md) | Build features end-to-end with conventions |
| [Architecture](./docs/ARCHITECTURE.md) | Layering rules and key design decisions |
| [API Reference](./docs/API.md) | Endpoint contract and response envelope |
| [Database Guide](./docs/DATABASE.md) | SQLite/PostgreSQL and migrations |
| [Testing Guide](./docs/TESTING.md) | Test strategy and fixtures |
| [Tips and Tricks](./docs/TIPS_AND_TRICKS.md) | Debugging and productivity shortcuts |
| [Bootstrap Checklist](./docs/BOOTSTRAP_CHECKLIST.md) | Turn this template into your product repo |
| [References](./docs/REFERENCES.md) | Curated links to extend this boilerplate |
| [DX Metrics & Rollout](./docs/DX_METRICS_AND_ROLLOUT.md) | Measure and evolve developer experience safely |

## Contributing

Contributions are welcome. Start with `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.
