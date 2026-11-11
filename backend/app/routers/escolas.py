import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import confirmar_senha, exigir_perfil
from app.database import get_db
from app.models.enum import PerfilEnum
from app.models.usuario import Escola, Usuario
from app.schemas.escola import CriarEscolaRequest, EditarEscolaRequest, EscolaResponse

# so o administrador da plataforma gerencia instituicoes
router = APIRouter(prefix="/escolas", tags=["escolas"])
admin = Depends(exigir_perfil(PerfilEnum.ADMIN))


@router.get("", response_model=list[EscolaResponse])
def listar_escolas(usuario: Usuario = admin, db: Session = Depends(get_db)):
    return db.query(Escola).order_by(Escola.nome).all()


@router.post("", response_model=EscolaResponse, status_code=status.HTTP_201_CREATED)
def criar_escola(payload: CriarEscolaRequest, usuario: Usuario = admin, db: Session = Depends(get_db)):
    if db.query(Escola).filter_by(cnpj=payload.cnpj).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma instituição com este CNPJ.")
    escola = Escola(**payload.model_dump())
    db.add(escola)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "Escola", escola.id)
    db.commit()
    db.refresh(escola)
    return escola


@router.put("/{escola_id}", response_model=EscolaResponse)
def editar_escola(escola_id: uuid.UUID, payload: EditarEscolaRequest, usuario: Usuario = admin,
                  db: Session = Depends(get_db), x_confirmar_senha: str | None = Header(default=None)):
    if "ativa" in payload.model_fields_set:  # desativar/reativar uma instituicao inteira: pede a senha de novo
        confirmar_senha(usuario, x_confirmar_senha)
    escola = db.get(Escola, escola_id)
    if not escola:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Instituição não encontrada.")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        if valor is not None:
            setattr(escola, campo, valor)
    registrar(db, usuario.id, "DESATIVAR" if payload.ativa is False else "EDITAR", "Escola", escola.id)
    db.commit()
    db.refresh(escola)
    return escola
