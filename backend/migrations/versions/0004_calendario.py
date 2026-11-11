"""calendario: tabela evento e Atividade.prazo

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evento",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("escola_id", UUID(as_uuid=True), sa.ForeignKey("escola.id"), nullable=False),
        sa.Column("turma_id", UUID(as_uuid=True), sa.ForeignKey("turma.id"), nullable=True),
        sa.Column("criado_por", UUID(as_uuid=True), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("inicio", sa.Date, nullable=False),
        sa.Column("fim", sa.Date, nullable=True),
    )
    op.create_index("ix_evento_escola_inicio", "evento", ["escola_id", "inicio"])
    with op.batch_alter_table("atividade") as b:
        b.add_column(sa.Column("prazo", sa.Date, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("atividade") as b:
        b.drop_column("prazo")
    op.drop_table("evento")
