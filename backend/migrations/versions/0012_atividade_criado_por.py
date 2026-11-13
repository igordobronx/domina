"""atividade.criado_por (a revisao do professor mostra so o que ele propos ou corrigiu)

Revision ID: 0012
Revises: 0011
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("atividade") as b:
        b.add_column(sa.Column("criado_por", postgresql.UUID(as_uuid=True), nullable=True))
        b.create_foreign_key("fk_atividade_criado_por", "usuario", ["criado_por"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("atividade") as b:
        b.drop_constraint("fk_atividade_criado_por", type_="foreignkey")
        b.drop_column("criado_por")
