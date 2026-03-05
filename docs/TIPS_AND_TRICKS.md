# Tips and Tricks

## Local productivity

- Use `make test-unit` for fast feedback while coding.
- Run `make autofix` before `make all-checks` to reduce formatting churn.
- Keep Swagger open at `http://localhost:8000/docs` while iterating endpoints.

## Debugging patterns

- Add a custom `X-Request-ID` header to correlate client calls with logs.
- Use `DEBUG=true` for readable local logs; keep `DEBUG=false` for JSON logs.
- If a handler returns 500, verify mapped exceptions in `app/core/exception_handlers.py`.

## Database workflow

- Prefer small, reviewable migrations.
- Validate migration output after `make migration-create MESSAGE="..."`.
- Re-run `make init-db` if local SQLite state gets out of sync.

## API contract hygiene

- Reuse `make_item_response`, `make_list_response`, `make_error_response`.
- Keep `dev_code` stable once clients consume it.
- Include both success and error scenarios in endpoint tests.

## Cross-platform guardrails

- Keep Git line endings consistent:
  - Linux/macOS: `git config --global core.autocrlf input`
  - Windows: `git config --global core.autocrlf true`
- This repo ships a `.gitattributes` file to reduce host/container line-ending drift.
- If you see many unexpected diffs, run:
  - `git add --renormalize .`
  - inspect with `git status` before committing.

## Git credentials in Dev Container

- HTTPS workflow: host credential helper is usually reused in container.
- SSH workflow: ensure host agent is running and key loaded (`ssh-add`).
- Reference:
  `https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials`

## Related docs

- `GETTING_STARTED.md` for first-run troubleshooting.
- `COMMANDS.md` for full command options.
- `DEVELOPMENT.md` for implementation standards.
