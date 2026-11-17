from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

import uuid

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.erros import registrar_erros
from app.estudos import gerar_exercicios, gerar_exercicios_exatas, salvar_exercicios, salvar_exercicios_exatas
from app.metas import avaliar_seguro
from app.models.enum import PerfilEnum
from app.models.usuario import ErroAluno, Exercicio, ExercicioResposta, Materia, Tema, Usuario
from app.routers.dominio import _compartilha_turma, _dominio_de

router = APIRouter(tags=["estudos"])

LIMITE_DIARIO = 9  # exercicios novos por aluno por dia (3 planos): protege o custo da API
MAX_NA_TELA = 6


class ExercicioAluno(BaseModel):
    """O que o aluno recebe: SEM gabarito e SEM explicacao enquanto nao respondeu.
    Depois de responder vem `respondida` (a alternativa dele), `correta`, `resposta_correta` e `explicacao`."""
    id: uuid.UUID
    habilidade_codigo: str  # C1..C5 na redacao; vazio em exatas
    materia: str | None = None  # so nos de exatas
    motivo: str | None = None  # so nos de exatas: o erro da correcao que originou o exercicio
    titulo: str
    enunciado: str
    opcoes: list[str]
    respondida: int | None = None
    correta: bool | None = None
    resposta_correta: int | None = None
    explicacao: str | None = None


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


def _lote(db: Session, aluno_id) -> list[tuple]:
    """Os ultimos exercicios que a IA gerou para o aluno, respondidos ou nao:
    (exercicio, codigo da competencia ou "", resposta dele ou None)."""
    linhas = (
        db.query(Exercicio, Tema.habilidade_codigo, ExercicioResposta)
        .outerjoin(Tema, Tema.id == Exercicio.tema_id)
        .outerjoin(ExercicioResposta, (ExercicioResposta.exercicio_id == Exercicio.id)
                   & (ExercicioResposta.aluno_id == aluno_id))
        .filter(Exercicio.aluno_id == aluno_id)
        .order_by(Exercicio.criado_em.desc()).limit(MAX_NA_TELA).all()
    )
    return [(e, cod or "", r) for e, cod, r in linhas]


def _erros_sem_exercicio(db: Session, aluno_id, limite: int) -> list[ErroAluno]:
    feitos = db.query(Exercicio.erro_id).filter(Exercicio.erro_id.isnot(None))
    return (db.query(ErroAluno).filter(ErroAluno.aluno_id == aluno_id, ~ErroAluno.id.in_(feitos))
            .order_by(ErroAluno.percentual, ErroAluno.criado_em.desc()).limit(limite).all())


def _base(db: Session, usuario: Usuario):
    """(competencias com evidencia, erros de exatas ainda sem exercicio, lote atual); 409 se nao ha nada."""
    _so_aluno(usuario)
    registrar_erros(db, usuario.id)
    db.commit()
    evidenciado = [d for d in _dominio_de(db, usuario.id) if d.num_evidencias > 0]
    erros = _erros_sem_exercicio(db, usuario.id, 3)
    lote = _lote(db, usuario.id)
    if not evidenciado and not erros and not lote:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Ainda não há correções aprovadas para montar seu plano personalizado.",
        )
    return evidenciado, erros, lote


def _apresentar(db: Session, lote, evidenciado) -> list[ExercicioAluno]:
    pct = {d.habilidade_codigo: d.percentual_dominio for d in evidenciado}
    erro_por_id = {e.id: e for e in db.query(ErroAluno).filter(
        ErroAluno.id.in_([x.erro_id for x, _, _ in lote if x.erro_id]))}
    nomes_mat = {m.id: m.nome for m in db.query(Materia).filter(
        Materia.id.in_([x.materia_id for x, _, _ in lote if x.materia_id]))}

    def ordem(p):  # por fazer antes dos feitos; dentro disso, mais fraco primeiro
        e, cod, r = p  # peso: % de dominio (redacao) ou % da questao que ele acertou (exatas)
        return (r is not None,
                float(erro_por_id[e.erro_id].percentual) if e.erro_id in erro_por_id else pct.get(cod, 100))

    return [
        ExercicioAluno(
            id=e.id, habilidade_codigo=cod, titulo=e.titulo, enunciado=e.enunciado, opcoes=e.alternativas,
            materia=nomes_mat.get(e.materia_id) if e.erro_id else None,
            motivo=(f"Você errou: {erro_por_id[e.erro_id].enunciado[:160]}" if e.erro_id in erro_por_id else None),
            # gabarito e explicacao so saem do servidor depois que o aluno respondeu
            **({"respondida": ord(r.resposta[0]) - 65, "correta": bool(r.correta),
                "resposta_correta": e.resposta_correta, "explicacao": e.explicacao or ""} if r else {}),
        )
        for e, cod, r in sorted(lote, key=ordem)
    ]


# plano de estudo personalizado: exercicios gerados a partir do que o aluno erra (dominio C1-C5 na redacao;
# questoes erradas nas correcoes de exatas) e SALVOS no banco.
# Abrir a tela (GET) NUNCA chama a IA: devolve sempre os mesmos exercicios salvos, feitos ou nao.
@router.get("/estudos/meu", response_model=list[ExercicioAluno], response_model_exclude_none=True)
def meus_exercicios(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    evidenciado, _, lote = _base(db, usuario)
    return _apresentar(db, lote, evidenciado)


# so aqui a IA e chamada, e so quando o aluno pede (botao). Se ainda sobra exercicio por fazer,
# nao gera nada: devolve os mesmos. Vale o limite diario.
@router.post("/estudos/meu/gerar", response_model=list[ExercicioAluno], response_model_exclude_none=True)
def gerar_meus_exercicios(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    evidenciado, erros, lote = _base(db, usuario)
    if all(r is not None for _, _, r in lote):
        if not settings.ANTHROPIC_API_KEY:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Geração de exercícios indisponível: servidor sem chave do Claude.",
            )
        hoje = db.query(func.count(Exercicio.id)).filter(
            Exercicio.aluno_id == usuario.id, Exercicio.criado_em >= datetime.combine(date.today(), time.min)).scalar()
        if hoje >= LIMITE_DIARIO:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
                                "Você já recebeu o máximo de exercícios novos por hoje. Volte amanhã!")
        if evidenciado:
            piores = sorted(evidenciado, key=lambda d: d.percentual_dominio)[:3]
            novos = gerar_exercicios(usuario.id, piores, forcar=True)  # forcar: o que vale e o salvo no banco
            salvar_exercicios(db, usuario.id, novos, {d.habilidade_codigo: d.tema_id for d in piores})
        if erros:
            nomes = {m.id: m.nome for m in db.query(Materia).filter(Materia.id.in_({e.materia_id for e in erros}))}
            salvar_exercicios_exatas(db, usuario.id, gerar_exercicios_exatas(erros, nomes), erros)
        db.commit()
        lote = _lote(db, usuario.id)
    return _apresentar(db, lote, evidenciado)


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
