"""Niveis e metas: escopo (escola/turma/aluno), conclusao automatica, nivel por pontos e ranking so da equipe."""
from datetime import date, timedelta

from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)

_c = {}


def _setup():
    """Turma, professor e dois alunos PROPRIOS deste teste (nao mexe nos do seed)."""
    g = token("gestor@domina.com")
    if not _c:
        turma = client.post("/turmas", headers=g, json={"nome": "Turma Metas", "ano": 2026}).json()["id"]
        outra = client.post("/turmas", headers=g, json={"nome": "Turma Alheia", "ano": 2026}).json()["id"]
        mk = lambda nome, email, perfil, t: client.post("/usuarios", headers=g, json={  # noqa: E731
            "nome": nome, "email": email, "senha": "123456", "perfil": perfil, "turma_id": t}).json()["id"]
        prof = mk("Prof Metas", "prof.metas@x.com", "PROFESSOR", turma)
        a1 = mk("Ana Meta", "ana.meta@x.com", "ALUNO", turma)
        a2 = mk("Beto Meta", "beto.meta@x.com", "ALUNO", turma)
        a3 = mk("Caio Alheio", "caio.meta@x.com", "ALUNO", outra)
        materia = client.post("/materias", headers=g, json={"nome": "Mat Metas", "tipo": "MATERIA_OBJETIVA"}).json()["id"]
        _c.update(turma=turma, outra=outra, prof=prof, a1=a1, a2=a2, a3=a3, materia=materia)
    return g, token("prof.metas@x.com", "123456"), _c


def _meta(h, **k):
    base = {"titulo": "Entregar 1", "tipo": "ENTREGAS", "alvo": 1, "pontos": 30}
    return client.post("/metas", headers=h, json={**base, **k})


def _entregar_objetiva(prof, aluno_id, materia, turma, valor=10):
    """Cria uma prova objetiva de 1 questao na turma e o aluno acerta (correcao nasce aprovada)."""
    ativ = client.post("/atividades/lote", headers=prof, json={
        "materia_id": materia, "turma_ids": [turma], "titulo": "Prova", "tipo": "PROVA_OBJETIVA", "valor_total": valor,
        "questoes": [{"enunciado": "1+1?", "alternativas": ["1", "2"], "resposta_correta": "B"}]}).json()[0]
    r = client.post("/submissoes/objetiva", headers=prof, json={"atividade_id": ativ["id"], "aluno_id": aluno_id, "respostas": {"Q1": "B"}})
    assert r.status_code == 201, r.text


def test_escopo_e_permissoes_de_criacao():
    g, p, c = _setup()
    assert _meta(p, turma_id=c["turma"]).status_code == 201
    assert _meta(p, aluno_id=c["a1"]).status_code == 201
    assert _meta(p).status_code == 403                                # escola toda: so gestor
    assert _meta(p, turma_id=c["outra"]).status_code == 403           # turma que ele nao leciona
    assert _meta(p, aluno_id=c["a3"]).status_code == 404              # aluno de outra turma
    assert _meta(p, turma_id=c["turma"], aluno_id=c["a1"]).status_code == 422
    assert _meta(p, tipo="DOMINIO_COMPETENCIA", alvo=80, turma_id=c["turma"]).status_code == 422  # sem materia/competencia
    assert _meta(g).status_code == 201                                 # gestor: escola toda
    aluno = token("ana.meta@x.com", "123456")
    assert _meta(aluno).status_code == 403                             # aluno nao cria
    assert client.get("/metas/ranking", headers=aluno).status_code == 403  # nem ve o ranking


def test_meta_conclui_sozinha_sobe_nivel_e_aparece_no_ranking():
    g, p, c = _setup()
    antes = token("beto.meta@x.com", "123456")
    assert client.get("/metas/minhas", headers=antes).json()["nivel"]["nivel"] == 1
    m = _meta(p, titulo="Primeira entrega", aluno_id=c["a2"], pontos=25).json()
    _entregar_objetiva(p, c["a2"], c["materia"], c["turma"])
    r = client.get("/metas/minhas", headers=antes).json()
    mine = next(x for x in r["metas"] if x["id"] == m["id"])
    assert mine["status"] == "CONCLUIDA" and mine["progresso"] == 1
    assert r["nivel"]["pontos"] >= 25 and r["nivel"]["nivel"] >= 2    # 20+ pontos = Aprendiz
    # meta individual: a colega nao enxerga a do Beto
    ana = client.get("/metas/minhas", headers=token("ana.meta@x.com", "123456")).json()
    assert m["id"] not in [x["id"] for x in ana["metas"]]
    # ranking: so equipe, ordenado por pontos
    rank = client.get("/metas/ranking", headers=p).json()
    assert rank[0]["nome"] == "Beto Meta" and rank[0]["pontos"] >= 25
    assert "Caio Alheio" not in [x["nome"] for x in rank]              # professor so ve as turmas dele
    assert client.get(f"/metas/ranking?turma_id={c['outra']}", headers=p).status_code == 404
    assert any(x["nome"] == "Caio Alheio" for x in client.get("/metas/ranking", headers=g).json())


def test_meta_nova_nao_conta_o_passado_e_nota_percentual():
    g, p, c = _setup()
    amanha = (date.today() + timedelta(days=1)).isoformat()
    futura = _meta(p, titulo="Amanhã", aluno_id=c["a1"], inicio=amanha).json()
    ana = token("ana.meta@x.com", "123456")
    _entregar_objetiva(p, c["a1"], c["materia"], c["turma"])
    item = next(x for x in client.get("/metas/minhas", headers=ana).json()["metas"] if x["id"] == futura["id"])
    assert item["status"] == "FUTURA"                                  # entrega de hoje nao conta numa meta que comeca amanha
    nota = _meta(p, titulo="Tirar 100%", tipo="NOTA_ATIVIDADE", alvo=100, aluno_id=c["a1"], pontos=10).json()
    _entregar_objetiva(p, c["a1"], c["materia"], c["turma"])           # 100% de uma prova de 10 pontos
    item = next(x for x in client.get("/metas/minhas", headers=ana).json()["metas"] if x["id"] == nota["id"])
    assert item["status"] == "CONCLUIDA"


def test_editar_arquivar_e_pontos_ficam():
    g, p, c = _setup()
    m = _meta(p, titulo="Para editar", turma_id=c["turma"], pontos=5, alvo=50).json()
    assert client.put(f"/metas/{m['id']}", headers=p, json={"titulo": "Novo título", "alvo": 60}).json()["titulo"] == "Novo título"
    outro = token("gestor@domina.com")
    assert client.put(f"/metas/{m['id']}", headers=outro, json={"pontos": 7}).status_code == 200  # gestor edita a do professor
    # outra escola nao enxerga: 404
    assert client.delete(f"/metas/{m['id']}", headers=p).status_code == 204
    assert m["id"] not in [x["id"] for x in client.get("/metas", headers=p).json()]
    # apos concluida, alvo/pontos congelam (409)
    k = _meta(p, titulo="Congela", aluno_id=c["a2"], alvo=1, pontos=3).json()
    _entregar_objetiva(p, c["a2"], c["materia"], c["turma"])
    assert client.put(f"/metas/{k['id']}", headers=p, json={"pontos": 99}).status_code == 409
    assert client.put(f"/metas/{k['id']}", headers=p, json={"titulo": "ok"}).status_code == 200
    antes = client.get("/metas/minhas", headers=token("beto.meta@x.com", "123456")).json()["nivel"]["pontos"]
    client.delete(f"/metas/{k['id']}", headers=p)                       # arquivar nao tira pontos ja ganhos
    assert client.get("/metas/minhas", headers=token("beto.meta@x.com", "123456")).json()["nivel"]["pontos"] == antes
