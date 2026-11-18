"""correcao.boa_correcao (exemplo modelo) e ia_trecho.ignorado (tirado de uso, nada apagado)

Revision ID: 0024
Revises: 0023
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0024"
down_revision: Union[str, None] = "0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("correcao", sa.Column("boa_correcao", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("ia_trecho", sa.Column("ignorado", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("ia_trecho", "ignorado")
    op.drop_column("correcao", "boa_correcao")
