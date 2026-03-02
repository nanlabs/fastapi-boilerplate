# Configuration Directory

This directory contains runtime configuration assets loaded by the application.

## `seed_data.yaml`

`seed_data.yaml` is an optional seed configuration file read during database initialization.

Current behavior:

- The file is parsed and validated on startup (`make init-db` or application lifespan init).
- If the file is missing, initialization continues without error.
- By default, this boilerplate does **not** insert, update, or delete records from `seed_data.yaml`.

Why this exists:

- Teams can extend `app/db/seed_data.py` and `app/db/init.py` to implement project-specific seeding logic.
- Keeping seed behavior explicit avoids hidden data mutations in new projects.

For full database setup and migration behavior, see `docs/DATABASE.md`.

## Related docs

- `docs/CONFIGURATION.md` for environment variables.
- `docs/GETTING_STARTED.md` for first-run setup.
- `docs/COMMANDS.md` for `make init-db` and environment commands.
