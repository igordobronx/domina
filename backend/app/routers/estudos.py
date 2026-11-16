from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

import uuid

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.estudos import gerar_exercicios, salvar_exercicios
from app.metas import avaliar_seguro
from app.models.enum import PerfilEnum
from app.models.usuario import Exercicio, ExercicioResposta, Tema, Usuario
from app.routers.dominio import _compartilha_turma, _dominio_de

router = APIRouter(tags=["estudos"])

LIMITE_DIARIO = 9  # exercicios novos por aluno por dia (3 planos): protege o custo da API
MAX_NA_TELA = 6


class ExercicioAluno(BaseModel):
    """O que o aluno recebe: SEM gabarito e SEM explicacao (so vem depois de responder)."""
    id: uuid.UUID
    habilidade_codigo: str
    titulo: str
    enunciado: str
    opcoes: list[str]


class RespostaRequest(BaseModel):
    opcao: int = Field(ge=0, le=3)


class ResultadoResposta(BaseModel):
    correta: bool
    resposta_correta: int
    explicacao: str


class PraticaItem(BaseModel):
    habilidade_codigo: str
    respondidos: int
    acertos: int


def _so_aluno(usuario: Usuario) -> None:
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")


def _pendentes(db: Session, aluno_id) -> list[tuple[Exercicio, str]]:
    respondidos = db.query(ExercicioResposta.exercicio_id).filter_by(aluno_id=aluno_id)
    return (
        db.query(Exercicio, Tema.habilidade_codigo).join(Tema, Tema.id == Exercicio.tema_id)
        .filter(Exercicio.aluno_id == aluno_id, ~Exercicio.id.in_(respondidos))
        .order_by(Exercicio.criado_em.desc(), Tema.habilidade_codigo).limit(MAX_NA_TELA).all()
    )


# plano de estudo personalizado: exercicios gerados a partir do dominio REAL do aluno e SALVOS.
# Devolve os ainda nao respondidos; so gera novos quando nao sobra nenhum (e ate o limite diario).
@router.get("/estudos/meu", response_model=list[ExercicioAluno])
def meus_exercicios(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_aluno(usuario)
    evidenciado = [d for d in _dominio_de(db, usuario.id) if d.num_evidencias > 0]
    if not evidenciado:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Ainda não há correções aprovadas para montar seu plano personalizado.",
        )
    pendentes = _pendentes(db, usuario.id)
    if not pendentes:
        if not settings.ANTHROPIC_API_KEY:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Geração de exercícios indisponível: servidor sem chave do Claude.",
            )
        hoje = db.query(func.count(Exercicio.id)).filter(
            Exercicio.aluno_id == usuario.id, Exercicio.criado_em >= datetime.combine(date.today(), time.min)).scalar()
        if hoje >= LIMITE_DIARIO:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
                                "Você já recebeu o máximo de exercícios novos por hoje. Volte amanhã!")
        piores = sorted(evidenciado, key=lambda d: d.percentual_dominio)[:3]
        novos = gerar_exercicios(usuario.id, piores, forcar=True)  # forcar: o que vale e o salvo no banco
        salvar_exercicios(db, usuario.id, novos, {d.habilidade_codigo: d.tema_id for d in piores})
        db.commit()
        pendentes = _pendentes(db, usuario.id)
    pct = {d.habilidade_codigo: d.percentual_dominio for d in evidenciado}
    pendentes = sorted(pendentes, key=lambda p: pct.get(p[1], 100))  # competencia mais fraca primeiro
    return [ExercicioAluno(id=e.id, habilidade_codigo=cod, titulo=e.titulo, enunciado=e.enunciado, opcoes=e.alternativas)
            for e, cod in pendentes]


# o servidor confere (o navegador nunca recebe o gabarito antes de responder)
@router.post("/estudos/exercicios/{exercicio_id}/responder", response_model=ResultadoResposta)
def responder(exercicio_id: uuid.UUID, payload: RespostaRequest, usuario: Usuario = Depends(get_current_user),
              db: Session = Depends(get_db)):
    _so_aluno(usuario)
    ex = db.get(Exercicio, exercicio_id)
    if not ex or ex.aluno_id != usuario.id:  # de outro aluno = nao existe
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercício não encontrado.")
    if payload.opcao >= len(ex.alternativas or []):
        raise HTTPException(422, "Alternativa inválida.")
    if db.query(ExercicioResposta.id).filter_by(exercicio_id=ex.id, aluno_id=usuario.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Você já respondeu este exercício.")
    correta = payload.opcao == ex.resposta_correta
    db.add(ExercicioResposta(exercicio_id=ex.id, aluno_id=usuario.id, resposta=chr(65 + payload.opcao), correta=correta))
    db.commit()
    avaliar_seguro(usuario.id)  # metas de pratica
    return ResultadoResposta(correta=correta, resposta_correta=ex.resposta_correta, explicacao=ex.explicacao or "")


def _pratica_de(db: Session, aluno_id) -> list[PraticaItem]:
    por = {}
    q = (db.query(Tema.habilidade_codigo, ExercicioResposta.correta)
         .join(Exercicio, Exercicio.tema_id == Tema.id).join(ExercicioResposta, ExercicioResposta.exercicio_id == Exercicio.id)
         .filter(ExercicioResposta.aluno_id == aluno_id))
    for cod, correta in q:
        r = por.setdefault(cod, [0, 0])
        r[0] += 1
        r[1] += 1 if correta else 0
    return [PraticaItem(habilidade_codigo=c, respondidos=v[0], acertos=v[1]) for c, v in sorted(por.items())]


# prática por competência; SEPARADA do dominio (que so vem de correcoes aprovadas)
@router.get("/estudos/minha-pratica", response_model=list[PraticaItem])
def minha_pratica(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_aluno(usuario)
    return _pratica_de(db, usuario.id)


@router.get("/alunos/{aluno_id}/pratica", response_model=list[PraticaItem])
def pratica_do_aluno(aluno_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    aluno = db.get(Usuario, aluno_id)
    if not aluno or aluno.perfil != PerfilEnum.ALUNO or aluno.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
    if usuario.perfil == PerfilEnum.PROFESSOR and not _compartilha_turma(db, usuario.id, aluno.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
    elif usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem a prática de alunos.")
    return _pratica_de(db, aluno.id)
