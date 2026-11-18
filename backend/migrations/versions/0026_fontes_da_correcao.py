"""correcao.fontes_ia: o que da memoria do professor a IA usou naquela correcao

Revision ID: 0026
Revises: 0025
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0026"
down_revision: Union[str, None] = "0025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("correcao", sa.Column("fontes_ia", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("correcao", "fontes_ia")
