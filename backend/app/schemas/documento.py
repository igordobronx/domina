import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enum import StatusProcessamentoEnum, TipoDocumentoEnum


class DocumentoBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    materia_id: uuid.UUID
    nome_arquivo: str
    tipo: TipoDocumentoEnum
    status_processamento: StatusProcessamentoEnum
