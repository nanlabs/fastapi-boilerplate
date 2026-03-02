# Database Guide

## Default: SQLite

No extra configuration is needed. The database file is created at `data/app.db` on first run.

```bash
make dev
```

The default SQLite file is stored at `data/app.db`.

## Switching to PostgreSQL

Set only `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

Install driver:

```bash
uv add psycopg2-binary
```

## Dev Container + PostgreSQL

Add a compose file in `.devcontainer/docker-compose.yml` with `app` and `db` services, then point `devcontainer.json` to it and set `DATABASE_URL=postgresql://postgres:postgres@db:5432/boilerplate`.

Rebuild container after changes.

## Migration history policy

This repository contains Alembic history inherited from earlier template iterations.

- The **current intended domain** for this boilerplate is the `projects` resource.
- Some historical revisions include legacy tables (`experiments`, `dataset_files`, `model_types`, etc.) that are removed in later revisions.
- A full migration run still converges to the current schema expected by the application.

If you bootstrap a new product from this template, you can keep this history for compatibility or squash/reset migrations in your derived project once your team agrees on a migration baseline.

## Migrations

```bash
make migration-create MESSAGE="add users table"
make migration-upgrade
make migration-current
make migration-history
make migration-downgrade
```

### Recommended workflow for new resources

1. Update model(s) in `app/db/models/`.
2. Run `make migration-create MESSAGE="..."`.
3. Review generated migration before applying.
4. Apply with `make migration-upgrade`.
5. Add/update tests that verify behavior against the migrated schema.

## Troubleshooting

- `sqlite3.OperationalError: unable to open database file`: run `make init-db`.
- PostgreSQL connection errors: verify DB service and `DATABASE_URL`.
- Alembic multiple heads: create a merge migration.

## Related docs

- `CONFIGURATION.md` for environment variable setup.
- `DEVELOPMENT.md` for model -> migration -> endpoint workflow.
- `COMMANDS.md` for full migration command reference.
