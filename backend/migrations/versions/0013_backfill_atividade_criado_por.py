"""preenche atividade.criado_por das atividades antigas, so quando da para saber com seguranca

Regra (sem chute): se a turma tem UM professor so, foi ele; senao, se UM professor so aprovou as
correcoes da atividade, foi ele. Nos demais casos continua nulo (so o gestor ve) ate alguem atribuir.

Revision ID: 0013
Revises: 0012
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    for atividade_id, turma_id in bind.execute(sa.text("SELECT id, turma_id FROM atividade WHERE criado_por IS NULL")).all():
        profs = [r[0] for r in bind.execute(sa.text(
            "SELECT usuario_id FROM usuario_turma WHERE turma_id = :t AND papel = 'PROFESSOR'"), {"t": turma_id})]
        if len(profs) != 1:
            profs = [r[0] for r in bind.execute(sa.text(
                "SELECT DISTINCT c.revisado_por FROM correcao c JOIN submissao s ON s.id = c.submissao_id "
                "WHERE s.atividade_id = :a AND c.revisado_por IS NOT NULL"), {"a": atividade_id})]
        if len(profs) == 1:
            bind.execute(sa.text("UPDATE atividade SET criado_por = :u WHERE id = :a"), {"u": profs[0], "a": atividade_id})


def downgrade() -> None:
    pass  # nao ha como separar o que foi preenchido aqui do que foi criado depois
