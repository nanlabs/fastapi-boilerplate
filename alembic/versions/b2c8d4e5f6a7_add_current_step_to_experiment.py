"""Add current_step to experiment

Revision ID: b2c8d4e5f6a7
Revises: ae7df3c1a51a
Create Date: 2026-01-23 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c8d4e5f6a7"
down_revision: str | None = "ae7df3c1a51a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "experiments",
        sa.Column("current_step", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    op.drop_column("experiments", "current_step")
