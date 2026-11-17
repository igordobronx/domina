import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum, StatusCorrecaoEnum
from app.lecionados import materias_visiveis_do_aluno
from app.models.usuario import Atividade, Correcao, CorrecaoCriterio, Materia, Submissao, Usuario
from app.routers.dominio import _compartilha_turma
from app.schemas.evolucao import EvolucaoMateriaResponse, EvolucaoPontoResponse

router = APIRouter(tags=["evolucao"])


# evolucao = nota (%) de cada atividade corrigida ao longo do tempo, agrupada por materia.
# funciona para qualquer materia (redacao OU exatas) porque usa so o historico de correcoes
# aprovadas -- nao depende do dominio_aluno por tema, que para exatas e deliberadamente vazio
# (ver app/routers/submissoes.py).
@router.get("/evolucao/minha", response_model=list[EvolucaoMateriaResponse])
def minha_evolucao(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")
    return _evolucao_de(db, usuario.id)


# professor: so as materias que ele leciona nas turmas do aluno; gestor: todas
@router.get("/alunos/{aluno_id}/evolucao", response_model=list[EvolucaoMateriaResponse])
def evolucao_do_aluno(aluno_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    aluno = db.get(Usuario, aluno_id)
    if not aluno or aluno.perfil != PerfilEnum.ALUNO or aluno.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
    if usuario.perfil == PerfilEnum.PROFESSOR and not _compartilha_turma(db, usuario.id, aluno.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
    elif usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem a evolução de alunos.")
    return _evolucao_de(db, aluno.id, materias_visiveis_do_aluno(db, usuario, aluno.id))


def _evolucao_de(db: Session, aluno_id, materia_ids=None) -> list[EvolucaoMateriaResponse]:
    linhas = (
        db.query(Correcao, Submissao, Atividade, Materia)
        .join(Submissao, Submissao.id == Correcao.submissao_id)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .join(Materia, Materia.id == Atividade.materia_id)
        .filter(Submissao.aluno_id == aluno_id, Correcao.status == StatusCorrecaoEnum.APROVADA)
        .order_by(Submissao.criado_em)
    )
    if materia_ids is not None:
        linhas = linhas.filter(Materia.id.in_(list(materia_ids)))
    linhas = linhas.all()
    num_criterios_por_correcao = dict(
        db.query(CorrecaoCriterio.correcao_id, func.count(CorrecaoCriterio.id))
        .group_by(CorrecaoCriterio.correcao_id)
        .all()
    )

    por_materia: dict[uuid.UUID, dict] = {}
    for correcao, submissao, atividade, materia in linhas:
        num_criterios = num_criterios_por_correcao.get(correcao.id, 0)
        if not num_criterios or correcao.nota_professor is None:
            continue
        # redacao: sempre 5 x 200 = 1000 (valor_total nulo). Exatas: valor definido pelo
        # professor na atividade (ver app/routers/submissoes.py::criar_atividade).
        valor_total = float(atividade.valor_total) if atividade.valor_total is not None else num_criterios * 200
        percentual = float(correcao.nota_professor) / valor_total * 100
        bucket = por_materia.setdefault(materia.id, {"nome": materia.nome, "pontos": []})
        bucket["pontos"].append(
            EvolucaoPontoResponse(
                atividade_titulo=atividade.titulo,
                percentual=round(percentual, 1),
                data=submissao.criado_em,
            )
        )

    return [
        EvolucaoMateriaResponse(
            materia_id=materia_id,
            materia=info["nome"],
            media_percentual=round(sum(p.percentual for p in info["pontos"]) / len(info["pontos"]), 1),
            num_atividades=len(info["pontos"]),
            historico=info["pontos"],
        )
        for materia_id, info in por_materia.items()
    ]
