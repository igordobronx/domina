import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.correcao import NOTAS_VALIDAS
from app.models.enum import TipoEnvioEnum


class SubmissaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    atividade_id: uuid.UUID
    aluno_id: uuid.UUID
    tipo_envio: TipoEnvioEnum
    texto_ocr: str | None
    texto_confirmado: str | None
    criado_em: datetime


class ConfirmarTextoRequest(BaseModel):
    # texto revisado pelo aluno; limite folgado (redacao ENEM tem ate 30 linhas)
    texto: str = Field(min_length=1, max_length=20_000)


class CorrigirRequest(BaseModel):
    # tema da proposta (a C2 depende dele); sem tema, usa o titulo da atividade
    tema: str | None = Field(default=None, max_length=500)


class CriterioResponse(BaseModel):
    codigo: str
    nome: str
    nota: float
    nota_professor: float | None
    justificativa: str


class CorrecaoResponse(BaseModel):
    id: uuid.UUID
    submissao_id: uuid.UUID
    nota_ia: float
    nota_professor: float | None
    revisado_por: uuid.UUID | None
    confianca: float
    status: str
    modelo_usado: str
    feedback: str | None
    criterios: list[CriterioResponse]


class NotaCriterioInput(BaseModel):
    codigo: Literal["C1", "C2", "C3", "C4", "C5"]
    nota: float

    @field_validator("nota")
    @classmethod
    def nivel_do_enem(cls, v):
        if v not in NOTAS_VALIDAS:
            raise ValueError(f"nota deve ser uma das {sorted(NOTAS_VALIDAS)}")
        return v


class AprovarRequest(BaseModel):
    # nota final por competencia, decidida pelo professor (pode so confirmar a da IA ou mudar)
    notas: list[NotaCriterioInput] = Field(min_length=5, max_length=5)
    feedback: str | None = Field(default=None, max_length=2000)

    @field_validator("notas")
    @classmethod
    def uma_de_cada(cls, v):
        if sorted(c.codigo for c in v) != ["C1", "C2", "C3", "C4", "C5"]:
            raise ValueError("informe as 5 competencias (C1..C5), uma vez cada")
        return v


class AlunoResumo(BaseModel):
    id: uuid.UUID
    nome: str


class AtividadeResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    turma: str
    alunos: list[AlunoResumo]
