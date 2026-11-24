"""assunto dentro da materia: a IA, os materiais, as atividades e os exercicios podem apontar para um

Revision ID: 0031
Revises: 0030
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0031"
down_revision: Union[str, None] = "0030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABELAS = ("documento_base", "ia_trecho", "atividade", "exercicio")


def upgrade() -> None:
    op.create_table(
        "assunto",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("professor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuario.id"), nullable=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assunto_materia_id", "assunto", ["materia_id"])
    for t in TABELAS:  # batch: o SQLite nao altera tabela direto
        with op.batch_alter_table(t) as b:
            b.add_column(sa.Column("assunto_id", postgresql.UUID(as_uuid=True), nullable=True))
            b.create_foreign_key(f"fk_{t}_assunto", "assunto", ["assunto_id"], ["id"])


def downgrade() -> None:
    for t in TABELAS:
        with op.batch_alter_table(t) as b:
            b.drop_constraint(f"fk_{t}_assunto", type_="foreignkey")
            b.drop_column("assunto_id")
    op.drop_index("ix_assunto_materia_id", "assunto")
    op.drop_table("assunto")
