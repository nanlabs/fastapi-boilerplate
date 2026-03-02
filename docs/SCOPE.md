# Scope

## What is in scope

- FastAPI REST API baseline with versioned routes (`/api/v1`).
- Layered structure (`endpoints`, `services`, `schemas`, `core`, `db`).
- Standard response envelope (`APIResponse[T]`) for success/error consistency.
- SQLAlchemy + Alembic database setup with SQLite default and PostgreSQL support.
- Quality gates for linting, typing, security scan, and tests.
- Dev Container-first developer workflow.

## What is intentionally out of scope

- Authentication/authorization implementation details.
- Background workers and job orchestration.
- Caching strategy and invalidation policies.
- Domain-specific modules beyond the sample `projects` resource.
- Cloud-provider specific deployment defaults.

## Expected extension points

- Add more resources under `app/api/endpoints/v1/`, `app/api/schemas/v1/`, `app/api/services/`.
- Add domain-specific exceptions in `app/api/exceptions.py` and map centrally.
- Add infra/deployment strategy in a separate folder/repository as needed.
- Extend seed behavior in `app/db/seed_data.py` based on product requirements.

## When not to use this boilerplate

- If your team needs an event-driven or async-first architecture from day one.
- If you need a full product framework with built-in auth, RBAC, and multitenancy.
- If your project has strict vendor platform constraints requiring a different runtime model.
