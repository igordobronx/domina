"""Marcas do professor sobre a foto do envio.

O aluno ve as marcas do professor so depois que a correcao e APROVADA (as da IA ficam em
CorrecaoCriterio.pontos e ele ja ve quando pede a correcao). Gestor so le."""
import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum, StatusCorrecaoEnum
from app.models.usuario import Anotacao, Correcao, Usuario
from app.routers.correcoes import _so_professor
from app.routers.submissoes import _submissao_visivel

router = APIRouter(tags=["anotacoes"])
MAX_ANOTACOES = 100  # por envio


class AnotacaoRequest(BaseModel):
    pagina: int = Field(default=0, ge=0, le=5)
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    largura: float = Field(gt=0, le=1)
    altura: float = Field(gt=0, le=1)
    tipo: Literal["acerto", "erro", "nota"] = "nota"
    comentario: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def _dentro_da_folha(self):
        if self.x + self.largura > 1.001 or self.y + self.altura > 1.001:
            raise ValueError("A marca precisa ficar dentro da folha.")
        return self


class AnotacaoEditar(BaseModel):
    tipo: Literal["acerto", "erro", "nota"] | None = None
    comentario: str | None = Field(default=None, min_length=1, max_length=1000)


class AnotacaoResponse(BaseModel):
    id: uuid.UUID
    pagina: int
    x: float
    y: float
    largura: float
    altura: float
    tipo: str
    comentario: str
    autor_nome: str
    minha: bool  # o professor logado pode editar/apagar
    criado_em: datetime


def _resposta(a: Anotacao, autor: Usuario, usuario: Usuario) -> AnotacaoResponse:
    return AnotacaoResponse(id=a.id, pagina=a.pagina, x=a.x, y=a.y, largura=a.largura, altura=a.altura, tipo=a.tipo,
                            comentario=a.comentario, autor_nome=autor.nome, minha=a.criado_por == usuario.id,
                            criado_em=a.criado_em)


@router.get("/submissoes/{submissao_id}/anotacoes", response_model=list[AnotacaoResponse])
def listar_anotacoes(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    if usuario.perfil == PerfilEnum.ALUNO:
        correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
        if not correcao or correcao.status != StatusCorrecaoEnum.APROVADA:
            return []
    linhas = (db.query(Anotacao, Usuario).join(Usuario, Usuario.id == Anotacao.criado_por)
              .filter(Anotacao.submissao_id == submissao.id).order_by(Anotacao.criado_em))
    return [_resposta(a, u, usuario) for a, u in linhas]


@router.post("/submissoes/{submissao_id}/anotacoes", response_model=AnotacaoResponse,
             status_code=status.HTTP_201_CREATED)
def criar_anotacao(submissao_id: uuid.UUID, payload: AnotacaoRequest,
                   usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _so_professor(db, submissao, usuario)
    if db.query(Anotacao).filter_by(submissao_id=submissao.id).count() >= MAX_ANOTACOES:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Limite de {MAX_ANOTACOES} marcas neste envio.")
    a = Anotacao(submissao_id=submissao.id, criado_por=usuario.id, **{**payload.model_dump(), "comentario": payload.comentario.strip()})
    db.add(a)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "Anotacao", a.id)
    db.commit()
    return _resposta(a, usuario, usuario)


def _minha(db: Session, usuario: Usuario, anotacao_id) -> Anotacao:
    a = db.get(Anotacao, anotacao_id)
    if not a or a.criado_por != usuario.id:  # so o autor mexe; o resto nem sabe que existe
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Marca não encontrada.")
    return a


@router.patch("/anotacoes/{anotacao_id}", response_model=AnotacaoResponse)
def editar_anotacao(anotacao_id: uuid.UUID, payload: AnotacaoEditar,
                    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    a = _minha(db, usuario, anotacao_id)
    if payload.tipo:
        a.tipo = payload.tipo
    if payload.comentario:
        a.comentario = payload.comentario.strip()
    registrar(db, usuario.id, "EDITAR", "Anotacao", a.id)
    db.commit()
    return _resposta(a, usuario, usuario)


@router.delete("/anotacoes/{anotacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_anotacao(anotacao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    a = _minha(db, usuario, anotacao_id)
    registrar(db, usuario.id, "EXCLUIR", "Anotacao", a.id)
    db.delete(a)
    db.commit()
