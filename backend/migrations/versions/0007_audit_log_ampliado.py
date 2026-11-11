"""audit_log: escola, IP, request_id, resultado e cadeia de hash

Revision ID: 0007
Revises: 0006
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("audit_log") as b:
        b.add_column(sa.Column("escola_id", UUID(as_uuid=True), nullable=True))
        b.add_column(sa.Column("ip", sa.String(45), nullable=True))
        b.add_column(sa.Column("request_id", sa.String(32), nullable=True))
        b.add_column(sa.Column("resultado", sa.String(10), nullable=True))
        b.add_column(sa.Column("seq", sa.BigInteger, nullable=True))
        b.add_column(sa.Column("hash_anterior", sa.String(64), nullable=True))
        b.add_column(sa.Column("hash", sa.String(64), nullable=True))
        b.create_unique_constraint("uq_audit_log_seq", ["seq"])
        b.create_index("ix_audit_log_escola_id", ["escola_id"])
    # linhas antigas: escola vem do autor (o gestor ja era filtrado assim); ficam fora da cadeia
    op.execute("UPDATE audit_log SET escola_id = (SELECT escola_id FROM usuario WHERE usuario.id = audit_log.usuario_id)")


def downgrade() -> None:
    with op.batch_alter_table("audit_log") as b:
        b.drop_index("ix_audit_log_escola_id")
        b.drop_constraint("uq_audit_log_seq", type_="unique")
        for c in ("hash", "hash_anterior", "seq", "resultado", "request_id", "ip", "escola_id"):
            b.drop_column(c)
