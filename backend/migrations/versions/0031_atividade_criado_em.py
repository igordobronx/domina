"""data de criacao da atividade (para listar as mais recentes primeiro)

Revision ID: 0031
Revises: 0030
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0031"
down_revision: Union[str, None] = "0030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite nao aceita default now() em ALTER TABLE: adiciona sem default e preenche (o model ja poe o default nas novas)
    op.add_column("atividade", sa.Column("criado_em", sa.DateTime(), nullable=True))
    op.execute("UPDATE atividade SET criado_em = CURRENT_TIMESTAMP")


def downgrade() -> None:
    op.drop_column("atividade", "criado_em")
