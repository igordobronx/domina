"""exercicio.grupo_id e exercicio.ordem (um exercicio com varias questoes)

Revision ID: 0036
Revises: 0035
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0036"
down_revision: Union[str, None] = "0035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("exercicio", sa.Column("grupo_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("exercicio", sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("exercicio", "ordem")
    op.drop_column("exercicio", "grupo_id")
