import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.security import hash_password
from app.auth.dependencies import escola_do_escopo, get_current_user
from app.database import get_db
from app.models.usuario import Escola, Turma, Usuario, UsuarioTurma
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.routers.submissoes import _professor_da_turma
from app.schemas.usuario import CriarUsuarioRequest, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _resposta(db: Session, usuario: Usuario) -> UsuarioResponse:
    escola = db.get(Escola, usuario.escola_id)
    return UsuarioResponse(
        id=usuario.id, nome=usuario.nome, email=usuario.email,
        perfil=usuario.perfil.value, escola_nome=escola.nome if escola else "Plataforma Domina",
    )


@router.get("/me", response_model=UsuarioResponse)
def meu_usuario(usuario_atual: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _resposta(db, usuario_atual)


# quem pode criar o que (RBAC): o admin cria em qualquer escola, os outros so na propria
PODE_CRIAR = {
    PerfilEnum.ADMIN: {PerfilEnum.GESTOR, PerfilEnum.PROFESSOR, PerfilEnum.ALUNO},
    PerfilEnum.GESTOR: {PerfilEnum.PROFESSOR, PerfilEnum.ALUNO},
    PerfilEnum.PROFESSOR: {PerfilEnum.ALUNO},
}


# lista a escola, para escolher quem matricular numa turma. Gestor ve todos; professor, so alunos;
# admin precisa dizer a escola (?escola_id=)
@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios(escola_id: uuid.UUID | None = None, usuario_atual: Usuario = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if usuario_atual.perfil == PerfilEnum.PROFESSOR:
        usuarios = db.query(Usuario).filter_by(escola_id=usuario_atual.escola_id, perfil=PerfilEnum.ALUNO)
    elif usuario_atual.perfil in (PerfilEnum.GESTOR, PerfilEnum.ADMIN):
        usuarios = db.query(Usuario).filter_by(escola_id=escola_do_escopo(db, usuario_atual, escola_id))
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Seu perfil não lista usuários.")
    return [_resposta(db, u) for u in usuarios]


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(payload: CriarUsuarioRequest, usuario_atual: Usuario = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    perfil = PerfilEnum(payload.perfil)
    if perfil not in PODE_CRIAR.get(usuario_atual.perfil, set()):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Seu perfil não pode criar este tipo de conta.")

    if usuario_atual.perfil == PerfilEnum.ADMIN:
        escola = db.get(Escola, payload.escola_id) if payload.escola_id else None
        if not escola:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Informe uma instituição válida (escola_id).")
        if not escola.ativa:
            raise HTTPException(status.HTTP_409_CONFLICT, "A instituição está desativada.")
        escola_id = escola.id
    else:
        # gestor/professor: sempre a propria escola, mesmo que mandem outro escola_id
        escola_id = usuario_atual.escola_id

    if db.query(Usuario).filter_by(email=payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado."
        )

    turma = None
    if payload.turma_id:
        turma = db.get(Turma, payload.turma_id)
        # a turma tem que ser da escola da nova conta (nem revela turmas de outras escolas)
        if not turma or turma.escola_id != escola_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
        if perfil == PerfilEnum.GESTOR:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Gestor não entra em turma.")
        if usuario_atual.perfil == PerfilEnum.PROFESSOR and not _professor_da_turma(db, usuario_atual, turma.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "O professor só matricula alunos nas próprias turmas.")

    novo_usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_password(payload.senha),
        perfil=perfil,
        escola_id=escola_id,
    )
    db.add(novo_usuario)
    db.flush()
    if turma:  # mesma transacao: ou cria a conta ja na turma, ou nao cria nada
        db.add(UsuarioTurma(usuario_id=novo_usuario.id, turma_id=turma.id, papel=UsuarioTurmaPapelEnum(perfil.value)))
    registrar(db, usuario_atual.id, "CRIAR", "Usuario", novo_usuario.id)
    db.commit()
    db.refresh(novo_usuario)

    return _resposta(db, novo_usuario)
