"""Roda corrigir() do app (v12, 2 correcoes + media) nas 53 do INEP. uso (de backend/):
DATABASE_URL=sqlite:// JWT_SECRET=x GEMINI_MODEL=gemini-3.5-flash-lite PYTHONPATH=. python <este> <saida.jsonl>
Retoma de onde parou. Resultado: python ../docs/calibracao/2026-10-18/analisa_inep.py <saida.jsonl>"""
import json, sys, time
from pathlib import Path
import openpyxl
from app import correcao
E = Path.cwd().parent / "essays"
rows = [r for r in list(openpyxl.load_workbook(E / "base_redacoes_inep.xlsm", read_only=True, data_only=True)["Redações"].iter_rows(values_only=True))[1:] if r[0]]
ids = {r[0] for r in rows}
rows += [tuple(r) for r in map(json.loads, open(E / "novas_51_53.jsonl", encoding="utf-8")) if r[0] not in ids]
saida = Path(sys.argv[1])
feitas = {json.loads(l)["id"] for l in saida.read_text(encoding="utf-8").splitlines()} if saida.exists() else set()
for r in rows:
    if str(r[0]) in feitas:
        continue
    for _ in range(5):
        t = time.time()
        try:
            res, modelo = correcao.corrigir(r[3], r[2]); break
        except Exception as e:
            print(f"  {r[0]}: {type(e).__name__} {str(e)[:80]}", flush=True); time.sleep(20)
    else:
        print(f"  {r[0]}: desisti", flush=True); continue
    ia = [c.nota for c in res.competencias]
    real = [float(r[i]) for i in range(4, 9)]
    linha = {"id": str(r[0]), "grupo": "inep", "ano": r[1], "real": real, "ia": ia, "real_total": sum(real), "ia_total": sum(ia),
             "confianca": res.confianca, "modelo": modelo, "variante": correcao.VERSAO_PROMPT, "seg": round(time.time() - t, 1)}
    with saida.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    print(f"{r[0]} real={sum(real):.0f} ia={sum(ia)} conf={res.confianca:.2f} ({linha['seg']}s)", flush=True)
