"""action

Revision ID: f3c7cf12f8a8
Revises: f77cee7db348
Create Date: 2024-04-28 13:37:51.815138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3c7cf12f8a8'
down_revision: Union[str, None] = 'f77cee7db348'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('actions',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('company_uuid', sa.UUID(), nullable=True),
    sa.Column('user_uuid', sa.UUID(), nullable=True),
    sa.Column('role', sa.Enum('ADMIN', 'MEMBER', 'OWNER', 'INVITED', 'REQUESTED', 'DECLINED', 'BLOCKED', name='companyrole'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['company_uuid'], ['companies.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_actions_role'), 'actions', ['role'], unique=False)
    op.create_index(op.f('ix_actions_uuid'), 'actions', ['uuid'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_actions_uuid'), table_name='actions')
    op.drop_index(op.f('ix_actions_role'), table_name='actions')
    op.drop_table('actions')
