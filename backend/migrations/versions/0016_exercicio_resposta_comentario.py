"""exercicio_resposta.comentario: comentario do professor (e certo/errado no discursivo)

Revision ID: 0016
Revises: 0015
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exercicio_resposta") as b:
        b.add_column(sa.Column("comentario", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("exercicio_resposta") as b:
        b.drop_column("comentario")
