"""figura da questao: Tema.imagem

Revision ID: 0003
Revises: 0002
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tema") as b:
        b.add_column(sa.Column("imagem", sa.String(255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("tema") as b:
        b.drop_column("imagem")
