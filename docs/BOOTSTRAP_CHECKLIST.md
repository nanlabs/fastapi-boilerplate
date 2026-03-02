# Bootstrap Checklist

Use this checklist when creating a new product repository from this boilerplate.

## 1) Rename and identity

- Update app name/version defaults in `app/core/config.py`.
- Update project metadata in `pyproject.toml`.
- Replace boilerplate wording in `README.md` and root docs.

## 2) Domain setup

- Decide if `Project` remains as your first domain entity or replace it.
- Add domain models/schemas/services/endpoints for your first real feature.
- Define stable `dev_code` conventions for your domain.

## 3) Data layer

- Choose DB target (SQLite for local only or PostgreSQL for all envs).
- Validate migration strategy with your team (keep or squash baseline history).
- Add initial migrations and verify upgrade/downgrade behavior.

## 4) Quality and CI

- Confirm `make test` and `make all-checks` pass in CI.
- Enforce branch and PR policies (reviews, status checks).
- Keep issue and PR templates aligned with team workflow.

## 5) Runtime and delivery

- Define environment matrix (dev/staging/prod).
- Add deployment pipeline and secrets management process.
- Document operational runbooks (health checks, logs, rollback basics).

## 6) Documentation done criteria

- `SCOPE.md` updated for product boundaries.
- `API.md` reflects real endpoints and examples.
- `DEVELOPMENT.md` includes project-specific conventions.
- `REFERENCES.md` includes only relevant links for your stack.
