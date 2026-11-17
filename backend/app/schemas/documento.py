import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enum import StatusProcessamentoEnum, TipoDocumentoEnum


class DocumentoBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    materia_id: uuid.UUID
    materia_nome: str = ""
    nome_arquivo: str
    tipo: TipoDocumentoEnum
    status_processamento: StatusProcessamentoEnum
    tamanho_bytes: int | None = None
    enviado_por_nome: str = ""
    pode_baixar: bool = False  # false nos enviados antes de o arquivo ser guardado com caminho
    criado_em: datetime
