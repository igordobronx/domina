"""exercicios de pratica salvos e respostas do aluno (plano de estudo)

Revision ID: 0014
Revises: 0013
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.add_column(sa.Column("aluno_id", postgresql.UUID(as_uuid=True), nullable=True))
        b.add_column(sa.Column("titulo", sa.String(200), nullable=True))
        b.add_column(sa.Column("opcoes", sa.JSON, nullable=True))
        b.add_column(sa.Column("resposta_correta", sa.Integer, nullable=True))
        b.add_column(sa.Column("explicacao", sa.Text, nullable=True))
        b.add_column(sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=True))
        b.create_foreign_key("fk_exercicio_aluno", "usuario", ["aluno_id"], ["id"])
    with op.batch_alter_table("exercicio_resposta") as b:
        b.add_column(sa.Column("respondida_em", sa.DateTime, server_default=sa.func.now(), nullable=True))
        b.create_unique_constraint("uq_exercicio_resposta_aluno", ["exercicio_id", "aluno_id"])


def downgrade() -> None:
    with op.batch_alter_table("exercicio_resposta") as b:
        b.drop_constraint("uq_exercicio_resposta_aluno", type_="unique")
        b.drop_column("respondida_em")
    with op.batch_alter_table("exercicio") as b:
        b.drop_constraint("fk_exercicio_aluno", type_="foreignkey")
        for c in ("criado_em", "explicacao", "resposta_correta", "opcoes", "titulo", "aluno_id"):
            b.drop_column(c)
