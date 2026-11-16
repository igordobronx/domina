"""exercicio gerado pela IA para um aluno (plano de estudo): aluno_id

As demais colunas (titulo, alternativas, resposta_correta, explicacao, criado_em) ja vieram na 0014.

Revision ID: 0019
Revises: 0018
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.add_column(sa.Column("aluno_id", postgresql.UUID(as_uuid=True), nullable=True))
        b.create_foreign_key("fk_exercicio_aluno", "usuario", ["aluno_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.drop_constraint("fk_exercicio_aluno", type_="foreignkey")
        b.drop_column("aluno_id")
