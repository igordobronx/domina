"""tipo de material "OUTRO" (qualquer arquivo que nao seja apostila, rubrica, gabarito ou plano de aula)

Revision ID: 0030
Revises: 0029
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0030"
down_revision: Union[str, None] = "0029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Postgres: o tipo e um enum nativo e ADD VALUE nao roda dentro de transacao. SQLite: texto, nada a fazer.
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE tipodocumentoenum ADD VALUE IF NOT EXISTS 'OUTRO'")


def downgrade() -> None:
    pass  # Postgres nao remove valor de enum; "OUTRO" sobra sem efeito
