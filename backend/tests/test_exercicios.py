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
    # so uma resposta: refazer e recusado e a primeira fica
    assert client.post(f"/exercicios/{ex['id']}/responder", headers=ana, json={"resposta": "1"}).status_code == 409
    stats = next(e for e in client.get("/exercicios", headers=p).json() if e["id"] == ex["id"])
    assert stats["respostas"] == 1 and stats["acertos"] == 0


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


def test_exercicio_so_para_alguns_alunos():
    p, c = _setup()
    g = token("gestor@domina.com")
    beto = client.post("/usuarios", headers=g, json={"nome": "Beto Exerc", "email": "beto.exerc@x.com",
                                                     "senha": "123456", "perfil": "ALUNO", "turma_id": c["turma"]}).json()["id"]
    caio_id = next(m["id"] for m in client.get(f"/turmas/{c['outra']}/membros", headers=g).json() if m["papel"] == "ALUNO")
    assert client.post("/exercicios", headers=p, json=_objetivo(c, aluno_ids=[caio_id])).status_code == 422
    ex = client.post("/exercicios", headers=p, json=_objetivo(c, titulo="Só do Beto", aluno_ids=[beto])).json()
    assert ex["alunos_nomes"] == ["Beto Exerc"]
    ana, beto_h = token("ana.exerc@x.com", "123456"), token("beto.exerc@x.com", "123456")
    assert all(e["id"] != ex["id"] for e in client.get("/exercicios/turma", headers=ana).json())
    assert client.post(f"/exercicios/{ex['id']}/responder", headers=ana, json={"resposta": "1"}).status_code == 404
    assert any(e["id"] == ex["id"] for e in client.get("/exercicios/turma", headers=beto_h).json())


def test_lote_respostas_avaliacao_e_resumo():
    p, c = _setup()
    g = token("gestor@domina.com")
    # o professor leciona nas duas turmas do teste so a partir daqui
    turma2 = client.post("/turmas", headers=g, json={"nome": "Turma Exerc 2", "ano": 2026}).json()["id"]
    prof_id = next(m["id"] for m in client.get(f"/turmas/{c['turma']}/membros", headers=g).json() if m["papel"] == "PROFESSOR")
    assert client.post(f"/turmas/{turma2}/matricular", headers=g, json={"usuario_id": prof_id, "papel": "PROFESSOR"}).status_code == 201
    disc = _objetivo(c, tipo="DISCURSIVO", alternativas=None, resposta_correta=None, resposta_exemplo="Quatro.",
                     titulo="Disc lote")
    del disc["turma_id"]
    assert client.post("/exercicios/lote", headers=p, json={**disc, "turma_ids": [c["turma"], c["outra"]]}).status_code == 403
    r = client.post("/exercicios/lote", headers=p, json={**disc, "turma_ids": [c["turma"], turma2]})
    assert r.status_code == 201 and len(r.json()) == 2 and r.json()[0]["id"] != r.json()[1]["id"]
    ex = r.json()[0]
    assert client.post("/exercicios/lote", headers=p, json={**disc, "turma_ids": [c["turma"], turma2],
                                                            "aluno_ids": [prof_id]}).status_code == 422  # nao e aluno

    linhas = client.get(f"/exercicios/{ex['id']}/respostas", headers=p).json()
    ana = next(l for l in linhas if l["nome"] == "Ana Exerc")
    assert ana["fez"] is False
    assert client.put(f"/exercicios/{ex['id']}/respostas/{ana['aluno_id']}", headers=p, json={"resultado": "CERTA"}).status_code == 404

    ana_h = token("ana.exerc@x.com", "123456")
    client.post(f"/exercicios/{ex['id']}/responder", headers=ana_h, json={"resposta": "É quatro"})
    r = client.put(f"/exercicios/{ex['id']}/respostas/{ana['aluno_id']}", headers=p,
                   json={"resultado": "PARCIAL"})
    assert r.status_code == 422  # parcial/errada sem comentario nao pode
    r = client.put(f"/exercicios/{ex['id']}/respostas/{ana['aluno_id']}", headers=p,
                   json={"resultado": "PARCIAL", "comentario": "Quase!"})
    assert r.status_code == 200 and r.json()["resultado"] == "PARCIAL" and r.json()["correta"] is None
    resumo = next(l for l in client.get(f"/exercicios/resumo?turma_id={c['turma']}", headers=p).json()
                  if l["nome"] == "Ana Exerc")
    assert resumo["parciais"] == 1
    r = client.put(f"/exercicios/{ex['id']}/respostas/{ana['aluno_id']}", headers=p,
                   json={"resultado": "CERTA", "comentario": "Boa!"})
    assert r.status_code == 200 and r.json()["correta"] is True
    meu = next(e for e in client.get("/exercicios/turma", headers=ana_h).json() if e["id"] == ex["id"])
    assert meu["resultado"] == "CERTA" and meu["comentario"] == "Boa!"
    resumo = next(l for l in client.get(f"/exercicios/resumo?turma_id={c['turma']}", headers=p).json()
                  if l["nome"] == "Ana Exerc")
    assert resumo["feitos"] >= 1 and resumo["acertos"] >= 1 and resumo["total"] >= resumo["feitos"]
    # nao da para responder de novo: a correcao fica
    assert client.post(f"/exercicios/{ex['id']}/responder", headers=ana_h, json={"resposta": "Outra"}).status_code == 409
    linha = next(l for l in client.get(f"/exercicios/{ex['id']}/respostas", headers=p).json() if l["nome"] == "Ana Exerc")
    assert linha["resultado"] == "CERTA" and linha["comentario"] == "Boa!"

    # alunos de turmas diferentes: cada turma recebe a copia so com os seus; turma sem escolhido fica de fora
    beto = client.post("/usuarios", headers=g, json={"nome": "Davi Exerc2", "email": "davi.exerc@x.com",
                                                     "senha": "123456", "perfil": "ALUNO", "turma_id": turma2}).json()["id"]
    turma3 = client.post("/turmas", headers=g, json={"nome": "Turma Exerc 3", "ano": 2026}).json()["id"]
    client.post(f"/turmas/{turma3}/matricular", headers=g, json={"usuario_id": prof_id, "papel": "PROFESSOR"})
    r = client.post("/exercicios/lote", headers=p, json={**disc, "titulo": "Mistos",
                    "turma_ids": [c["turma"], turma2, turma3], "aluno_ids": [ana["aluno_id"], beto]})
    assert r.status_code == 201, r.text
    assert sorted(e["turma_id"] for e in r.json()) == sorted([c["turma"], turma2])
    assert all(len(e["aluno_ids"]) == 1 for e in r.json())


def test_discursivo_com_varias_respostas_de_exemplo():
    p, c = _setup()
    disc = _objetivo(c, tipo="DISCURSIVO", alternativas=None, resposta_correta=None, titulo="Varias",
                     respostas_exemplo=["Primeira.", "  ", "Segunda."])
    r = client.post("/exercicios", headers=p, json=disc)
    assert r.status_code == 201, r.text
    assert r.json()["respostas_exemplo"] == ["Primeira.", "Segunda."] and r.json()["resposta_exemplo"] == "Primeira."
    assert client.post("/exercicios", headers=p, json={**disc, "respostas_exemplo": ["", " "]}).status_code == 422
    ana = token("ana.exerc@x.com", "123456")
    r = client.post(f"/exercicios/{r.json()['id']}/responder", headers=ana, json={"resposta": "Minha"}).json()
    assert r["respostas_exemplo"] == ["Primeira.", "Segunda."]
