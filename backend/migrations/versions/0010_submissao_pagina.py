"""submissao_pagina (varias fotos por envio)

Revision ID: 0010
Revises: 0009
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "submissao_pagina",
        sa.Column("submissao_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissao.id"), primary_key=True),
        sa.Column("ordem", sa.Integer, primary_key=True),
        sa.Column("caminho", sa.String(500), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("submissao_pagina")
