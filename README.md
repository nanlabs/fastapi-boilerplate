# FastAPI Boilerplate

[![CI](https://github.com/nanlabs/fastapi-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/nanlabs/fastapi-boilerplate/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/nanlabs/fastapi-boilerplate)](./LICENSE)
[![Powered by NaNLABS](https://img.shields.io/badge/powered%20by-NaNLABS-111827)](https://www.nanlabs.com/)

Opinionated FastAPI template for teams that want a strong backend baseline from day zero: clear layering, predictable API contracts, strict quality gates, and a reproducible developer workflow.

## Why Teams Pick This

- Versioned API foundation (`/api/v1`) with thin endpoints and service-first logic.
- Consistent response envelope (`APIResponse[T]`) for success and errors.
- Strong quality defaults (`Ruff`, `MyPy strict`, `Bandit`, `pytest`).
- Dev Container-first setup for low-friction onboarding.

## Scope

**In scope:** versioned REST API baseline, layered structure (`endpoints/services/schemas/core/db`), `APIResponse[T]` envelope, SQLAlchemy + Alembic with SQLite default and PostgreSQL support, quality gates, Dev Container workflow.

**Out of scope:** authentication, background workers, caching, cloud-specific deployment defaults, domain modules beyond the sample `projects` resource.

**Extension points:** add resources under `app/api/endpoints/v1/`, `app/api/schemas/v1/`, `app/api/services/`; map new exceptions in `app/api/exceptions.py`; extend seed logic in `app/db/seed_data.py`.

**Not the right fit if:** you need event-driven or async-first architecture, a full product framework with RBAC/multitenancy, or strict vendor platform constraints.

## Quick Start (10-15 minutes) 🚀

Development happens inside the Dev Container.

```bash
# VS Code / Cursor
# Open project, then choose "Reopen in Container"

# CLI alternative
devcontainer up --workspace-folder .
```

Inside the container:

```bash
make install-dev
make init-db
make dev
```

Validate your setup:

```bash
curl -s http://localhost:8000/ping
curl -s http://localhost:8000/api/v1/healthz
make test
make all-checks
```

If a `make` command fails with "must run inside the Dev Container", follow the setup above first.

## Host vs Dev Container

- Host machine: editor, AI tooling, and `git` commands.
- Dev Container: runtime and project commands (`make dev`, `make test`, `make all-checks`, migrations).

Bridge command from host terminal:

```bash
devcontainer exec --workspace-folder . make <target>
```

## Common Commands 🛠️

```bash
make bootstrap      # One-shot setup (install + init + doctor + docs check)
make dev            # Run API with auto-reload
make test-unit      # Fast local loop
make test           # Full test suite
make all-checks     # Ruff + MyPy + Bandit + docs checks
make help           # Full command list
```

For all targets and migration commands, see `docs/COMMANDS.md`.

## Documentation Map 📚

| Doc | Why read it |
|---|---|
| [Docs Home](./docs/README.md) | Pick your path by role and goal |
| [Getting Started](./docs/GETTING_STARTED.md) | First run and setup validation |
| [Commands Reference](./docs/COMMANDS.md) | Every available `make` command grouped by purpose |
| [Development Guide](./docs/DEVELOPMENT.md#end-to-end-walkthrough) | Build your first feature end-to-end |
| [Development Guide](./docs/DEVELOPMENT.md) | Team conventions, delivery workflow, and first-feature walkthrough |
| [API Reference](./docs/API.md) | Endpoint contract and response envelope |
| [Architecture](./docs/ARCHITECTURE.md) | Layer boundaries and design decisions |
| [Database Guide](./docs/DATABASE.md) | SQLite/PostgreSQL and migration workflow |
| [Testing Guide](./docs/TESTING.md) | Test structure, fixtures, and assertions |
| [Tips and Tricks](./docs/TIPS_AND_TRICKS.md) | Practical troubleshooting shortcuts |
| [Bootstrap Checklist](./docs/BOOTSTRAP_CHECKLIST.md) | Convert this template into your product repo |

## Contributing

Contributions are welcome. Start with `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.
