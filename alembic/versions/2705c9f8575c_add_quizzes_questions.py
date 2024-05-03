"""add_quizzes_questions

Revision ID: 2705c9f8575c
Revises: 5fe9d9cae265
Create Date: 2024-05-01 20:14:58.528121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '2705c9f8575c'
down_revision: Union[str, None] = '5fe9d9cae265'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('quizzes',
                    sa.Column('uuid', sa.UUID(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('frequency_days', sa.Integer(), nullable=False),
                    sa.Column('company_uuid', sa.UUID(), nullable=True),
                    sa.ForeignKeyConstraint(['company_uuid'], ['companies.uuid'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('uuid')
                    )
    op.create_table('questions',
                    sa.Column('uuid', sa.UUID(), nullable=False),
                    sa.Column('quiz_uuid', sa.UUID(), nullable=True),
                    sa.Column('text', sa.Text(), nullable=False),
                    sa.Column('answer_choices', postgresql.ARRAY(sa.String()), nullable=False),
                    sa.Column('correct_answer', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(['quiz_uuid'], ['quizzes.uuid'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('uuid')
                    )


def downgrade() -> None:
    op.drop_table('questions')
    op.drop_table('quizzes')
