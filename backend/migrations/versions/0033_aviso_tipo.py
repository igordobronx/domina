"""aviso: tipo, destino, chave (nao repetir alerta) e qtd (avisos agrupados)

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
    with op.batch_alter_table("aviso") as b:
        b.add_column(sa.Column("tipo", sa.String(20), nullable=False, server_default="GERAL"))
        b.add_column(sa.Column("destino", sa.String(20), nullable=True))
        b.add_column(sa.Column("chave", sa.String(80), nullable=True))
        b.add_column(sa.Column("qtd", sa.Integer, nullable=False, server_default="1"))
        b.create_index("ix_aviso_chave", ["chave"])


def downgrade() -> None:
    with op.batch_alter_table("aviso") as b:
        b.drop_index("ix_aviso_chave")
        for c in ("qtd", "chave", "destino", "tipo"):
            b.drop_column(c)
