"""erro_aluno (onde o aluno errou em exatas) e exercicio.erro_id

Revision ID: 0020
Revises: 0019
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "erro_aluno",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("aluno_id", UUID, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("materia_id", UUID, sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("atividade_id", UUID, sa.ForeignKey("atividade.id"), nullable=False),
        sa.Column("correcao_id", UUID, sa.ForeignKey("correcao.id"), nullable=False),
        sa.Column("criterio_id", UUID, sa.ForeignKey("correcao_criterio.id"), nullable=False, unique=True),
        sa.Column("enunciado", sa.Text, nullable=False),
        sa.Column("gabarito", sa.Text, nullable=True),
        sa.Column("nota", sa.Numeric(6, 2), nullable=False),
        sa.Column("valor", sa.Numeric(6, 2), nullable=False),
        sa.Column("percentual", sa.Numeric(5, 2), nullable=False),
        sa.Column("detalhe", sa.Text, nullable=False),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_erro_aluno_aluno_id", "erro_aluno", ["aluno_id"])
    with op.batch_alter_table("exercicio") as b:
        b.add_column(sa.Column("erro_id", UUID, nullable=True))
        b.create_foreign_key("fk_exercicio_erro", "erro_aluno", ["erro_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.drop_constraint("fk_exercicio_erro", type_="foreignkey")
        b.drop_column("erro_id")
    op.drop_index("ix_erro_aluno_aluno_id", "erro_aluno")
    op.drop_table("erro_aluno")
