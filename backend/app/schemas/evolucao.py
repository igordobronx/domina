import uuid
from datetime import datetime

from pydantic import BaseModel


class EvolucaoPontoResponse(BaseModel):
    atividade_titulo: str
    percentual: float
    data: datetime


class SubtopicoResponse(BaseModel):
    nome: str
    percentual: float
    num_questoes: int


class EvolucaoMateriaResponse(BaseModel):
    materia_id: uuid.UUID
    materia: str
    media_percentual: float
    num_atividades: int
    historico: list[EvolucaoPontoResponse]
    subtopicos: list[SubtopicoResponse] = []  # exatas: media por subtopico das questoes (redacao usa o dominio C1-C5)
