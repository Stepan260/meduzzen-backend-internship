"""add default value to action uuid

Revision ID: 5fe9d9cae265
Revises: f3c7cf12f8a8
Create Date: 2024-04-29 01:28:42.437028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5fe9d9cae265'
down_revision: Union[str, None] = 'f3c7cf12f8a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_actions_uuid', table_name='actions')


def downgrade() -> None:
    op.create_index('ix_actions_uuid', 'actions', ['uuid'], unique=False)
