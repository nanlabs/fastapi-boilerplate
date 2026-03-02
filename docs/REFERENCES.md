# References

Curated references to extend this boilerplate intentionally. These links are selected for practical relevance, not completeness.

## NaNLABS References

## FastAPI backend patterns

- FastAPI base example  
  `https://github.com/nanlabs/backend-reference/tree/main/examples/fastapi-base`  
  Use when you need a minimal FastAPI baseline to compare structure choices.

- FastAPI CRUD example  
  `https://github.com/nanlabs/backend-reference/tree/main/examples/fastapi-crud`  
  Use when adding additional resources/endpoints beyond `projects`.

- FastAPI + PostgreSQL + Serverless  
  `https://github.com/nanlabs/backend-reference/tree/main/examples/fastapi-postgres-with-serverless`  
  Use when preparing deployment patterns for serverless platforms.

- FastAPI + Docker Compose (simple setup)  
  `https://github.com/nanlabs/backend-reference/tree/main/examples/fastapi-simple-docker-pip`  
  Use when you want a non-devcontainer local setup variant.

## Containers and local environments

- PostgreSQL with Docker Compose  
  `https://github.com/nanlabs/devops-reference/tree/main/examples/compose-postgres/`  
  Use when switching local development from SQLite to PostgreSQL.

- DevContainers intro  
  `https://github.com/nanlabs/devops-reference/tree/main/examples/devcontainers-intro/`  
  Use when adapting or hardening this repository's devcontainer workflow.

## CI/CD and quality automation

- Actionlint playground  
  `https://rhysd.github.io/actionlint/`  
  Use to validate and debug GitHub Actions workflows quickly.

- DangerJS with GitHub Actions  
  `https://github.com/nanlabs/devops-reference/tree/main/examples/github-actions-with-dangerjs`  
  Use when enforcing PR hygiene and review conventions automatically.

- Markdown lint workflow example  
  `https://github.com/nanlabs/devops-reference/tree/main/.github/workflows/markdownlint.yml`  
  Use when expanding docs quality gates beyond link checks.

## Security and platform maturity

- Secrets management guide  
  `https://github.com/nanlabs/devops-reference/tree/main/examples/the-ultimate-guide-to-secrets-management-for-developers`  
  Use before moving from local/dev to shared environments.

- Security assessment tools guide  
  `https://github.com/nanlabs/devops-reference/tree/main/examples/the-ultimate-guide-to-security-assessment-tools`  
  Use when defining static/dynamic analysis and security posture in CI.

## Official Documentation

- FastAPI docs: `https://fastapi.tiangolo.com/`  
  Use for router patterns, dependencies, request/response modeling.

- Pydantic docs: `https://docs.pydantic.dev/`  
  Use for schema validation patterns and model configuration.

- SQLAlchemy docs: `https://docs.sqlalchemy.org/`  
  Use for ORM behavior, query patterns, and transaction handling.

- Alembic docs: `https://alembic.sqlalchemy.org/`  
  Use for migration operations, branching, and merge-head workflows.

- uv docs: `https://docs.astral.sh/uv/`  
  Use for dependency/workspace management and reproducible environments.

- Ruff docs: `https://docs.astral.sh/ruff/`  
  Use for linting/formatting configuration and rule tuning.

## How to use this page

- Add only references that directly help maintain or extend this boilerplate.
- Prefer links with concrete examples over generic articles.
- Remove stale references during regular docs maintenance.
