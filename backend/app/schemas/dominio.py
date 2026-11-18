import uuid

from pydantic import BaseModel


class DominioResponse(BaseModel):
    tema_id: uuid.UUID
    tema: str
    materia: str = ""
    habilidade_codigo: str
    percentual_dominio: float
    num_evidencias: int
