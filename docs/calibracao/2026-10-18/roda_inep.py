"""Roda calibra.py com prompt de arquivo na base INEP (nota oficial). uso (de backend/): python <este> <prompt.txt> <saida.jsonl> <modelo>"""
import runpy, sys
from pathlib import Path
import openpyxl
from calibracao import variantes
BASE = Path.cwd().parent / "essays" / "base_redacoes_final_inep.xlsm"
rows = [r for r in list(openpyxl.load_workbook(BASE, read_only=True, data_only=True)["Redações"].iter_rows(values_only=True))[1:] if r[0]]
variantes.amostra = lambda a, b: [("inep", r) for r in rows]
variantes.VARIANTES["arq"] = (open(sys.argv[1], encoding="utf-8").read(), variantes.ResultadoIA, lambda r: r)
sys.argv = ["calibra", sys.argv[2], sys.argv[3], "0", "0", "arq"]
runpy.run_module("calibracao.calibra", run_name="__main__")
