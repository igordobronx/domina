"""Evolucao real por materia: historico de correcoes aprovadas, agrupado por materia.
Cobre redacao (5 criterios, escala 0-1000) e exatas (N questoes, escala 0-200 cada) com a
MESMA rota, sem depender do dominio_aluno (que exatas deliberadamente nao alimenta).

    cd backend && python -m pytest tests/test_evolucao.py
"""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
import app.correcao_exatas as exatas_mod  # noqa: E402
from app.main import app  # noqa: E402

seed.run_seed()
client = TestClient(app)


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _gemini_falso(notas):
    import json
    from types import SimpleNamespace

    def gerar(prompt, config):
        payload = {
            "questoes": [{"codigo": f"Q{i+1}", "nota": n, "justificativa": "x"} for i, n in enumerate(notas)],
            "confianca": 0.9,
        }
        return SimpleNamespace(text=json.dumps(payload)), "modelo-falso"
    return gerar


def test_evolucao_agrupa_por_materia_sem_tocar_dominio():
    prof, aluno = token("professor@domina.com"), token("aluno3@domina.com")
    gestor = token("gestor@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    materia = client.post("/materias", headers=gestor,
                          json={"nome": "Química", "tipo": "MATERIA_OBJETIVA"}).json()
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": materia["id"], "turma_id": turma_id, "titulo": "Lista - Estequiometria", "tipo": "EXERCICIO",
        "questoes": [
            {"enunciado": "Quantos mols em 36g de água?", "resposta_correta": "2 mols"},
            {"enunciado": "Qual a massa molar do O2?", "resposta_correta": "32 g/mol"},
        ],
    }).json()

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "2 mols e 16 g/mol"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 0])
    try:
        client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        aprovacao = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 200}, {"codigo": "Q2", "nota": 0}],
        })
        assert aprovacao.status_code == 200, aprovacao.text

        evolucao = client.get("/evolucao/minha", headers=aluno).json()
        quimica = next(e for e in evolucao if e["materia"] == "Química")
        assert quimica["media_percentual"] == 50.0  # 200/(2*200)*100
        assert quimica["num_atividades"] == 1
        assert len(quimica["historico"]) == 1
        assert quimica["historico"][0]["atividade_titulo"] == "Lista - Estequiometria"

        # confirma que, mesmo alimentando a evolucao, exatas continua fora do dominio_aluno
        dominio = client.get("/dominio/meu", headers=aluno).json()
        assert not {d["habilidade_codigo"] for d in dominio} & {"Q1", "Q2"}
    finally:
        exatas_mod.gerar = original


def test_evolucao_so_para_aluno():
    prof = token("professor@domina.com")
    assert client.get("/evolucao/minha", headers=prof).status_code == 403
