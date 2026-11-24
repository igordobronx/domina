"""Assuntos dentro de uma materia (ver docs/decisoes/assuntos.md).

Professor: ve e usa os PROPRIOS assuntos mais os da escola (criados pelo gestor) das materias que leciona.
Gestor: ve todos os da materia e cria assuntos da escola. Nunca apaga: so tira de uso."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.lecionados import materias_do_professor
from app.models.enum import PerfilEnum
from app.models.usuario import Assunto, IaTrecho, Materia, Usuario

router = APIRouter(tags=["assuntos"])


class AssuntoRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)


class AssuntoEditar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    ativo: bool | None = None


class AssuntoResponse(BaseModel):
    id: uuid.UUID
    materia_id: uuid.UUID
    nome: str
    da_escola: bool  # true = criado pelo gestor, vale para todos os professores
    ativo: bool
    materiais: int = 0  # trechos de material que a IA guardou neste assunto
    instrucoes: int = 0
    correcoes: int = 0  # correcoes aprovadas + exercicios corrigidos usados como exemplo


def _materia(db: Session, usuario: Usuario, materia_id) -> Materia:
    materia = db.get(Materia, materia_id)
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores usam assuntos.")
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    if usuario.perfil == PerfilEnum.PROFESSOR and materia.id not in materias_do_professor(db, usuario.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Você não leciona {materia.nome}.")
    return materia


def _visiveis(db: Session, usuario: Usuario, materia_id):
    q = db.query(Assunto).filter(Assunto.materia_id == materia_id)
    if usuario.perfil == PerfilEnum.PROFESSOR:
        q = q.filter(or_(Assunto.professor_id == usuario.id, Assunto.professor_id.is_(None)))
    return q


def assunto_do_usuario(db: Session, usuario: Usuario, assunto_id, materia_id) -> Assunto:
    """O assunto que o usuario quer usar (em material, atividade, exercicio...). 404 se nao for dele
    ou de outra materia; 422 se estiver tirado de uso."""
    a = _visiveis(db, usuario, materia_id).filter(Assunto.id == assunto_id).first()
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assunto não encontrado nesta matéria.")
    if not a.ativo:
        raise HTTPException(422, "Este assunto está tirado de uso.")
    return a


def _resposta(a: Assunto, contagem: dict) -> AssuntoResponse:
    c = contagem.get(a.id, {})
    return AssuntoResponse(
        id=a.id, materia_id=a.materia_id, nome=a.nome, da_escola=a.professor_id is None, ativo=a.ativo,
        materiais=c.get("MATERIAL", 0), instrucoes=c.get("INSTRUCAO", 0),
        correcoes=c.get("CORRECAO", 0) + c.get("EXERCICIO", 0),
    )


def _contagem(db: Session, usuario: Usuario, assuntos: list[Assunto]) -> dict:
    ids = [a.id for a in assuntos]
    if not ids:
        return {}
    q = (db.query(IaTrecho.assunto_id, IaTrecho.origem, func.count())
         .filter(IaTrecho.assunto_id.in_(ids), IaTrecho.ignorado.is_(False)))
    if usuario.perfil == PerfilEnum.PROFESSOR:
        gestores = db.query(Usuario.id).filter(Usuario.perfil == PerfilEnum.GESTOR)
        q = q.filter(or_(IaTrecho.professor_id == usuario.id, IaTrecho.professor_id.in_(gestores)))
    contagem: dict = {}
    for aid, origem, n in q.group_by(IaTrecho.assunto_id, IaTrecho.origem):
        contagem.setdefault(aid, {})[origem] = n
    return contagem


@router.get("/materias/{materia_id}/assuntos", response_model=list[AssuntoResponse])
def listar_assuntos(materia_id: uuid.UUID, incluir_inativos: bool = False,
                    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia(db, usuario, materia_id)
    q = _visiveis(db, usuario, materia_id)
    if not incluir_inativos:
        q = q.filter(Assunto.ativo.is_(True))
    assuntos = q.order_by(func.lower(Assunto.nome)).all()
    contagem = _contagem(db, usuario, assuntos)
    return [_resposta(a, contagem) for a in assuntos]


@router.post("/materias/{materia_id}/assuntos", response_model=AssuntoResponse, status_code=status.HTTP_201_CREATED)
def criar_assunto(materia_id: uuid.UUID, payload: AssuntoRequest,
                  usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    materia = _materia(db, usuario, materia_id)
    nome = payload.nome.strip()
    if not nome:
        raise HTTPException(422, "Dê um nome para o assunto.")
    if _visiveis(db, usuario, materia.id).filter(func.lower(Assunto.nome) == nome.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um assunto com esse nome nesta matéria.")
    a = Assunto(materia_id=materia.id, nome=nome,
                professor_id=usuario.id if usuario.perfil == PerfilEnum.PROFESSOR else None)
    db.add(a)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "Assunto", a.id)
    db.commit()
    return _resposta(a, {})


@router.patch("/assuntos/{assunto_id}", response_model=AssuntoResponse)
def editar_assunto(assunto_id: uuid.UUID, payload: AssuntoEditar,
                   usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.get(Assunto, assunto_id)
    materia = db.get(Materia, a.materia_id) if a else None
    if not a or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assunto não encontrado.")
    _materia(db, usuario, a.materia_id)
    if not _visiveis(db, usuario, a.materia_id).filter(Assunto.id == a.id).first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assunto não encontrado.")
    if usuario.perfil == PerfilEnum.PROFESSOR and a.professor_id is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o gestor muda um assunto da escola.")
    if payload.nome is not None:
        nome = payload.nome.strip()
        if not nome:
            raise HTTPException(422, "Dê um nome para o assunto.")
        outro = _visiveis(db, usuario, a.materia_id).filter(
            func.lower(Assunto.nome) == nome.lower(), Assunto.id != a.id).first()
        if outro:
            raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um assunto com esse nome nesta matéria.")
        a.nome = nome
    if payload.ativo is not None:
        a.ativo = payload.ativo
    registrar(db, usuario.id, "EDITAR", "Assunto", a.id)
    db.commit()
    return _resposta(a, _contagem(db, usuario, [a]))
