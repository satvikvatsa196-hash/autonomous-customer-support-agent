"""Add hashed_password

Revision ID: da42f6b73242
Revises: 6e2cc357645c
Create Date: 2026-07-17 15:16:15.271316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da42f6b73242'
down_revision: Union[str, None] = '6e2cc357645c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(255), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'hashed_password')
