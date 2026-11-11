"""Confere a cadeia de hash dos dois logs.  python verificar_logs.py  (sai com codigo 1 se alguma quebrou)"""
import sys

from app.auditoria import verificar_auditoria
from app.database import SessionLocal
from app.seguranca import verificar_cadeia

falhou = False
with SessionLocal() as db:
    for nome, verificar in (("seguranca", verificar_cadeia), ("auditoria", verificar_auditoria)):
        ok, mensagem = verificar(db)
        falhou |= not ok
        print(f"{nome}: " + ("OK: " if ok else "ADULTERADO: ") + mensagem)
sys.exit(1 if falhou else 0)
