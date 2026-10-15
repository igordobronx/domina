import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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


class EnviarTextoRequest(BaseModel):
    atividade_id: uuid.UUID
    texto: str = Field(min_length=1, max_length=20_000)
    aluno_id: uuid.UUID | None = None


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
    justificativa: str


class CorrecaoResponse(BaseModel):
    id: uuid.UUID
    submissao_id: uuid.UUID
    nota_ia: float
    confianca: float
    status: str
    modelo_usado: str
    feedback: str | None
    criterios: list[CriterioResponse]


class AlunoResumo(BaseModel):
    id: uuid.UUID
    nome: str


class AtividadeResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    turma: str
    alunos: list[AlunoResumo]
