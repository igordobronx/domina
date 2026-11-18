"""ia_chamada: cada pedido ao modelo de fora e a resposta dele (material de treino da IA propria)

Revision ID: 0025
Revises: 0024
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0025"
down_revision: Union[str, None] = "0024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ia_chamada",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tarefa", sa.String(40), nullable=False),
        sa.Column("modelo", sa.String(100), nullable=False),
        sa.Column("entrada", sa.Text(), nullable=False),
        sa.Column("saida", sa.Text(), nullable=False),
        sa.Column("imagens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("materia_id", sa.UUID(), sa.ForeignKey("materia.id"), nullable=True),
        sa.Column("professor_id", sa.UUID(), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("correcao_id", sa.UUID(), sa.ForeignKey("correcao.id"), nullable=True),
        sa.Column("exportado_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ia_chamada_tarefa", "ia_chamada", ["tarefa"])
    op.create_index("ix_ia_chamada_correcao_id", "ia_chamada", ["correcao_id"])


def downgrade() -> None:
    op.drop_index("ix_ia_chamada_correcao_id", table_name="ia_chamada")
    op.drop_index("ix_ia_chamada_tarefa", table_name="ia_chamada")
    op.drop_table("ia_chamada")
