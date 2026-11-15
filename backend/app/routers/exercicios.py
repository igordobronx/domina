"""Exercicios de pratica criados pelo professor (a mao ou com ajuda da IA).

Separacao das abas do aluno: a regra e QUEM PUBLICOU.
- "Para voce (IA)": /estudos/meu, gerados na hora pelos pontos fracos do aluno (nada aqui).
- "Do professor": esta rota. Se o professor pediu ajuda da IA, continua sendo do professor
  (gerado_por_ia=True so liga um selo). A IA so sugere rascunhos; nada chega ao aluno sem o
  professor salvar (RN-13).
Exercicio nao vale nota: provas continuam em Atividade.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.exercicios_ia import SugestaoExercicio, sugerir_exercicios, sugerir_resposta_exemplo
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.models.usuario import Exercicio, ExercicioResposta, Materia, Turma, Usuario, UsuarioTurma
from app.routers.submissoes import _professor_da_turma
from app.schemas.exercicio import (
    ExercicioAlunoResponse, ExercicioProfessorResponse, ExercicioRequest, ResponderRequest,
    SugerirRequest, SugerirRespostaRequest, SugestaoRespostaResponse,
)

router = APIRouter(prefix="/exercicios", tags=["exercicios"])


def _so_professor(usuario: Usuario) -> None:
    if usuario.perfil != PerfilEnum.PROFESSOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores criam exercícios.")


def _materia_da_escola(db: Session, usuario: Usuario, materia_id) -> Materia:
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return materia


def _conferir(db: Session, usuario: Usuario, payload: ExercicioRequest) -> None:
    _materia_da_escola(db, usuario, payload.materia_id)
    turma = db.get(Turma, payload.turma_id)
    if not turma or turma.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if not _professor_da_turma(db, usuario, turma.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")


def _meu(db: Session, usuario: Usuario, exercicio_id: uuid.UUID) -> Exercicio:
    _so_professor(usuario)
    ex = db.get(Exercicio, exercicio_id)
    if not ex or not ex.ativo or ex.criado_por != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercício não encontrado.")
    return ex


def _aplicar(ex: Exercicio, p: ExercicioRequest) -> None:
    ex.titulo, ex.assunto = p.titulo.strip(), p.assunto.strip()
    ex.materia_id, ex.turma_id, ex.tipo = p.materia_id, p.turma_id, p.tipo
    ex.enunciado = p.enunciado.strip()
    ex.alternativas, ex.resposta_correta = p.alternativas, p.resposta_correta
    ex.resposta_exemplo = p.resposta_exemplo.strip() if p.resposta_exemplo else None
    ex.explicacao = (p.explicacao or "").strip() or None
    ex.gerado_por_ia = p.gerado_por_ia


def _resposta_professor(db: Session, ex: Exercicio) -> ExercicioProfessorResponse:
    total, acertos = db.query(
        func.count(ExercicioResposta.id), func.count(ExercicioResposta.id).filter(ExercicioResposta.correta.is_(True)),
    ).filter(ExercicioResposta.exercicio_id == ex.id).one()
    return ExercicioProfessorResponse(
        id=ex.id, titulo=ex.titulo or "", assunto=ex.assunto or "", materia_id=ex.materia_id,
        materia_nome=db.get(Materia, ex.materia_id).nome, turma_id=ex.turma_id,
        turma_nome=db.get(Turma, ex.turma_id).nome, tipo=ex.tipo, enunciado=ex.enunciado,
        alternativas=ex.alternativas, resposta_correta=ex.resposta_correta, resposta_exemplo=ex.resposta_exemplo,
        explicacao=ex.explicacao, gerado_por_ia=ex.gerado_por_ia, criado_em=ex.criado_em,
        respostas=total, acertos=acertos,
    )


def _resposta_aluno(db: Session, ex: Exercicio, minha: ExercicioResposta | None) -> ExercicioAlunoResponse:
    professor = db.get(Usuario, ex.criado_por)
    r = ExercicioAlunoResponse(
        id=ex.id, titulo=ex.titulo or "", assunto=ex.assunto or "", materia_nome=db.get(Materia, ex.materia_id).nome,
        professor_nome=professor.nome if professor else "", tipo=ex.tipo, enunciado=ex.enunciado,
        alternativas=ex.alternativas, gerado_por_ia=ex.gerado_por_ia, criado_em=ex.criado_em,
    )
    if minha:  # gabarito so depois de responder
        r.minha_resposta, r.correta = minha.resposta, minha.correta
        r.resposta_correta, r.resposta_exemplo, r.explicacao = ex.resposta_correta, ex.resposta_exemplo, ex.explicacao
    return r


def _precisa_da_ia() -> None:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "IA indisponível: servidor sem chave do Claude.")


# ---------- professor ----------

@router.get("", response_model=list[ExercicioProfessorResponse])
def listar_meus(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_professor(usuario)
    exercicios = (db.query(Exercicio).filter_by(criado_por=usuario.id, ativo=True)
                  .order_by(Exercicio.criado_em.desc()).all())
    return [_resposta_professor(db, ex) for ex in exercicios]


@router.post("", response_model=ExercicioProfessorResponse, status_code=status.HTTP_201_CREATED)
def criar(payload: ExercicioRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_professor(usuario)
    _conferir(db, usuario, payload)
    ex = Exercicio(criado_por=usuario.id, aprovado_por=usuario.id)  # publicar = aprovar (RN-13)
    _aplicar(ex, payload)
    db.add(ex)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "Exercicio", ex.id)
    db.commit()
    db.refresh(ex)
    return _resposta_professor(db, ex)


@router.put("/{exercicio_id}", response_model=ExercicioProfessorResponse)
def editar(exercicio_id: uuid.UUID, payload: ExercicioRequest,
           usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ex = _meu(db, usuario, exercicio_id)
    _conferir(db, usuario, payload)
    _aplicar(ex, payload)
    registrar(db, usuario.id, "EDITAR", "Exercicio", ex.id)
    db.commit()
    db.refresh(ex)
    return _resposta_professor(db, ex)


@router.delete("/{exercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(exercicio_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ex = _meu(db, usuario, exercicio_id)
    ex.ativo = False  # some para os alunos; as respostas ficam
    registrar(db, usuario.id, "EXCLUIR", "Exercicio", ex.id)
    db.commit()


@router.post("/sugerir", response_model=list[SugestaoExercicio])
def sugerir(payload: SugerirRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Rascunhos da IA sobre um tema. NAO salva: o professor revisa e salva cada um."""
    _so_professor(usuario)
    materia = _materia_da_escola(db, usuario, payload.materia_id)
    _precisa_da_ia()
    return sugerir_exercicios(materia.nome, payload.assunto.strip(), payload.tipo, payload.quantidade,
                              (payload.instrucoes or "").strip() or None)


@router.post("/sugerir-resposta", response_model=SugestaoRespostaResponse)
def sugerir_resposta(payload: SugerirRespostaRequest, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    """Resposta de exemplo para um discursivo (botao "IA sugere")."""
    _so_professor(usuario)
    materia = _materia_da_escola(db, usuario, payload.materia_id)
    _precisa_da_ia()
    return SugestaoRespostaResponse(resposta_exemplo=sugerir_resposta_exemplo(
        materia.nome, (payload.assunto or "").strip(), payload.enunciado.strip()))


# ---------- aluno ----------

def _turmas_do_aluno(db: Session, usuario: Usuario) -> list:
    return [ut.turma_id for ut in db.query(UsuarioTurma).filter_by(
        usuario_id=usuario.id, papel=UsuarioTurmaPapelEnum.ALUNO)]


@router.get("/turma", response_model=list[ExercicioAlunoResponse])
def da_minha_turma(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")
    turmas = _turmas_do_aluno(db, usuario)
    if not turmas:
        return []
    exercicios = (db.query(Exercicio).filter(Exercicio.turma_id.in_(turmas), Exercicio.ativo.is_(True))
                  .order_by(Exercicio.criado_em.desc()).all())
    minhas = {r.exercicio_id: r for r in db.query(ExercicioResposta).filter(
        ExercicioResposta.aluno_id == usuario.id,
        ExercicioResposta.exercicio_id.in_([e.id for e in exercicios]))} if exercicios else {}
    return [_resposta_aluno(db, ex, minhas.get(ex.id)) for ex in exercicios]


@router.post("/{exercicio_id}/responder", response_model=ExercicioAlunoResponse)
def responder(exercicio_id: uuid.UUID, payload: ResponderRequest,
              usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos respondem exercícios.")
    ex = db.get(Exercicio, exercicio_id)
    if not ex or not ex.ativo or ex.turma_id not in _turmas_do_aluno(db, usuario):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercício não encontrado.")
    correta = None
    if ex.tipo == "OBJETIVO":
        try:
            indice = int(payload.resposta)
        except ValueError:
            raise HTTPException(422, "Escolha uma das alternativas.")
        if not 0 <= indice < len(ex.alternativas or []):
            raise HTTPException(422, "Escolha uma das alternativas.")
        correta = indice == ex.resposta_correta
    # praticar de novo sobrescreve: guarda a ultima tentativa (o professor ve quem fez e quem acertou)
    minha = db.query(ExercicioResposta).filter_by(exercicio_id=ex.id, aluno_id=usuario.id).first()
    if minha is None:
        minha = ExercicioResposta(exercicio_id=ex.id, aluno_id=usuario.id, resposta="")
        db.add(minha)
    minha.resposta, minha.correta = payload.resposta.strip(), correta
    db.commit()
    return _resposta_aluno(db, ex, minha)
