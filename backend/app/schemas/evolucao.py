import uuid
from datetime import datetime

from pydantic import BaseModel


class EvolucaoPontoResponse(BaseModel):
    atividade_titulo: str
    percentual: float
    data: datetime


class EvolucaoMateriaResponse(BaseModel):
    materia_id: uuid.UUID
    materia: str
    media_percentual: float
    num_atividades: int
    historico: list[EvolucaoPontoResponse]
