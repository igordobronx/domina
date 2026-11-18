"""IA aprende com exercicios marcados pelo professor; professor marca explicacao ruim da IA

Revision ID: 0023
Revises: 0022
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0023"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("correcao", sa.Column("explicacao_ruim", sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table("ia_trecho") as b:
        b.add_column(sa.Column("exercicio_resposta_id", sa.UUID(), nullable=True))
        b.create_foreign_key("fk_ia_trecho_exercicio_resposta", "exercicio_resposta", ["exercicio_resposta_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("ia_trecho") as b:
        b.drop_constraint("fk_ia_trecho_exercicio_resposta", type_="foreignkey")
        b.drop_column("exercicio_resposta_id")
    op.drop_column("correcao", "explicacao_ruim")
