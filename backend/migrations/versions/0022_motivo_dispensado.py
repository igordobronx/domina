"""correcao.motivo_dispensado: o professor recusou virar instrucao o motivo desta correcao

Revision ID: 0022
Revises: 0021
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("correcao", sa.Column("motivo_dispensado", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("correcao", "motivo_dispensado")
