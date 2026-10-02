from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.database import get_db
from app.models.usuario import Usuario 
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first() #verifica o uti.lizador de email
    if not usuario or not verify_password(payload.senha, usuario.senha_hash): #valida a existencia da palavra passe caso der certo
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou palavra passe estão incorretos",
            headers={"www-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": str(usuario.id), "email": usuario.email}
    )
    return TokenResponse(access_token=access_token)