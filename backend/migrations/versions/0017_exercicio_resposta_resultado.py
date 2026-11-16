"""exercicio_resposta.resultado: CERTA | PARCIAL | ERRADA (o professor pode dar parcialmente certa)

Revision ID: 0017
Revises: 0016
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exercicio_resposta") as b:
        b.add_column(sa.Column("resultado", sa.String(8), nullable=True))
    op.execute("UPDATE exercicio_resposta SET resultado = 'CERTA' WHERE correta = true")
    op.execute("UPDATE exercicio_resposta SET resultado = 'ERRADA' WHERE correta = false")


def downgrade() -> None:
    with op.batch_alter_table("exercicio_resposta") as b:
        b.drop_column("resultado")
