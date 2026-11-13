"""tema.alternativas (questao objetiva estilo ENEM)

Revision ID: 0009
Revises: 0008
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tema") as b:
        b.add_column(sa.Column("alternativas", sa.JSON, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("tema") as b:
        b.drop_column("alternativas")
