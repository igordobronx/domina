"""cadeia de hash no evento_seguranca

Revision ID: 0006
Revises: 0005
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("evento_seguranca") as b:
        b.add_column(sa.Column("seq", sa.BigInteger, nullable=True))
        b.add_column(sa.Column("hash_anterior", sa.String(64), nullable=True))
        b.add_column(sa.Column("hash", sa.String(64), nullable=True))
        b.create_unique_constraint("uq_evento_seguranca_seq", ["seq"])


def downgrade() -> None:
    with op.batch_alter_table("evento_seguranca") as b:
        b.drop_constraint("uq_evento_seguranca_seq", type_="unique")
        b.drop_column("hash")
        b.drop_column("hash_anterior")
        b.drop_column("seq")
