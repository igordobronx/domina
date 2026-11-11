"""Retencao dos logs no banco. Rodar periodicamente (Railway Cron / cron da VPS):  python retencao.py

- evento_seguranca e audit_log: apaga o que passou de RETENCAO_DIAS (padrao 365 = 12 meses).
- O access log (6 meses) NAO esta no banco: vive no stdout e a retencao e a do Railway/journald.
So apaga o COMECO da cadeia (as mais antigas): a verificacao parte da primeira linha que sobrou.
O resultado sai no stdout em JSON, com o hash da nova primeira linha, que serve de ancora.
"""
import logging
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.database import SessionLocal
from app.logs import configurar_logging
from app.models.usuario import AuditLog, EventoSeguranca

logger = logging.getLogger("domina.retencao")


def aplicar(db, dias: int) -> dict[str, int]:
    limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=dias)
    apagados = {}
    for modelo in (EventoSeguranca, AuditLog):
        apagados[modelo.__tablename__] = db.query(modelo).filter(modelo.criado_em < limite).delete(synchronize_session=False)
    db.commit()
    return apagados


if __name__ == "__main__":
    configurar_logging()
    with SessionLocal() as db:
        resultado = aplicar(db, settings.RETENCAO_DIAS)
    logger.info("retencao aplicada", extra={"campos": {"dias": settings.RETENCAO_DIAS, "apagados": resultado}})
