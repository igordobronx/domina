"""O sino do topo: lista os avisos da pessoa e marca como lidos (app/avisos.py cria os avisos)."""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.avisos import gerar_alertas
from app.database import get_db
from app.models.usuario import Aviso, Usuario

router = APIRouter(tags=["avisos"])


class AvisoResponse(BaseModel):
    id: uuid.UUID
    tipo: str
    texto: str
    destino: str | None
    submissao_id: uuid.UUID | None
    lido: bool
    criado_em: datetime


class AvisosResponse(BaseModel):
    nao_lidos: int
    itens: list[AvisoResponse]


@router.get("/avisos", response_model=AvisosResponse)
def meus_avisos(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    gerar_alertas(db, usuario)  # prazo, feriado, sequencia... (a cada poucos minutos, sem tarefa agendada)
    q = db.query(Aviso).filter(Aviso.usuario_id == usuario.id, Aviso.tipo != "MARCADOR")
    itens = q.order_by(Aviso.criado_em.desc()).limit(40).all()
    return AvisosResponse(nao_lidos=q.filter(Aviso.lido.is_(False)).count(),
                          itens=[AvisoResponse(id=i.id, tipo=i.tipo, texto=i.texto, destino=i.destino,
                                               submissao_id=i.submissao_id, lido=i.lido, criado_em=i.criado_em)
                                 for i in itens])


@router.post("/avisos/lidos", status_code=status.HTTP_204_NO_CONTENT)
def marcar_lidos(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Aviso).filter_by(usuario_id=usuario.id, lido=False).update({"lido": True})
    db.commit()
