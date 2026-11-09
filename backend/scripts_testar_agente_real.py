"""Roda o agente de verdade (Claude + Gemini, GASTA API) num banco temporario e imprime o passo a passo.

    cd backend && ../venv/bin/python scripts_testar_agente_real.py [texto.txt]
Precisa de ANTHROPIC_API_KEY e GEMINI_API_KEY no ambiente/.env. Fora da suite de testes de proposito.
"""
import os
import sys
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/real.db"
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ["UPLOAD_DIR"] = f"{_tmp}/uploads"

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.usuario import Atividade  # noqa: E402

seed.run_seed()
client = TestClient(app)
login = client.post("/auth/login", json={"email": "aluno@domina.com", "senha": seed.SENHA}).json()
h = {"Authorization": f"Bearer {login['access_token']}"}
texto = open(sys.argv[1]).read() if len(sys.argv) > 1 else "A educacao no Brasil precisa melhorar. " * 20
with SessionLocal() as db:
    atividade = str(db.query(Atividade).first().id)
sub = client.post("/submissoes/texto", headers=h, json={"atividade_id": atividade, "texto": texto}).json()
r = client.post(f"/submissoes/{sub['id']}/agente", headers=h, json={})
print(r.status_code)
for p in r.json().get("passos", []):
    print(p.get("ferramenta") or p["tipo"], "|", p.get("motivo") or p.get("texto", ""), "| erro" if p.get("erro") else "")
print("nota:", (r.json().get("correcao") or {}).get("nota_ia"), "| resumo:", r.json().get("resumo_professor"))
