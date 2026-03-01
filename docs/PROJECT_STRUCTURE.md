# Project Structure

```text
fastapi-boilerplate/
|
├── app/                          # Application package
│   ├── main.py                   # FastAPI app and wiring
│   ├── api/
│   │   ├── endpoints/
│   │   │   └── v1/               # API v1 handlers
│   │   │       ├── __init__.py   # v1 APIRouter aggregate
│   │   │       ├── health.py     # GET /api/v1/healthz
│   │   │       └── projects.py   # CRUD /api/v1/projects
│   │   ├── schemas/
│   │   │   ├── common/           # Shared schemas across versions
│   │   │   │   ├── params.py     # Pagination, sorting, search params
│   │   │   │   └── responses.py  # APIResponse envelope + helpers
│   │   │   └── v1/
│   │   │       └── project.py    # ProjectCreate, ProjectUpdate, ProjectResponse
│   │   ├── services/             # Business logic (non-versioned)
│   │   │   ├── project_service.py
│   │   │   ├── dependencies.py
│   │   │   └── utils.py
│   │   ├── dependencies/
│   │   │   └── query_params.py
│   │   └── exceptions.py
│   ├── core/
│   │   ├── config.py
│   │   ├── middleware.py
│   │   ├── logging_config.py
│   │   └── exception_handlers.py
│   └── db/
│       ├── models/
│       ├── session.py
│       ├── init.py
│       └── seed_data.py
|
├── alembic/
├── tests/
├── docs/
├── scripts/
├── .devcontainer/
├── pyproject.toml
└── Makefile
```

## Layer rules

| Layer | Responsibility | Can import from |
|---|---|---|
| `endpoints/v1/` | HTTP: parse request, call service, return envelope | `services/`, `schemas/`, `dependencies/` |
| `services/` | Business logic and DB queries | `db/`, `schemas/`, `exceptions.py` |
| `schemas/` | Validation and serialization | External libs only |
| `core/` | Cross-cutting concerns | `schemas/`, `exceptions.py` |
| `db/` | ORM models and sessions | `core/config.py` |

Do not import `endpoints/` from services. Do not import services in schemas.
