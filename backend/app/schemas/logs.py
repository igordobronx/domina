import uuid
from datetime import datetime

from pydantic import BaseModel


class EventoSegurancaResponse(BaseModel):
    seq: int | None
    criado_em: datetime  # UTC
    tipo: str
    usuario: str | None  # nome, se a conta existe
    email_tentado: str | None
    ip: str
    request_id: str
    detalhe: str | None


class AuditoriaResponse(BaseModel):
    seq: int | None
    criado_em: datetime  # UTC
    usuario: str | None
    escola: str | None
    acao: str
    entidade: str
    entidade_id: uuid.UUID
    resultado: str | None
    # so o admin recebe: o gestor nao ve IP nem request_id (dado pessoal de quem trabalha na escola)
    ip: str | None = None
    request_id: str | None = None


class IntegridadeResponse(BaseModel):
    seguranca_ok: bool
    seguranca: str
    auditoria_ok: bool
    auditoria: str
