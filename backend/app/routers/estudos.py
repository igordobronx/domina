from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.estudos import ExercicioGerado, gerar_exercicios
from app.models.enum import PerfilEnum
from app.models.usuario import Usuario
from app.routers.dominio import _dominio_de

router = APIRouter(prefix="/estudos", tags=["estudos"])


# RF: plano de estudo personalizado -- exercicios gerados a partir do dominio REAL do aluno
# (so competencias com pelo menos 1 correcao aprovada; sem evidencia nao ha o que personalizar)
@router.get("/meu", response_model=list[ExercicioGerado])
def meus_exercicios(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")

    evidenciado = [d for d in _dominio_de(db, usuario.id) if d.num_evidencias > 0]
    if not evidenciado:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Ainda não há correções aprovadas para montar seu plano personalizado.",
        )
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Geração de exercícios indisponível: servidor sem chave do Gemini.",
        )

    piores = sorted(evidenciado, key=lambda d: d.percentual_dominio)[:3]
    return gerar_exercicios(usuario.id, piores)
