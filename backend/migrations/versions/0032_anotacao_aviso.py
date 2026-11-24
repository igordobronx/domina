"""marcas do professor sobre a foto (anotacao) e avisos (notificacoes) para o usuario

Revision ID: 0032
Revises: 0031
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0032"
down_revision: Union[str, None] = "0031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "anotacao",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("submissao_id", UUID, sa.ForeignKey("submissao.id"), nullable=False),
        sa.Column("pagina", sa.Integer, nullable=False),
        sa.Column("x", sa.Float, nullable=False),
        sa.Column("y", sa.Float, nullable=False),
        sa.Column("largura", sa.Float, nullable=False),
        sa.Column("altura", sa.Float, nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("comentario", sa.Text, nullable=False),
        sa.Column("criado_por", UUID, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_anotacao_submissao_id", "anotacao", ["submissao_id"])
    op.create_table(
        "aviso",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("usuario_id", UUID, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("texto", sa.String(255), nullable=False),
        sa.Column("submissao_id", UUID, sa.ForeignKey("submissao.id"), nullable=True),
        sa.Column("lido", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_aviso_usuario_id", "aviso", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_aviso_usuario_id", "aviso")
    op.drop_table("aviso")
    op.drop_index("ix_anotacao_submissao_id", "anotacao")
    op.drop_table("anotacao")
