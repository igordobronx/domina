"""XP, sequencia de dias e conquistas do proprio aluno (so ALUNO; ninguem ve o XP dos outros aqui)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import exigir_perfil
from app.database import get_db
from app.gamificacao import xp_do_aluno
from app.metas import avaliar_metas, nivel_de
from app.models.enum import PerfilEnum
from app.models.usuario import Usuario
from app.schemas.gamificacao import MinhaGamificacaoResponse

router = APIRouter(tags=["gamificacao"])
APENAS_ALUNO = exigir_perfil(PerfilEnum.ALUNO)
HISTORICO_MAX = 30


@router.get("/gamificacao/minha", response_model=MinhaGamificacaoResponse)
def minha_gamificacao(usuario: Usuario = Depends(APENAS_ALUNO), db: Session = Depends(get_db)):
    avaliar_metas(db, usuario.id)  # mesma rede de seguranca de /metas/minhas: metas cumpridas entram no XP
    db.commit()
    r = xp_do_aluno(db, usuario.id)
    return MinhaGamificacaoResponse(nivel=nivel_de(r["xp"]), sequencia=r["sequencia"],
                                    conquistas=r["conquistas"], historico=r["historico"][:HISTORICO_MAX])
