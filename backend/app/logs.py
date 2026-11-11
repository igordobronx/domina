"""Logging do sistema: JSON em stdout (uma linha por evento) + contexto da requisicao.

Onde vai parar:
- stdout: Railway mostra no painel "Logs"; na VPS o Docker manda para o journald/syslog do host.
- Banco (tabela evento_seguranca): so autenticacao e acesso negado (ver app/seguranca.py).
Nunca entra aqui: senha, token, corpo da requisicao, query string, texto de redacao, foto.
"""
import contextvars
import json
import logging
import sys
import uuid
from datetime import datetime, timezone

from fastapi import Request

from app.config import settings

# preenchidos pelo middleware a cada requisicao; quem loga depois (login, erro) herda sem receber argumento
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
ip_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("ip", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        linha = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),  # UTC
            "nivel": record.levelname,
            "logger": record.name,
            "request_id": request_id_ctx.get(),
            "msg": record.getMessage(),
            **getattr(record, "campos", {}),
        }
        if record.exc_info:
            linha["erro"] = self.formatException(record.exc_info)
        return json.dumps(linha, ensure_ascii=False, default=str)


def configurar_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    raiz = logging.getLogger()
    raiz.handlers = [handler]
    raiz.setLevel(settings.LOG_LEVEL.upper())
    # o access log do uvicorn seria duplicado (e sem usuario/request_id): o nosso middleware o substitui
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False


def novo_request_id() -> str:
    # sempre gerado aqui: um X-Request-ID vindo de fora poderia ser usado para forjar/poluir o log
    return uuid.uuid4().hex


def ip_do_cliente(request: Request) -> str:
    """IP real. Atras do proxy (Railway, Nginx) o IP do socket e o do proxy; o real vem em X-Forwarded-For.

    So confiamos no cabecalho com CONFIAR_PROXY=true: sem proxy, qualquer cliente o forjaria.
    Pegamos o ULTIMO valor: e o que o NOSSO proxy acrescentou; os anteriores o cliente pode ter inventado.
    """
    if settings.CONFIAR_PROXY:
        encaminhado = request.headers.get("x-forwarded-for", "")
        if encaminhado:
            return encaminhado.split(",")[-1].strip()[:45]
    return request.client.host if request.client else "-"
