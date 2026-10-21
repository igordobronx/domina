"""Mede a correcao da IA contra notas conhecidas, via Groq (gratis). Nao altera o projeto.

Usa a MESMA amostra (seed 42) e o MESMO prompt que calibra.py, pra ficar comparavel.
Groq nao suporta response_schema (saida estruturada forcada) como o Gemini: o formato
JSON pedido no proprio texto do prompt (ver app/correcao.py) e o que ele realmente segue.

uso (de dentro de backend/):
    python -m calibracao.calibra_groq <saida.jsonl> <modelo> [n1000] [nuol] [variante v2|v3a|v3b]
ex.: python -m calibracao.calibra_groq ../docs/calibracao/groq.jsonl openai/gpt-oss-120b 20 30 v2
Retoma de onde parou: redacoes ja presentes no jsonl sao puladas.
"""
import json, sys, time
from pathlib import Path

import httpx

from calibracao import variantes

CODIGOS = ["c1", "c2", "c3", "c4", "c5"]


def _groq_key() -> str:
    # sem python-dotenv no venv de calibracao; leitura simples do backend/.env
    for linha in (Path(__file__).resolve().parents[1] / ".env").read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith("GROQ_API_KEY"):
            return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("GROQ_API_KEY nao encontrada em backend/.env")


if len(sys.argv) < 3:
    sys.exit(__doc__)
SAIDA, MODELO = Path(sys.argv[1]), sys.argv[2]
N1000 = int(sys.argv[3]) if len(sys.argv) > 3 else 20
NUOL = int(sys.argv[4]) if len(sys.argv) > 4 else 30
VARIANTE = sys.argv[5] if len(sys.argv) > 5 else "v2"
PROMPT, _, _ = variantes.pegar(VARIANTE)  # SCHEMA/CONV sao do Gemini; aqui nao se aplicam
GROQ_KEY = _groq_key()

amostra = variantes.amostra(N1000, NUOL)
feitas = {json.loads(l)["id"] for l in SAIDA.read_text(encoding="utf-8").splitlines()} if SAIDA.exists() else set()
print(f"amostra {len(amostra)} ({N1000} nota 1000 + {NUOL} UOL), ja feitas {len(feitas)}, modelo {MODELO}", flush=True)


def chamar(prompt: str) -> dict:
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={
            "model": MODELO,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_completion_tokens": 8000,
            "reasoning_effort": "low",
            "response_format": {"type": "json_object"},
        },
        timeout=90,
    )
    if r.status_code == 429:
        raise TimeoutError(r.headers.get("retry-after", "30"))
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


for grupo, r in amostra:
    if str(r[0]) in feitas:
        continue
    for tentativa in range(6):
        t = time.time()
        try:
            corpo = chamar(PROMPT.format(tema=r[2], texto=r[3]))
            comp = corpo["competencias"]
            if isinstance(comp, list):  # formato atual do prompt: lista com "codigo" C1..C5
                comp = {str(x["codigo"]).lower(): x for x in comp}
            ia = [float(comp[c]["nota"]) for c in CODIGOS]
            justificativas = [comp[c].get("justificativa") or comp[c].get("analise", "") for c in CODIGOS]
            confianca = float(corpo.get("confianca", 0))
            break
        except TimeoutError as e:
            espera = int(e.args[0]) if e.args[0].isdigit() else 30
            print(f"  {r[0]}: 429, esperando {espera}s", flush=True); time.sleep(espera)
        except Exception as e:
            print(f"  {r[0]}: {type(e).__name__} {str(e)[:80]}", flush=True); time.sleep(10)
    else:
        print(f"  {r[0]}: desisti", flush=True); continue
    real = [float(r[i]) for i in range(4, 9)]
    linha = {"id": str(r[0]), "grupo": grupo, "ano": r[1], "real": real, "ia": ia, "real_total": sum(real),
             "ia_total": sum(ia), "confianca": confianca, "modelo": MODELO, "variante": VARIANTE, "seg": round(time.time() - t, 1),
             "justificativas": justificativas}
    with SAIDA.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    print(f"{grupo} {r[0]} real={sum(real):.0f} ia={sum(ia):.0f} ({linha['seg']}s)", flush=True)
