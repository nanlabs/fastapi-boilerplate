"""merge heads

Revision ID: f09b1c2d3e4f
Revises: 745db99c7486, c1d2e3f4g5h6
Create Date: 2026-02-09 00:00:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "f09b1c2d3e4f"
down_revision: str | tuple[str, str] | None = ("745db99c7486", "c1d2e3f4g5h6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge heads; no schema changes."""
    pass


def downgrade() -> None:
    """Downgrade merge; no schema changes."""
    pass
