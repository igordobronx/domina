import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enum import StatusProcessamentoEnum, TipoDocumentoEnum


class DocumentoBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    materia_id: uuid.UUID
    nome_arquivo: str
    tipo: TipoDocumentoEnum
    status_processamento: StatusProcessamentoEnum
    detalhe: str | None = None  # motivo quando a IA nao conseguiu ler o arquivo
    criado_em: datetime


class MemoriaIAResponse(BaseModel):
    trechos_de_material: int
    correcoes_aprendidas: int
    instrucoes: int = 0


class InstrucaoRequest(BaseModel):
    texto: str = Field(min_length=5, max_length=2000)


class InstrucaoResponse(BaseModel):
    id: uuid.UUID
    materia_id: uuid.UUID
    texto: str
    criado_em: datetime
