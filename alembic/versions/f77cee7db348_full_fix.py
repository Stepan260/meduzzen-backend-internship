"""full fix

Revision ID: f77cee7db348
Revises: 30d8de7666f4
Create Date: 2024-04-24 16:10:27.792351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f77cee7db348'
down_revision: Union[str, None] = '30d8de7666f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('companies',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('company_name', sa.String(), nullable=True),
    sa.Column('owner_uuid', sa.UUID(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('is_visible', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_uuid'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_companies_company_name'), 'companies', ['company_name'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_companies_company_name'), table_name='companies')
    op.drop_table('companies')
