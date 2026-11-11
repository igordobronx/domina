"""log de seguranca: tabela evento_seguranca

Revision ID: 0005
Revises: 0004
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evento_seguranca",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), nullable=True),
        sa.Column("email_tentado", sa.String(254), nullable=True),
        sa.Column("ip", sa.String(45), nullable=False),
        sa.Column("request_id", sa.String(32), nullable=False),
        sa.Column("detalhe", sa.String(200), nullable=True),
    )
    op.create_index("ix_evento_seguranca_criado_em", "evento_seguranca", ["criado_em"])
    op.create_index("ix_evento_seguranca_tipo", "evento_seguranca", ["tipo"])


def downgrade() -> None:
    op.drop_table("evento_seguranca")
