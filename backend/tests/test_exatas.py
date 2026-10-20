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
    # sem valor_total explicito, assume 1000 (como a redacao) e divide pelas questoes
    assert atividade["valor_total"] == 1000.0
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
        # IA acerta/erra na escala relativa 0..200, mas a nota guardada ja vem reescalada: 1000
        # de valor_total / 2 questoes = 500 cada, entao 200/200 vira 500 e 0/200 vira 0
        assert c["nota_ia"] == 500  # 500 + 0
        assert len(c["criterios"]) == 2
        codigos = sorted(k["codigo"] for k in c["criterios"])
        assert codigos == ["Q1", "Q2"]
        assert c["feedback"] == "1/2 questões corretas."

        # aprovar com so 2 criterios (nao precisa ser exatamente 5 como na redacao)
        aprovacao = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 500}, {"codigo": "Q2", "nota": 0}],
            "feedback": "Revise a segunda equação.",
        })
        assert aprovacao.status_code == 200, aprovacao.text
        assert aprovacao.json()["nota_professor"] == 500

        # aluno ve a nota (RN-01: so depois de aprovada)
        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["atividade_id"] == atividade["id"])
        assert desta["nota"] == 500 and desta["status"] == "APROVADA"

        # exatas nao alimenta a evolucao de redacao (tema especifico da atividade, nunca se repete)
        dominio = client.get("/dominio/meu", headers=aluno).json()
        codigos_dominio = {d["habilidade_codigo"] for d in dominio}
        assert not codigos_dominio & {"Q1", "Q2"}
    finally:
        exatas_mod.gerar = original


def test_aluno_gera_propria_correcao_exatas_e_professor_aprova_depois():
    # mesma RN-01 relaxada do test_fluxo_envio.py, aqui pro lado de exatas
    prof, aluno = token("professor@domina.com"), token("aluno2@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "x = 2 e x = 3"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 200])
    try:
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=aluno, json={})
        assert r.status_code == 201, r.text

        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["id"] == sub["id"])
        # _gemini_falso usa um "modelo-falso" (nao o configurado), entao vai pra REQUER_ATENCAO;
        # a nota provisoria (nota_ia) ja aparece pro aluno de qualquer jeito
        assert desta["status"] == "REQUER_ATENCAO" and desta["nota"] == 1000  # 500 + 500, provisorio

        aprovacao = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 500}, {"codigo": "Q2", "nota": 500}],
        })
        assert aprovacao.status_code == 200, aprovacao.text

        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["id"] == sub["id"])
        assert desta["status"] == "APROVADA" and desta["nota"] == 1000
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


def test_valor_total_configuravel_e_dividido_pelas_questoes():
    # professor define o valor total da atividade (em vez de cada questao valer 200 fixo);
    # o sistema divide igualmente entre as questoes cadastradas
    prof, aluno = token("professor@domina.com"), token("aluno3@domina.com")
    gestor = token("gestor@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    materia = client.post("/materias", headers=gestor,
                          json={"nome": "Física II", "tipo": "MATERIA_OBJETIVA"}).json()
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": materia["id"], "turma_id": turma_id, "titulo": "Prova - 4 questões", "tipo": "PROVA_OBJETIVA",
        "valor_total": 400,
        "questoes": [
            {"enunciado": f"Questão {i}", "resposta_correta": f"resposta {i}"} for i in range(1, 5)
        ],
    }).json()
    assert atividade["valor_total"] == 400.0  # 4 questoes -> 100 pontos cada

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "respostas quaisquer"}).json()
    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 200, 80, 0])
    try:
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        assert r.status_code == 201, r.text
        c = r.json()
        # 200/200 * 100 = 100, 80/200 * 100 = 40, 0 -> 0
        notas = {k["codigo"]: k["nota"] for k in c["criterios"]}
        assert notas == {"Q1": 100.0, "Q2": 100.0, "Q3": 40.0, "Q4": 0.0}
        assert c["nota_ia"] == 240.0

        # professor nao pode dar mais do que o valor da questao (100) na aprovacao
        excesso = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": f"Q{i}", "nota": 200 if i == 1 else notas[f"Q{i}"]} for i in range(1, 5)],
        })
        assert excesso.status_code == 422

        ok = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": k, "nota": v} for k, v in notas.items()],
            "feedback": "Bom trabalho.",
        })
        assert ok.status_code == 200, ok.text
        assert ok.json()["nota_professor"] == 240.0
    finally:
        exatas_mod.gerar = original


def test_so_professor_ou_gestor_criam_materia():
    aluno = token("aluno@domina.com")
    r = client.post("/materias", headers=aluno, json={"nome": "Física", "tipo": "MATERIA_OBJETIVA"})
    assert r.status_code == 403


def test_enunciado_longo_nao_quebra_a_criacao():
    # bug real: Tema.nome era VARCHAR(150) no Postgres, mas um enunciado de prova discursiva
    # (gerado por IA, com contexto/formatacao) facilmente passa disso -> 500 ("Failed to fetch"
    # no navegador). Tema.nome agora e Text; este teste cobre a validacao do pydantic (max 2000).
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    enunciado_longo = "### **Questão 1** (Geometria Plana) " + "Lorem ipsum dolor sit amet. " * 50
    assert len(enunciado_longo) > 150
    r = client.post("/atividades", headers=prof, json={
        "materia_id": materia_id, "turma_id": turma_id, "titulo": "Prova discursiva", "tipo": "PROVA_DISCURSIVA",
        "questoes": [{"enunciado": enunciado_longo, "resposta_correta": "x = 42"}],
    })
    assert r.status_code == 201, r.text
    assert r.json()["questoes"][0]["enunciado"] == enunciado_longo.strip()
