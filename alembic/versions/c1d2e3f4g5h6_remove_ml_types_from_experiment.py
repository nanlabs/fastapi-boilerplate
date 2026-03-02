"""Remove ML types from experiment

Revision ID: c1d2e3f4g5h6
Revises: ae7df3c1a51a
Create Date: 2026-02-06 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: str | None = 'ae7df3c1a51a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove experiment_type and model_type tables and foreign keys from experiments."""
    # Drop foreign key constraints from experiments table
    with op.batch_alter_table('experiments') as batch_op:
        batch_op.drop_index('ix_experiments_experiment_type_id')
        batch_op.drop_index('ix_experiments_model_type_id')
        batch_op.drop_column('experiment_type_id')
        batch_op.drop_column('model_type_id')

    # Drop experiment_types and model_types tables
    op.drop_table('experiment_types')
    op.drop_table('model_types')


def downgrade() -> None:
    """Recreate experiment_type and model_type tables and add foreign keys back."""
    # Recreate model_types table
    op.create_table(
        'model_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_types_name'), 'model_types', ['name'], unique=False)

    # Recreate experiment_types table
    op.create_table(
        'experiment_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_types_name'), 'experiment_types', ['name'], unique=False)

    # Add foreign key columns back to experiments table
    with op.batch_alter_table('experiments') as batch_op:
        batch_op.add_column(sa.Column('experiment_type_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('model_type_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_experiments_experiment_type_id', ['experiment_type_id'])
        batch_op.create_index('ix_experiments_model_type_id', ['model_type_id'])
        batch_op.create_foreign_key(
            'fk_experiments_experiment_type_id',
            'experiment_types',
            ['experiment_type_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_foreign_key(
            'fk_experiments_model_type_id',
            'model_types',
            ['model_type_id'],
            ['id'],
            ondelete='SET NULL'
        )
