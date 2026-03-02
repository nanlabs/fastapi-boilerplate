# FastAPI Boilerplate - Development Makefile
#
# This project supports development with Dev Containers
# Requirements:
# - VS Code with Dev Containers extension, OR
# - Dev Container CLI: https://containers.dev/supporting#devcontainer-cli
#
# All commands are designed to run INSIDE the dev container environment.

.PHONY: help ensure-devcontainer install install-dev bootstrap doctor check-docs clean test test-unit test-integration test-coverage lint format autofix type-check all-checks run dev init-db migration-create migration-upgrade migration-downgrade migration-history migration-current migration-stamp migration-downgrade-to migration-upgrade-to migration-show migration-merge

DIR ?= .

# Default target
help:
	@echo ""
	@echo "FastAPI Boilerplate - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "[ENV] Environment & Dependencies:"
	@echo "  install         - Install production dependencies with UV"
	@echo "  install-dev     - Install development dependencies with UV"
	@echo "  bootstrap       - One-shot local setup (install + init + doctor + checks)"
	@echo "  doctor          - Validate local development environment"
	@echo "  clean           - Clean build artifacts and caches"
	@echo ""
	@echo "[TEST] Testing:"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration- Run integration tests only"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo ""
	@echo "[QUALITY] Code Quality:"
	@echo "  lint            - Run code linting with ruff"
	@echo "  format          - Format code with ruff"
	@echo "  autofix         - Auto-fix code formatting and imports"
	@echo "  type-check      - Run type checking with mypy"
	@echo "  check-docs      - Validate markdown docs links"
	@echo "  all-checks      - Run all code quality checks"
	@echo ""
	@echo "[DEV] Development:"
	@echo "  run             - Run FastAPI server"
	@echo "  dev             - Run FastAPI server with auto-reload"
	@echo "  init-db         - Initialize database (runs migrations + seed data)"
	@echo ""
	@echo "[DB] Database Migrations (Alembic):"
	@echo "  Note: init-db automatically runs migrations. Use these for manual control:"
	@echo "  migration-create      - Create a new migration (usage: make migration-create MESSAGE='description')"
	@echo "  migration-upgrade     - Upgrade database to head revision"
	@echo "  migration-upgrade-to  - Upgrade to specific revision (usage: make migration-upgrade-to REVISION='revision_id')"
	@echo "  migration-downgrade   - Downgrade database by one revision"
	@echo "  migration-downgrade-to - Downgrade to specific revision (usage: make migration-downgrade-to REVISION='revision_id')"
	@echo "  migration-history     - Show migration history"
	@echo "  migration-current     - Show current database revision"
	@echo "  migration-show       - Alias for migration-current"
	@echo "  migration-stamp       - Stamp database with revision (usage: make migration-stamp REVISION='revision_id')"
	@echo "  migration-merge       - Merge migration branches (usage: make migration-merge REVISIONS='rev1,rev2' MESSAGE='description')"
	@echo ""
	@echo "[ARGS] Optional directory argument:"
	@echo "  lint, format, autofix, type-check, all-checks"
	@echo "  Examples: make lint app | make all-checks tests | make all-checks DIR=app"
	@echo ""
	@echo "[FLOWS] Suggested workflows:"
	@echo "  First run:     make bootstrap"
	@echo "  Daily dev:     make test-unit && make autofix && make all-checks"
	@echo "  Pre-PR:        make test && make all-checks"
	@echo ""

ensure-devcontainer:
	@if [ "$$CI" = "true" ] || [ "$$CI" = "1" ]; then \
		exit 0; \
	fi
	@if [ ! -f /.dockerenv ]; then \
		echo "ERROR: This project must run inside the Dev Container."; \
		echo ""; \
		echo "Read README.md -> 'Quick Start (10-15 minutes)' for setup."; \
		echo "Open the repo and choose 'Reopen in Container' or run:"; \
		echo "  devcontainer up --workspace-folder ."; \
		exit 1; \
	fi

# Install production dependencies
install: ensure-devcontainer
	@echo "INFO: Installing production dependencies with UV..."
	uv sync --no-dev
	@echo "OK: Installation complete."

# Install development dependencies
install-dev: ensure-devcontainer
	@echo "INFO: Installing all dependencies with UV..."
	uv sync
	@echo "OK: Installation complete."

bootstrap: ensure-devcontainer
	@echo "INFO: Running bootstrap workflow..."
	$(MAKE) install-dev
	$(MAKE) init-db
	$(MAKE) doctor
	$(MAKE) check-docs
	@echo "OK: Bootstrap completed."

doctor: ensure-devcontainer
	@echo "INFO: Running environment diagnostics..."
	uv run python scripts/doctor.py

check-docs: ensure-devcontainer
	@echo "INFO: Running documentation checks..."
	uv run python scripts/check_docs.py

# Clean up build artifacts and caches
clean:
	@echo "INFO: Cleaning build artifacts and caches..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf build/
	rm -rf dist/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/
	@echo "OK: Cleanup complete."

# Run all tests
test: ensure-devcontainer
	@echo "INFO: Running all tests..."
	uv run pytest

# Run unit tests only
test-unit: ensure-devcontainer
	@echo "INFO: Running unit tests..."
	uv run pytest tests/unit -m "not integration and not slow"

# Run integration tests only
test-integration: ensure-devcontainer
	@echo "INFO: Running integration tests..."
	uv run pytest tests/integration -m integration

# Run tests with coverage
test-coverage: ensure-devcontainer
	@echo "INFO: Running tests with coverage..."
	uv run pytest --cov=app --cov-report=html --cov-report=term
	@echo "OK: Coverage report generated in htmlcov/"

# Run code linting
lint: ensure-devcontainer
	@echo "INFO: Running code linting..."
	uv run ruff check $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

# Format code
format: ensure-devcontainer
	@echo "INFO: Formatting code..."
	uv run ruff format $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

# Auto-fix code formatting and imports
autofix: ensure-devcontainer
	@echo "INFO: Auto-fixing code..."
	uv run ruff check --fix $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run ruff format $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

# Type checking
type-check: ensure-devcontainer
	@echo "INFO: Running type checking..."
	uv run mypy $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

all-checks: ensure-devcontainer
	@echo "INFO: Running all code quality checks..."
	uv run ruff check $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run ruff format --check $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run mypy $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run bandit -c pyproject.toml -r $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	$(MAKE) check-docs
	@echo "OK: All code quality checks complete."

%:
	@:

# Run FastAPI server
run: ensure-devcontainer
	@echo "INFO: Starting FastAPI server..."
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run FastAPI server with auto-reload
dev: ensure-devcontainer
	@echo "INFO: Starting FastAPI server with auto-reload..."
	uv run python scripts/devserver.py

# Initialize database
init-db: ensure-devcontainer
	@echo "INFO: Initializing database..."
	uv run python scripts/init_db.py

# Create a new migration
migration-create: ensure-devcontainer
	@$(if $(MESSAGE),,echo ERROR: MESSAGE is required. Usage: make migration-create MESSAGE='description' && exit 1)
	@echo "INFO: Creating new migration: $(MESSAGE)"
	uv run alembic revision --autogenerate -m "$(MESSAGE)"

# Upgrade database to head revision
migration-upgrade: ensure-devcontainer
	@echo "INFO: Upgrading database to head revision..."
	uv run alembic upgrade head

# Downgrade database by one revision
migration-downgrade: ensure-devcontainer
	@echo "INFO: Downgrading database by one revision..."
	uv run alembic downgrade -1

# Show migration history
migration-history: ensure-devcontainer
	@echo "INFO: Migration history:"
	uv run alembic history

# Show current database revision
migration-current: ensure-devcontainer
	@echo "INFO: Current database revision:"
	uv run alembic current

# Alias for migration-current
migration-show: migration-current

# Stamp database with a specific revision
migration-stamp: ensure-devcontainer
	@$(if $(REVISION),,echo ERROR: REVISION is required. Usage: make migration-stamp REVISION='revision_id' && exit 1)
	@echo "INFO: Stamping database with revision: $(REVISION)"
	uv run alembic stamp "$(REVISION)"

# Upgrade database to a specific revision
migration-upgrade-to: ensure-devcontainer
	@$(if $(REVISION),,echo ERROR: REVISION is required. Usage: make migration-upgrade-to REVISION='revision_id' && exit 1)
	@echo "INFO: Upgrading database to revision: $(REVISION)"
	uv run alembic upgrade "$(REVISION)"

# Downgrade database to a specific revision
migration-downgrade-to: ensure-devcontainer
	@$(if $(REVISION),,echo ERROR: REVISION is required. Usage: make migration-downgrade-to REVISION='revision_id' && exit 1)
	@echo "INFO: Downgrading database to revision: $(REVISION)"
	uv run alembic downgrade "$(REVISION)"

# Merge migration branches
migration-merge: ensure-devcontainer
	@$(if $(REVISIONS),,echo ERROR: REVISIONS is required. Usage: make migration-merge REVISIONS='rev1,rev2' MESSAGE='description' && exit 1)
	@$(if $(MESSAGE),,echo ERROR: MESSAGE is required. Usage: make migration-merge REVISIONS='rev1,rev2' MESSAGE='description' && exit 1)
	@echo "INFO: Merging migration branches: $(REVISIONS)"
	uv run alembic merge -m "$(MESSAGE)" $(REVISIONS)
