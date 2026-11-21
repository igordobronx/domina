"""tema.subtopico (assunto da questao; o professor escreve ou a IA identifica)

Revision ID: 0033
Revises: 0032
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0033"
down_revision: Union[str, None] = "0032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tema", sa.Column("subtopico", sa.String(150), nullable=True))


def downgrade() -> None:
    op.drop_column("tema", "subtopico")
