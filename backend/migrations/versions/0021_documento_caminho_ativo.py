"""documento_base: caminho do arquivo e ativo (excluir = arquivar)

Revision ID: 0021
Revises: 0020
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: Union[str, None] = "0020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("documento_base") as b:
        b.add_column(sa.Column("caminho", sa.String(255), nullable=True))
        b.add_column(sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    with op.batch_alter_table("documento_base") as b:
        b.drop_column("ativo")
        b.drop_column("caminho")
