import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum, StatusCorrecaoEnum
from app.models.usuario import Atividade, Correcao, CorrecaoCriterio, Materia, Submissao, Usuario
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

    linhas = (
        db.query(Correcao, Submissao, Atividade, Materia)
        .join(Submissao, Submissao.id == Correcao.submissao_id)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .join(Materia, Materia.id == Atividade.materia_id)
        .filter(Submissao.aluno_id == usuario.id, Correcao.status == StatusCorrecaoEnum.APROVADA)
        .order_by(Submissao.criado_em)
        .all()
    )
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
        percentual = float(correcao.nota_professor) / (num_criterios * 200) * 100
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
