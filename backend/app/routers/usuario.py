from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.security import hash_password
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.usuario import Usuario
from app.models.enum import PerfilEnum
from app.schemas.usuario import CriarUsuarioRequest, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioResponse)
def meu_usuario(usuario_atual: Usuario = Depends(get_current_user)):
    return usuario_atual


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(payload: CriarUsuarioRequest, usuario_atual: Usuario = Depends(get_current_user),
                   db: Session = Depends(get_db)):

    if usuario_atual.perfil != PerfilEnum.GESTOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "somente gestores podem criar usuarios")

    if db.query(Usuario).filter_by(email=payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado."
        )

    novo_usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_password(payload.senha),
        perfil=PerfilEnum(payload.perfil),
        escola_id=usuario_atual.escola_id,
    )
    db.add(novo_usuario)
    db.flush()
    registrar(db, usuario_atual.id, "CRIAR", "Usuario", novo_usuario.id)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario