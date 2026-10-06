import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database import get_db
from app.models.usuario import Usuario

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
    return usuario
