"""Mede a correcao da IA contra notas conhecidas (so texto, sem OCR). Nao altera o projeto.

uso (de dentro de backend/):
    python -m calibracao.calibra <saida.jsonl> <modelo> [n1000] [nuol] [variante v2|v3a|v3b]
ex.: python -m calibracao.calibra ../docs/calibracao/nova.jsonl gemini-3.5-flash 20 30 v3a
Retoma de onde parou: redacoes ja presentes no jsonl sao puladas.
"""
import json, sys, time
from pathlib import Path

from google.genai import errors, types

from calibracao import variantes
from app.ocr.gemini import _client

if len(sys.argv) < 3:
    sys.exit(__doc__)
SAIDA, MODELO = Path(sys.argv[1]), sys.argv[2]
N1000 = int(sys.argv[3]) if len(sys.argv) > 3 else 20
NUOL = int(sys.argv[4]) if len(sys.argv) > 4 else 30
VARIANTE = sys.argv[5] if len(sys.argv) > 5 else "v2"
PROMPT, SCHEMA, CONV = variantes.pegar(VARIANTE)

amostra = variantes.amostra(N1000, NUOL)

feitas = {json.loads(l)["id"] for l in SAIDA.read_text(encoding="utf-8").splitlines()} if SAIDA.exists() else set()
cfg = types.GenerateContentConfig(temperature=0, response_mime_type="application/json", response_schema=SCHEMA)
print(f"amostra {len(amostra)} ({N1000} nota 1000 + {NUOL} UOL), ja feitas {len(feitas)}, modelo {MODELO}", flush=True)

for grupo, r in amostra:
    if str(r[0]) in feitas:
        continue
    for tentativa in range(6):
        t = time.time()
        try:
            resp = _client().models.generate_content(model=MODELO, contents=PROMPT.format(tema=r[2], texto=r[3]), config=cfg)
            fim = resp.candidates[0].finish_reason if resp.candidates else None
            if not resp.text:
                raise RuntimeError(f"resposta vazia ({fim})")
            res = CONV(SCHEMA.model_validate_json(resp.text))
            break
        except errors.ClientError as e:
            if e.code == 429 and "PerDay" in str(e):
                sys.exit(f"cota diaria do {MODELO} acabou; rode de novo amanha ou com outro modelo")
            espera = 30 if e.code == 429 else 5
            print(f"  {r[0]}: {e.code}, esperando {espera}s", flush=True); time.sleep(espera)
        except Exception as e:
            print(f"  {r[0]}: {type(e).__name__} {str(e)[:80]}", flush=True); time.sleep(15)
    else:
        print(f"  {r[0]}: desisti", flush=True); continue
    ia = [c.nota for c in res.competencias]
    real = [float(r[i]) for i in range(4, 9)]
    linha = {"id": str(r[0]), "grupo": grupo, "ano": r[1], "real": real, "ia": ia, "real_total": sum(real),
             "ia_total": sum(ia), "confianca": res.confianca, "modelo": MODELO, "variante": VARIANTE, "seg": round(time.time() - t, 1),
             "justificativas": [c.justificativa for c in res.competencias]}
    with SAIDA.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    print(f"{grupo} {r[0]} real={sum(real):.0f} ia={sum(ia)} ({linha['seg']}s)", flush=True)
