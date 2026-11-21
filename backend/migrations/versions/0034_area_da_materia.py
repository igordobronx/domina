"""materia.area (exatas, natureza, humanas, linguagens, redacao, outra)

Revision ID: 0034
Revises: 0033
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0034"
down_revision: Union[str, None] = "0033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("materia", sa.Column("area", sa.String(20), nullable=False, server_default="OUTRA"))
    op.execute("UPDATE materia SET area = 'EXATAS' WHERE tipo = 'MATERIA_OBJETIVA'")
    op.execute("UPDATE materia SET area = 'REDACAO' WHERE tipo IN ('REDACAO_ENEM', 'REDACAO_OUTRO_VESTIBULAR')")


def downgrade() -> None:
    op.drop_column("materia", "area")
