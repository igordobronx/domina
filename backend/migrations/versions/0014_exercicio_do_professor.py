"""exercicio do professor: titulo, tema, turma, tipo, alternativas, resposta de exemplo

A tabela `exercicio` existia desde o baseline mas nunca foi usada; agora guarda os exercicios de
pratica criados pelo professor (a mao ou com ajuda da IA). tema_id passa a ser opcional.

Revision ID: 0014
Revises: 0013
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    with op.batch_alter_table("exercicio") as b:
        b.alter_column("tema_id", existing_type=UUID, nullable=True)
        b.add_column(sa.Column("titulo", sa.String(200), nullable=True))
        b.add_column(sa.Column("assunto", sa.String(200), nullable=True))
        b.add_column(sa.Column("materia_id", UUID, nullable=True))
        b.add_column(sa.Column("turma_id", UUID, nullable=True))
        b.add_column(sa.Column("criado_por", UUID, nullable=True))
        b.add_column(sa.Column("tipo", sa.String(12), nullable=False, server_default="OBJETIVO"))
        b.add_column(sa.Column("alternativas", sa.JSON(), nullable=True))
        b.add_column(sa.Column("resposta_correta", sa.Integer(), nullable=True))
        b.add_column(sa.Column("resposta_exemplo", sa.Text(), nullable=True))
        b.add_column(sa.Column("explicacao", sa.Text(), nullable=True))
        b.add_column(sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()))
        b.add_column(sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now(), nullable=True))
        b.create_foreign_key("fk_exercicio_materia", "materia", ["materia_id"], ["id"])
        b.create_foreign_key("fk_exercicio_turma", "turma", ["turma_id"], ["id"])
        b.create_foreign_key("fk_exercicio_criado_por", "usuario", ["criado_por"], ["id"])
    with op.batch_alter_table("exercicio_resposta") as b:
        b.add_column(sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("exercicio_resposta") as b:
        b.drop_column("criado_em")
    with op.batch_alter_table("exercicio") as b:
        for fk in ("fk_exercicio_criado_por", "fk_exercicio_turma", "fk_exercicio_materia"):
            b.drop_constraint(fk, type_="foreignkey")
        for col in ("criado_em", "ativo", "explicacao", "resposta_exemplo", "resposta_correta", "alternativas",
                    "tipo", "criado_por", "turma_id", "materia_id", "assunto", "titulo"):
            b.drop_column(col)
        b.alter_column("tema_id", existing_type=UUID, nullable=False)
