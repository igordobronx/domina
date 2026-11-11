"""admin: escola ativa e plano, usuario sem escola, tamanho do documento

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("escola") as b:
        b.add_column(sa.Column("ativa", sa.Boolean(), server_default=sa.true(), nullable=False))
        b.add_column(sa.Column("plano_fixo", sa.Numeric(10, 2), server_default="1000", nullable=False))
        b.add_column(sa.Column("valor_por_aluno", sa.Numeric(10, 2), server_default="8", nullable=False))
    with op.batch_alter_table("usuario") as b:
        b.alter_column("escola_id", existing_type=sa.UUID(), nullable=True)
    with op.batch_alter_table("documento_base") as b:
        b.add_column(sa.Column("tamanho_bytes", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("documento_base") as b:
        b.drop_column("tamanho_bytes")
    with op.batch_alter_table("usuario") as b:
        b.alter_column("escola_id", existing_type=sa.UUID(), nullable=False)
    with op.batch_alter_table("escola") as b:
        b.drop_column("valor_por_aluno")
        b.drop_column("plano_fixo")
        b.drop_column("ativa")
