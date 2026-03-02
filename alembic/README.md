# Alembic Notes

## Why migration history looks longer than current models

This boilerplate evolved from previous internal iterations. Some historical revisions reference tables that are no longer part of the current template domain.

Current app scope uses the `projects` table model from `app/db/models/project.py`.

## What matters for consumers

- Running migrations to `head` produces the schema expected by current code.
- New features should add forward-only revisions from current `head`.
- If you fork this boilerplate for a greenfield product, your team may decide to squash/reset migration history after initial adoption.

## Team guideline

Before merging a migration:

1. Ensure autogeneration output is reviewed manually.
2. Ensure downgrade path is valid for local/dev environments.
3. Ensure tests cover behavior tied to schema changes.

For the complete migration command set, see `docs/COMMANDS.md`.
