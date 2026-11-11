"""Cadeia de hash compartilhada pelos logs append-only (evento_seguranca e audit_log).

Cada linha guarda seq, hash_anterior e hash = sha256(campos da linha + hash_anterior).
Alterar uma linha quebra todas as seguintes; apagar uma no meio deixa um buraco em seq.
Apagar o FIM da tabela a cadeia nao ve: para isso o hash tambem sai no stdout (copia fora do banco).
"""
import hashlib
import json
from typing import Callable

from sqlalchemy import text
from sqlalchemy.orm import Session

GENESIS = "0" * 64  # "hash anterior" da primeira linha


def hash_de(campos: list) -> str:
    return hashlib.sha256(json.dumps(campos, separators=(",", ":"), ensure_ascii=False, default=str).encode()).hexdigest()


def proximo_elo(db: Session, modelo, chave_lock: int) -> tuple[int, str]:
    """(seq, hash_anterior) da proxima linha. Chamar DEPOIS de ter definido os campos e ANTES do add."""
    if db.get_bind().dialect.name == "postgresql":
        # duas gravacoes ao mesmo tempo leriam o mesmo "anterior" e bifurcariam a cadeia: o lock
        # serializa e solta sozinho no commit/rollback da transacao
        db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": chave_lock})
    ultimo = db.query(modelo).filter(modelo.seq.isnot(None)).order_by(modelo.seq.desc()).first()
    return ((ultimo.seq + 1, ultimo.hash) if ultimo else (1, GENESIS))


def verificar(db: Session, modelo, campos: Callable) -> tuple[bool, str]:
    """Confere a cadeia inteira; devolve (integra, mensagem com a primeira quebra)."""
    anterior, total = None, 0
    for e in db.query(modelo).filter(modelo.seq.isnot(None)).order_by(modelo.seq):
        if anterior is None:
            pass  # primeira que sobrou (a retencao pode ter apagado as antigas): ponto de partida
        elif e.seq != anterior.seq + 1:
            return False, f"linha(s) apagada(s) entre seq {anterior.seq} e {e.seq}"
        elif e.hash_anterior != anterior.hash:
            return False, f"seq {e.seq}: a linha anterior foi alterada"
        if hash_de(campos(e)) != e.hash:
            return False, f"seq {e.seq}: conteudo alterado"
        anterior, total = e, total + 1
    return True, f"cadeia integra ({total} registros)"
