"""Exercicios do professor: criar (objetivo/discursivo), IA sugere rascunhos, aluno responde e o
gabarito so aparece depois. A IA e falsa (nao chama o Claude).

    cd backend && python -m pytest tests/test_exercicios.py
"""
from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)

import app.exercicios_ia as ia_mod  # noqa: E402

_c = {}


def _setup():
    g = token("gestor@domina.com")
    if not _c:
        turma = client.post("/turmas", headers=g, json={"nome": "Turma Exerc", "ano": 2026}).json()["id"]
        outra = client.post("/turmas", headers=g, json={"nome": "Turma Exerc Alheia", "ano": 2026}).json()["id"]
        mk = lambda nome, email, perfil, t: client.post("/usuarios", headers=g, json={  # noqa: E731
            "nome": nome, "email": email, "senha": "123456", "perfil": perfil, "turma_id": t}).json()["id"]
        mk("Prof Exerc", "prof.exerc@x.com", "PROFESSOR", turma)
        mk("Ana Exerc", "ana.exerc@x.com", "ALUNO", turma)
        mk("Caio Exerc", "caio.exerc@x.com", "ALUNO", outra)
        materia = client.post("/materias", headers=g, json={"nome": "Matematica Ex", "tipo": "MATERIA_OBJETIVA"}).json()["id"]
        _c.update(turma=turma, outra=outra, materia=materia)
    return token("prof.exerc@x.com", "123456"), _c


def _objetivo(c, **k):
    return {"titulo": "Soma", "assunto": "Aritmética", "materia_id": c["materia"], "turma_id": c["turma"],
            "tipo": "OBJETIVO", "enunciado": "Quanto é 2+2?", "alternativas": ["3", "4", "5"],
            "resposta_correta": 1, "explicacao": "2+2=4", **k}


def test_criar_validacoes_e_permissoes():
    p, c = _setup()
    assert client.post("/exercicios", headers=p, json=_objetivo(c)).status_code == 201
    assert client.post("/exercicios", headers=p, json=_objetivo(c, alternativas=["so uma"])).status_code == 422
    assert client.post("/exercicios", headers=p, json=_objetivo(c, resposta_correta=5)).status_code == 422
    disc = _objetivo(c, tipo="DISCURSIVO", alternativas=None, resposta_correta=None)
    assert client.post("/exercicios", headers=p, json=disc).status_code == 422  # sem resposta de exemplo
    r = client.post("/exercicios", headers=p, json={**disc, "resposta_exemplo": "Quatro."})
    assert r.status_code == 201 and r.json()["alternativas"] is None
    assert client.post("/exercicios", headers=p, json=_objetivo(c, turma_id=c["outra"])).status_code == 403
    aluno = token("ana.exerc@x.com", "123456")
    assert client.post("/exercicios", headers=aluno, json=_objetivo(c)).status_code == 403
    assert client.get("/exercicios", headers=aluno).status_code == 403


def test_aluno_ve_so_da_turma_e_gabarito_depois_de_responder():
    p, c = _setup()
    ex = client.post("/exercicios", headers=p, json=_objetivo(c, titulo="Gabarito escondido")).json()
    ana, caio = token("ana.exerc@x.com", "123456"), token("caio.exerc@x.com", "123456")
    lista = client.get("/exercicios/turma", headers=ana).json()
    meu = next(e for e in lista if e["id"] == ex["id"])
    assert meu["resposta_correta"] is None and meu["explicacao"] is None  # ainda nao respondeu
    assert all(e["id"] != ex["id"] for e in client.get("/exercicios/turma", headers=caio).json())
    assert client.post(f"/exercicios/{ex['id']}/responder", headers=caio, json={"resposta": "1"}).status_code == 404

    r = client.post(f"/exercicios/{ex['id']}/responder", headers=ana, json={"resposta": "0"}).json()
    assert r["correta"] is False and r["resposta_correta"] == 1
    r = client.post(f"/exercicios/{ex['id']}/responder", headers=ana, json={"resposta": "1"}).json()
    assert r["correta"] is True
    stats = next(e for e in client.get("/exercicios", headers=p).json() if e["id"] == ex["id"])
    assert stats["respostas"] == 1 and stats["acertos"] == 1  # guarda so a ultima tentativa


def test_editar_e_excluir_somem_para_o_aluno():
    p, c = _setup()
    ex = client.post("/exercicios", headers=p, json=_objetivo(c, titulo="Vai sumir")).json()
    r = client.put(f"/exercicios/{ex['id']}", headers=p, json=_objetivo(c, titulo="Editado"))
    assert r.status_code == 200 and r.json()["titulo"] == "Editado"
    assert client.delete(f"/exercicios/{ex['id']}", headers=p).status_code == 204
    ana = token("ana.exerc@x.com", "123456")
    assert all(e["id"] != ex["id"] for e in client.get("/exercicios/turma", headers=ana).json())


def test_ia_sugere_rascunhos_sem_salvar():
    p, c = _setup()
    pedidos = []

    def falso(prompt, schema, temperature=0, model=None):
        pedidos.append(prompt)
        if "resposta_exemplo\": \"...\"" in prompt:
            return schema.model_validate({"resposta_exemplo": "Modelo."}), "falso"
        return schema.model_validate({"exercicios": [
            {"titulo": f"t{i}", "enunciado": "e", "alternativas": ["a", "b", "c", "d"], "resposta_correta": 9,
             "explicacao": "x"} for i in range(5)]}), "falso"

    original, ia_mod.gerar_json = ia_mod.gerar_json, falso
    try:
        antes = len(client.get("/exercicios", headers=p).json())
        r = client.post("/exercicios/sugerir", headers=p, json={
            "materia_id": c["materia"], "assunto": "Função afim", "tipo": "OBJETIVO", "quantidade": 2})
        assert r.status_code == 200, r.text
        assert len(r.json()) == 2 and r.json()[0]["resposta_correta"] == 0  # indice invalido vira 0
        assert "Função afim" in pedidos[0] and "Matematica Ex" in pedidos[0]
        assert len(client.get("/exercicios", headers=p).json()) == antes  # nada foi salvo
        r = client.post("/exercicios/sugerir-resposta", headers=p, json={
            "materia_id": c["materia"], "enunciado": "Explique a função afim."})
        assert r.json() == {"resposta_exemplo": "Modelo."}
    finally:
        ia_mod.gerar_json = original
