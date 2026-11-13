"""meta e meta_concluida (niveis e metas dos alunos)

Revision ID: 0011
Revises: 0010
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "meta",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("escola_id", UUID, sa.ForeignKey("escola.id"), nullable=False),
        sa.Column("criado_por", UUID, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("titulo", sa.String(150), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("alvo", sa.Numeric(7, 2), nullable=False),
        sa.Column("materia_id", UUID, sa.ForeignKey("materia.id")),
        sa.Column("competencia", sa.String(2)),
        sa.Column("pontos", sa.Integer, nullable=False),
        sa.Column("inicio", sa.Date, nullable=False),
        sa.Column("fim", sa.Date),
        sa.Column("turma_id", UUID, sa.ForeignKey("turma.id")),
        sa.Column("aluno_id", UUID, sa.ForeignKey("usuario.id")),
        sa.Column("ativa", sa.Boolean, nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "meta_concluida",
        sa.Column("meta_id", UUID, sa.ForeignKey("meta.id"), primary_key=True),
        sa.Column("aluno_id", UUID, sa.ForeignKey("usuario.id"), primary_key=True),
        sa.Column("concluida_em", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("meta_concluida")
    op.drop_table("meta")
