"""professor_materia: qual materia o professor da em qual turma

Preenche a partir do historico: materia/turma das atividades que o professor criou ou corrigiu.
O gestor ajusta depois na tela de turmas.

Revision ID: 0022
Revises: 0021
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "professor_materia",
        sa.Column("usuario_id", UUID, sa.ForeignKey("usuario.id"), primary_key=True),
        sa.Column("turma_id", UUID, sa.ForeignKey("turma.id"), primary_key=True),
        sa.Column("materia_id", UUID, sa.ForeignKey("materia.id"), primary_key=True),
    )
    op.execute("""
        INSERT INTO professor_materia (usuario_id, turma_id, materia_id)
        SELECT DISTINCT x.u, x.t, x.m FROM (
            SELECT a.criado_por AS u, a.turma_id AS t, a.materia_id AS m
              FROM atividade a WHERE a.criado_por IS NOT NULL
            UNION
            SELECT c.revisado_por, a.turma_id, a.materia_id
              FROM correcao c JOIN submissao s ON s.id = c.submissao_id JOIN atividade a ON a.id = s.atividade_id
             WHERE c.revisado_por IS NOT NULL
        ) x JOIN usuario us ON us.id = x.u
        WHERE us.perfil = 'PROFESSOR'
    """)


def downgrade() -> None:
    op.drop_table("professor_materia")
