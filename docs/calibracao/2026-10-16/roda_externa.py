"""Roda calibra.py com prompt de arquivo na planilha externa. uso (de backend/): python <este> <prompt.txt> <saida.jsonl> <modelo>"""
import runpy, sys
from pathlib import Path
import openpyxl
from calibracao import variantes
BASE = Path.cwd().parent / "essays" / "base_teste_externa.xlsm"
rows = [r for r in list(openpyxl.load_workbook(BASE, read_only=True, data_only=True)["Redações"].iter_rows(values_only=True))[1:] if r[0]]
variantes.amostra = lambda a, b: [("aes" if str(r[10]).startswith("AES") else "ebr", r) for r in rows]
variantes.VARIANTES["arq"] = (open(sys.argv[1], encoding="utf-8").read(), variantes.ResultadoIA, lambda r: r)
sys.argv = ["calibra", sys.argv[2], sys.argv[3], "0", "0", "arq"]
runpy.run_module("calibracao.calibra", run_name="__main__")
