"""memoria da IA por materia (RAG): tabela ia_trecho; documento_base guarda o motivo do erro; correcao guarda por que o professor mudou a nota

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
    with op.batch_alter_table("documento_base") as b:
        b.add_column(sa.Column("detalhe", sa.String(255), nullable=True))
    with op.batch_alter_table("correcao") as b:
        b.add_column(sa.Column("motivo_mudanca", sa.Text(), nullable=True))
    op.create_table(
        "ia_trecho",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("materia_id", sa.UUID(), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("professor_id", sa.UUID(), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("origem", sa.String(20), nullable=False),
        sa.Column("documento_id", sa.UUID(), sa.ForeignKey("documento_base.id"), nullable=True),
        sa.Column("correcao_id", sa.UUID(), sa.ForeignKey("correcao.id"), nullable=True),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ia_trecho_materia_id", "ia_trecho", ["materia_id"])


def downgrade() -> None:
    op.drop_index("ix_ia_trecho_materia_id", table_name="ia_trecho")
    op.drop_table("ia_trecho")
    with op.batch_alter_table("correcao") as b:
        b.drop_column("motivo_mudanca")
    with op.batch_alter_table("documento_base") as b:
        b.drop_column("detalhe")
