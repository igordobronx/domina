import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token, verify_password
from app.database import get_db
from app.models.enum import PerfilEnum
from app.models.usuario import Escola, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="não foi possivel validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id)  # o JWT guarda o id como string; a coluna espera um uuid.UUID
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise credentials_exception
    escola_inativa(db, usuario)
    return usuario


def escola_inativa(db: Session, usuario: Usuario) -> None:
    # escola desativada pelo administrador: ninguem dela entra mais (o admin nao tem escola)
    escola = db.get(Escola, usuario.escola_id) if usuario.escola_id else None
    if escola is not None and not escola.ativa:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Instituição desativada. Fale com a equipe do Domina.")


def exigir_perfil(*perfis: PerfilEnum):
    """Dependencia: so deixa passar quem tem um dos perfis."""
    def dependencia(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.perfil not in perfis:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Seu perfil não tem acesso a isto.")
        return usuario
    return dependencia


def escola_do_escopo(db: Session, usuario: Usuario, escola_id: uuid.UUID | None) -> uuid.UUID:
    """Escola sobre a qual a consulta vale. E AQUI que o RBAC acontece, no backend.

    - GESTOR: sempre a propria escola. Pedir outra devolve 404 (nao revela que existe).
    - ADMIN: precisa dizer qual escola; ve qualquer uma.
    """
    if usuario.perfil == PerfilEnum.ADMIN:
        if escola_id is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Informe a escola (escola_id).")
        if db.get(Escola, escola_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Instituição não encontrada.")
        return escola_id
    if usuario.perfil == PerfilEnum.GESTOR and usuario.escola_id:
        if escola_id is not None and escola_id != usuario.escola_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Instituição não encontrada.")
        return usuario.escola_id
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Seu perfil não tem acesso a isto.")


def confirmar_senha(usuario: Usuario, senha: str | None) -> None:
    """Reautenticacao em acao sensivel: o JWT roubado/esquecido aberto nao basta, pede a senha de novo.

    A senha vem no cabecalho X-Confirmar-Senha (nunca na URL, que iria para o access log do proxy).
    A recusa e um 403, que o middleware ja grava como ACESSO_NEGADO com a rota.
    """
    if not senha or not verify_password(senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Confirme sua senha para realizar esta ação.")
