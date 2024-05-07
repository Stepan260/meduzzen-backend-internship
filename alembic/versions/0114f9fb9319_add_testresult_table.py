"""Add Result table

Revision ID: 0114f9fb9319
Revises: 2705c9f8575c
Create Date: 2024-05-03 16:33:19.987641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0114f9fb9319'
down_revision: Union[str, None] = '2705c9f8575c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('results',
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('user_uuid', sa.UUID(), nullable=False),
    sa.Column('company_uuid', sa.UUID(), nullable=False),
    sa.Column('quiz_uuid', sa.UUID(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('total_questions', sa.Integer(), nullable=False),
    sa.Column('correct_answers', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_uuid'], ['companies.uuid'], ),
    sa.ForeignKeyConstraint(['quiz_uuid'], ['quizzes.uuid'], ),
    sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade() -> None:
    op.drop_table('results')