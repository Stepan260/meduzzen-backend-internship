"""add_notifications

Revision ID: 31f24cac5b5b
Revises: 0114f9fb9319
Create Date: 2024-05-07 21:35:17.304605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '31f24cac5b5b'
down_revision: Union[str, None] = '0114f9fb9319'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('notifications',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('user_uuid', sa.UUID(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade() -> None:
    op.drop_table('notifications')
