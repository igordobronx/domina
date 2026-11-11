"""Log de auditoria (quem fez o que sobre quais dados), append-only e com cadeia de hash.

Roda na transacao de quem chama (db.add; o commit e da rota): se a acao der rollback, o registro
dela tambem some, o que e o certo para "o que de fato aconteceu". Escola, IP e request_id saem
sozinhos do usuario e do contexto da requisicao, entao as rotas continuam chamando como antes.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.cadeia import hash_de, proximo_elo, verificar
from app.logs import ip_ctx, request_id_ctx
from app.models.usuario import AuditLog, Usuario

_LOCK = 7305002  # advisory lock desta tabela (a do evento_seguranca e 7305001)


def _campos(a: AuditLog) -> list:
    return [a.seq, str(a.id), a.criado_em.isoformat(), str(a.usuario_id), str(a.escola_id) if a.escola_id else None,
            a.acao, a.entidade, str(a.entidade_id), a.ip, a.request_id, a.resultado, a.hash_anterior]


def registrar(db: Session, usuario_id, acao: str, entidade: str, entidade_id, resultado: str = "OK") -> None:
    autor = db.get(Usuario, usuario_id)
    seq, anterior = proximo_elo(db, AuditLog, _LOCK)
    a = AuditLog(
        id=uuid.uuid4(), criado_em=datetime.now(timezone.utc).replace(tzinfo=None),  # UTC, entra no hash
        usuario_id=usuario_id, escola_id=autor.escola_id if autor else None, acao=acao, entidade=entidade,
        entidade_id=entidade_id, ip=ip_ctx.get(), request_id=request_id_ctx.get(), resultado=resultado,
        seq=seq, hash_anterior=anterior,
    )
    a.hash = hash_de(_campos(a))
    db.add(a)
    db.flush()  # o proximo registrar() na mesma transacao enxerga este como "ultimo"


def verificar_auditoria(db: Session) -> tuple[bool, str]:
    return verificar(db, AuditLog, _campos)
