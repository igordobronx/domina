"""Professor com varias turmas: lancar em lote, editar e excluir/arquivar atividade."""
from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)


_cache = {}


def _setup():
    """Um professor PROPRIO deste teste (nao mexe no do seed, que os outros testes usam) com duas turmas."""
    g = token("gestor@domina.com")
    if not _cache:
        t1 = next(t["id"] for t in client.get("/turmas/minhas", headers=g).json() if t["nome"] == "3º Ano A")  # tem aluno
        t2 = client.post("/turmas", headers=g, json={"nome": "3º Ano B", "ano": 2026}).json()["id"]
        prof = client.post("/usuarios", headers=g, json={"nome": "Prof Lote", "email": "prof.lote@x.com",
                           "senha": "123456", "perfil": "PROFESSOR", "turma_id": t1}).json()
        client.post(f"/turmas/{t2}/matricular", headers=g, json={"usuario_id": prof["id"], "papel": "PROFESSOR"})
        materia = client.post("/materias", headers=g, json={"nome": "Física", "tipo": "MATERIA_OBJETIVA"}).json()["id"]
        _cache.update(t1=t1, t2=t2, materia=materia)
    p = token("prof.lote@x.com", "123456")
    return g, p, _cache["t1"], _cache["t2"], _cache["materia"]


def _lote(p, materia, turmas, **extra):
    return client.post("/atividades/lote", headers=p, json={
        "materia_id": materia, "turma_ids": turmas, "titulo": "Lista de Cinemática", "tipo": "EXERCICIO",
        "questoes": [{"enunciado": "v = d/t, d=10 e t=2", "resposta_correta": "5"}], **extra})


def test_lote_cria_uma_atividade_independente_por_turma():
    g, p, t1, t2, materia = _setup()
    r = _lote(p, materia, [t1, t2, t1], prazo="2030-05-10")  # t1 repetida: so uma
    assert r.status_code == 201, r.text
    criadas = r.json()
    assert len(criadas) == 2 and criadas[0]["id"] != criadas[1]["id"]
    assert {a["turma"] for a in criadas} == {"3º Ano A", "3º Ano B"}
    assert all(a["prazo"] == "2030-05-10" and a["questoes"][0]["enunciado"] for a in criadas)


def test_lote_e_tudo_ou_nada_e_professor_so_nas_proprias_turmas():
    g, p, t1, t2, materia = _setup()
    alheia = client.post("/turmas", headers=g, json={"nome": "Turma sem o professor", "ano": 2026}).json()["id"]
    antes = len(client.get("/atividades", headers=p).json())
    r = _lote(p, materia, [t1, alheia])
    assert r.status_code == 403 and "Turma sem o professor" in r.json()["detail"]
    assert len(client.get("/atividades", headers=p).json()) == antes  # nem a t1 foi criada
    assert _lote(token("aluno@domina.com"), materia, [t1]).status_code == 403
    assert _lote(p, materia, []).status_code == 422
    assert _lote(g, materia, [t1, alheia]).status_code == 201  # gestor: qualquer turma da escola


def test_editar_titulo_prazo_e_gabarito_enquanto_ninguem_enviou():
    g, p, t1, t2, materia = _setup()
    a = _lote(p, materia, [t1]).json()[0]
    r = client.put(f"/atividades/{a['id']}", headers=p, json={
        "titulo": "Novo título", "prazo": "2030-06-01", "valor_total": 500,
        "questoes": [{"enunciado": "Q um", "resposta_correta": "1"}, {"enunciado": "Q dois", "resposta_correta": "2"}]})
    assert r.status_code == 200, r.text
    e = r.json()
    assert e["titulo"] == "Novo título" and e["prazo"] == "2030-06-01" and e["valor_total"] == 500
    assert [q["enunciado"] for q in e["questoes"]] == ["Q um", "Q dois"]
    # lista menor tira a ultima; prazo null limpa
    e = client.put(f"/atividades/{a['id']}", headers=p, json={"prazo": None, "questoes": [{"enunciado": "So uma", "resposta_correta": "9"}]}).json()
    assert e["prazo"] is None and len(e["questoes"]) == 1


def test_depois_do_primeiro_envio_so_titulo_e_prazo_mudam():
    g, p, t1, t2, materia = _setup()
    a = _lote(p, materia, [t1]).json()[0]
    aluno = token("aluno@domina.com")
    assert client.post("/submissoes/texto", headers=aluno, json={"atividade_id": a["id"], "texto": "Questão 1: 5"}).status_code == 201
    assert client.put(f"/atividades/{a['id']}", headers=p, json={"titulo": "Renomeada"}).json()["titulo"] == "Renomeada"
    r = client.put(f"/atividades/{a['id']}", headers=p, json={"questoes": [{"enunciado": "x", "resposta_correta": "y"}]})
    assert r.status_code == 409 and "nova atividade" in r.json()["detail"]
    assert client.put(f"/atividades/{a['id']}", headers=p, json={"valor_total": 10}).status_code == 409


def test_excluir_apaga_se_vazia_e_arquiva_se_tem_envio():
    g, p, t1, t2, materia = _setup()
    vazia, usada = _lote(p, materia, [t1]).json()[0], _lote(p, materia, [t1]).json()[0]
    aluno = token("aluno@domina.com")
    client.post("/submissoes/texto", headers=aluno, json={"atividade_id": usada["id"], "texto": "Questão 1: 5"})
    assert client.delete(f"/atividades/{vazia['id']}", headers=p).json() == {"acao": "excluida"}
    assert client.delete(f"/atividades/{usada['id']}", headers=p).json() == {"acao": "arquivada"}
    ids = {x["id"] for x in client.get("/atividades", headers=aluno).json()}
    assert vazia["id"] not in ids and usada["id"] not in ids  # some para o aluno
    # a nota/historico fica: a submissao continua la, mas nao entra mais envio novo
    assert any(s["atividade_id"] == usada["id"] for s in client.get("/submissoes/minhas", headers=aluno).json())
    assert client.post("/submissoes/texto", headers=aluno, json={"atividade_id": usada["id"], "texto": "outra"}).status_code == 404
    assert client.delete(f"/atividades/{vazia['id']}", headers=p).status_code == 404  # ja era


def test_so_professor_da_turma_ou_gestor_editam_ou_excluem():
    g, p, t1, t2, materia = _setup()
    a = _lote(p, materia, [t1]).json()[0]
    for h in (token("aluno@domina.com"), token("gestor2@domina.com")):  # aluno: 403; gestor de outra escola: 404
        assert client.put(f"/atividades/{a['id']}", headers=h, json={"titulo": "x"}).status_code in (403, 404)
        assert client.delete(f"/atividades/{a['id']}", headers=h).status_code in (403, 404)
    assert client.delete(f"/atividades/{a['id']}", headers=g).status_code == 200  # gestor da escola


def test_gabarito_so_vai_para_o_professor_e_tem_envios_aparece():
    g, p, t1, t2, materia = _setup()
    a = _lote(p, materia, [t1]).json()[0]
    assert a["tem_envios"] is False and a["questoes"][0]["resposta_correta"] == "5"
    aluno = token("aluno@domina.com")
    client.post("/submissoes/texto", headers=aluno, json={"atividade_id": a["id"], "texto": "Questão 1: 5"})
    do_aluno = next(x for x in client.get("/atividades", headers=aluno).json() if x["id"] == a["id"])
    assert do_aluno["questoes"][0]["resposta_correta"] is None
    assert next(x for x in client.get("/atividades", headers=p).json() if x["id"] == a["id"])["tem_envios"] is True
