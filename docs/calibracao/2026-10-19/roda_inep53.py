"""Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da planilha. uso (de backend/): python <este> <prompt.txt> <saida.jsonl> <modelo>"""
import json, runpy, sys
from pathlib import Path
import openpyxl
from calibracao import variantes
E = Path.cwd().parent / "essays"
rows = [r for r in list(openpyxl.load_workbook(E / "base_redacoes_inep.xlsm", read_only=True, data_only=True)["Redações"].iter_rows(values_only=True))[1:] if r[0]]
ids = {r[0] for r in rows}
rows += [tuple(r) for r in map(json.loads, open(E / "novas_51_53.jsonl", encoding="utf-8")) if r[0] not in ids]
variantes.amostra = lambda a, b: [("inep", r) for r in rows]
variantes.VARIANTES["arq"] = (open(sys.argv[1], encoding="utf-8").read(), variantes.ResultadoIA, lambda r: r)
sys.argv = ["calibra", sys.argv[2], sys.argv[3], "0", "0", "arq"]
runpy.run_module("calibracao.calibra", run_name="__main__")
