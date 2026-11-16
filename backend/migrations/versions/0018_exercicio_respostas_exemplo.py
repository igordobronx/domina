"""exercicio.respostas_exemplo: discursivo com mais de uma resposta de exemplo

Revision ID: 0018
Revises: 0017
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.add_column(sa.Column("respostas_exemplo", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.drop_column("respostas_exemplo")
