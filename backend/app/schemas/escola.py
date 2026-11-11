import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CriarEscolaRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=250)
    cnpj: str = Field(min_length=14, max_length=18)
    plano_fixo: Decimal = Field(default=Decimal("1000"), ge=0)
    valor_por_aluno: Decimal = Field(default=Decimal("8"), ge=0)


class EditarEscolaRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=250)
    cnpj: str | None = Field(default=None, min_length=14, max_length=18)
    plano_fixo: Decimal | None = Field(default=None, ge=0)
    valor_por_aluno: Decimal | None = Field(default=None, ge=0)
    ativa: bool | None = None  # false = desativar a instituicao


class EscolaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    cnpj: str
    ativa: bool
    plano_fixo: float
    valor_por_aluno: float
    criado_em: datetime
