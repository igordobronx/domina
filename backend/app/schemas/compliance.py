import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ConsentimentoRequest(BaseModel):
    responsavel_nome: str = Field(min_length=1, max_length=200)
    responsavel_email: EmailStr


class ConsentimentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    aluno_id: uuid.UUID
    responsavel_nome: str
    responsavel_email: str
    aceito_em: datetime


class CustoUsoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mes_referencia: str
    tokens_llm: int
    chamadas_ocr: int
    custo_estimado: float


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    usuario_id: uuid.UUID
    acao: str
    entidade: str
    entidade_id: uuid.UUID
    criado_em: datetime
