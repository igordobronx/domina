import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TipoEvento = Literal["PROVA", "ENTREGA", "REUNIAO", "AVISO"]


class EventoRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str | None = Field(default=None, max_length=2000)
    tipo: TipoEvento = "AVISO"
    inicio: date
    fim: date | None = None
    turma_id: uuid.UUID | None = None  # nulo = escola toda (so gestor/admin)

    @model_validator(mode="after")
    def fim_depois_do_inicio(self):
        if self.fim and self.fim < self.inicio:
            raise ValueError("O fim não pode ser antes do início.")
        return self


class ItemCalendario(BaseModel):
    id: str  # "evento:<uuid>", "prazo:<uuid>" ou "feriado:<data>"
    origem: Literal["evento", "prazo", "feriado"]
    titulo: str
    descricao: str | None = None
    tipo: str
    inicio: date
    fim: date | None = None
    turma_id: uuid.UUID | None = None
    turma: str | None = None
    editavel: bool = False  # so eventos, e so de quem pode mexer neles
