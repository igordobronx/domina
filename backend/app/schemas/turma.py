import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CriarTurmaRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    ano: int


class TurmaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    ano: int


class MatricularRequest(BaseModel):
    usuario_id: uuid.UUID
    papel: Literal["ALUNO", "PROFESSOR"]


class MembroTurmaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: str
    papel: str
