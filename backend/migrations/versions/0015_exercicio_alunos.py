"""exercicio.alunos: exercicio so para alguns alunos da turma (nulo = turma toda)

Revision ID: 0015
Revises: 0014
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.add_column(sa.Column("alunos", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.drop_column("alunos")
