"""Eventos de seguranca (autenticacao e acesso negado) gravados no banco, so com INSERT.

Sessao propria: o evento fica gravado mesmo quando a requisicao que o causou da rollback/erro,
e uma falha ao gravar o log NUNCA derruba a requisicao (so vira um erro no stdout).

CADEIA DE HASH: cada linha guarda o hash da anterior. Alterar uma linha muda o hash dela e
quebra todas as seguintes; apagar uma no meio deixa um buraco em `seq`. O hash tambem sai na
linha JSON do stdout: essa copia (Railway/journald/destino externo) serve de ancora para detectar
quem apaga o FIM da tabela, o que a cadeia sozinha nao percebe.
"""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.cadeia import hash_de, proximo_elo, verificar
from app.database import SessionLocal
from app.logs import ip_ctx, request_id_ctx
from app.models.usuario import EventoSeguranca

logger = logging.getLogger("domina.seguranca")

LOGIN_OK, LOGIN_FALHA = "LOGIN_OK", "LOGIN_FALHA"
NAO_AUTENTICADO, ACESSO_NEGADO = "NAO_AUTENTICADO", "ACESSO_NEGADO"  # respostas 401 e 403
_LOCK = 7305001  # chave do advisory lock desta tabela


def _campos(e: EventoSeguranca) -> list:
    return [e.seq, str(e.id), e.criado_em.isoformat(), e.tipo, str(e.usuario_id) if e.usuario_id else None,
            e.email_tentado, e.ip, e.request_id, e.detalhe, e.hash_anterior]


def registrar_seguranca(tipo: str, usuario_id: uuid.UUID | None = None, email: str | None = None,
                        detalhe: str | None = None) -> None:
    hash_novo = None
    try:
        with SessionLocal() as db:
            seq, anterior = proximo_elo(db, EventoSeguranca, _LOCK)
            e = EventoSeguranca(
                id=uuid.uuid4(), criado_em=datetime.now(timezone.utc).replace(tzinfo=None),  # UTC, definido aqui para entrar no hash
                tipo=tipo, usuario_id=usuario_id, ip=ip_ctx.get(), request_id=request_id_ctx.get(),
                email_tentado=email.strip().lower()[:254] if email else None,  # so em LOGIN_FALHA
                detalhe=detalhe[:200] if detalhe else None,
                seq=seq, hash_anterior=anterior,
            )
            e.hash = hash_novo = hash_de(_campos(e))
            db.add(e)
            db.commit()
    except Exception:
        logger.exception("nao foi possivel gravar o evento de seguranca %s", tipo)
    logger.info(tipo, extra={"campos": {"evento": tipo, "usuario_id": str(usuario_id) if usuario_id else None,
                                        "ip": ip_ctx.get(), "detalhe": detalhe, "hash": hash_novo}})


def verificar_cadeia(db: Session) -> tuple[bool, str]:
    return verificar(db, EventoSeguranca, _campos)
