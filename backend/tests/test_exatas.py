"""Correcao de exercicios de materias exatas (matematica/fisica/quimica): gabarito -> IA confere
resposta por questao -> professor aprova -> aluno ve a nota (sem entrar na evolucao de redacao).

    cd backend && python -m pytest tests/test_exatas.py
Mesma base de tests/test_fluxo_envio.py (sqlite temporario, sem chamar o Google de verdade).
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


def criar_turma_e_materia(prof):
    gestor = token("gestor@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    materia = client.post("/materias", headers=gestor,
                          json={"nome": "Matemática", "tipo": "MATERIA_OBJETIVA"}).json()
    return turma_id, materia["id"]


def criar_atividade_com_gabarito(prof, turma_id, materia_id):
    payload = {
        "materia_id": materia_id, "turma_id": turma_id, "titulo": "Lista 1 - Equações", "tipo": "EXERCICIO",
        "questoes": [
            {"enunciado": "Resolva 2x + 3 = 7", "resposta_correta": "x = 2"},
            {"enunciado": "Resolva 3x = 9", "resposta_correta": "x = 3"},
        ],
    }
    r = client.post("/atividades", headers=prof, json=payload)
    assert r.status_code == 201, r.text
    atividade = r.json()
    # o aluno precisa ver o enunciado real de cada questao (nao um texto fixo de outra materia)
    assert atividade["questoes"] == [
        {"codigo": "Q1", "enunciado": "Resolva 2x + 3 = 7"},
        {"codigo": "Q2", "enunciado": "Resolva 3x = 9"},
    ]
    return atividade


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


def test_atividade_de_exatas_exige_gabarito():
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    payload = {"materia_id": materia_id, "turma_id": turma_id, "titulo": "Sem gabarito", "tipo": "EXERCICIO"}
    assert client.post("/atividades", headers=prof, json=payload).status_code == 422


def test_fluxo_completo_exatas():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)
    assert atividade["materia"] == "Matemática"

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "Questão 1: x = 2\nQuestão 2: x = 5"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 0])
    try:
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        assert r.status_code == 201, r.text
        c = r.json()
        assert c["nota_ia"] == 200  # 200 + 0
        assert len(c["criterios"]) == 2
        codigos = sorted(k["codigo"] for k in c["criterios"])
        assert codigos == ["Q1", "Q2"]
        assert c["feedback"] == "1/2 questões corretas."

        # aprovar com so 2 criterios (nao precisa ser exatamente 5 como na redacao)
        aprovacao = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 200}, {"codigo": "Q2", "nota": 0}],
            "feedback": "Revise a segunda equação.",
        })
        assert aprovacao.status_code == 200, aprovacao.text
        assert aprovacao.json()["nota_professor"] == 200

        # aluno ve a nota (RN-01: so depois de aprovada)
        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["atividade_id"] == atividade["id"])
        assert desta["nota"] == 200 and desta["status"] == "APROVADA"

        # exatas nao alimenta a evolucao de redacao (tema especifico da atividade, nunca se repete)
        dominio = client.get("/dominio/meu", headers=aluno).json()
        codigos_dominio = {d["habilidade_codigo"] for d in dominio}
        assert not codigos_dominio & {"Q1", "Q2"}
    finally:
        exatas_mod.gerar = original


def test_aprovar_exige_todos_os_criterios():
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)
    aluno = token("aluno2@domina.com")
    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "x = 2 e x = 3"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 200])
    try:
        client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        r = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof,
                       json={"notas": [{"codigo": "Q1", "nota": 200}]})  # faltou Q2
        assert r.status_code == 422
    finally:
        exatas_mod.gerar = original


def test_so_professor_ou_gestor_criam_materia():
    aluno = token("aluno@domina.com")
    r = client.post("/materias", headers=aluno, json={"nome": "Física", "tipo": "MATERIA_OBJETIVA"})
    assert r.status_code == 403
