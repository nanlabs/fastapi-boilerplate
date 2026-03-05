"""Remove experiment and dataset tables

Revision ID: 1a2b3c4d5e6f
Revises: f09b1c2d3e4f
Create Date: 2026-02-23 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: str | None = "f09b1c2d3e4f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Drop Thorcast/ML-specific tables no longer used by the app."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "experiments" in tables:
        op.drop_table("experiments")

    if "dataset_files" in tables:
        op.drop_table("dataset_files")


def downgrade() -> None:
    """Recreate tables dropped in this migration."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "dataset_files" not in tables:
        op.create_table(
            "dataset_files",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("path", sa.String(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_dataset_files_deleted_at"),
            "dataset_files",
            ["deleted_at"],
            unique=False,
        )
        op.create_index(op.f("ix_dataset_files_name"), "dataset_files", ["name"], unique=False)
        op.create_index(op.f("ix_dataset_files_path"), "dataset_files", ["path"], unique=False)

    if "experiments" not in tables:
        op.create_table(
            "experiments",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("status", sa.String(), server_default=sa.text("'draft'"), nullable=False),
            sa.Column("external_experiment_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("current_step", sa.Integer(), server_default=sa.text("0"), nullable=False),
            sa.Column("dataset_file_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["dataset_file_id"], ["dataset_files.id"], name="fk_experiments_dataset_file_id", ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_experiments_deleted_at"), "experiments", ["deleted_at"], unique=False)
        op.create_index(op.f("ix_experiments_external_experiment_id"), "experiments", ["external_experiment_id"], unique=True)
        op.create_index(op.f("ix_experiments_name"), "experiments", ["name"], unique=False)
        op.create_index(op.f("ix_experiments_project_id"), "experiments", ["project_id"], unique=False)
        op.create_index(op.f("ix_experiments_dataset_file_id"), "experiments", ["dataset_file_id"], unique=False)
