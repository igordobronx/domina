"""tema.valor (pontos de cada questao; vazio = total da atividade dividido igual)

Revision ID: 0035
Revises: 0034
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0035"
down_revision: Union[str, None] = "0034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tema", sa.Column("valor", sa.Numeric(6, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("tema", "valor")
