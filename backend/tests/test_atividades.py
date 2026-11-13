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


def test_fila_traz_turma_e_filtra_por_turma():
    g, p, t1, t2, materia = _setup()
    _lote(p, materia, [t1, t2])
    todas = client.get("/submissoes", headers=p)
    assert todas.status_code == 200
    for s in todas.json():
        assert s["turma_nome"] and s["turma_id"]
    um = client.get(f"/submissoes?turma_id={t2}", headers=p)
    assert um.status_code == 200
    assert all(s["turma_id"] == t2 for s in um.json())
    assert client.get("/submissoes?turma_id=00000000-0000-0000-0000-000000000000", headers=p).status_code == 404


def _objetiva(p, materia, turmas):
    qs = [{"enunciado": "2+2?", "alternativas": ["3", "4", "5", "6", "7"], "resposta_correta": "b"},
          {"enunciado": "Capital do Brasil?", "alternativas": ["Rio", "SP", "Brasília", "BH"], "resposta_correta": "C"}]
    return client.post("/atividades/lote", headers=p, json={
        "materia_id": materia, "turma_ids": turmas, "titulo": "Prova objetiva", "tipo": "PROVA_OBJETIVA",
        "valor_total": 10, "questoes": qs})


def test_objetiva_corrige_na_hora_e_nao_vaza_gabarito():
    g, p, t1, t2, materia = _setup()
    r = _objetiva(p, materia, [t1])
    assert r.status_code == 201, r.text
    ativ = r.json()[0]
    assert [q["alternativas"][1] for q in ativ["questoes"]][0] == "4"
    assert ativ["questoes"][0]["resposta_correta"] == "B"  # normalizado para maiuscula

    aluno = ativ["alunos"][0]["id"]
    env = client.post("/submissoes/objetiva", headers=p, json={
        "atividade_id": ativ["id"], "aluno_id": aluno, "respostas": {"Q1": "b", "Q2": "A"}})
    assert env.status_code == 201, env.text
    cor = client.get(f"/submissoes/{env.json()['id']}/correcao", headers=p).json()
    assert cor["status"] == "APROVADA" and float(cor["nota_professor"]) == 5.0  # 1 de 2 questoes x 5
    # segunda entrega do mesmo aluno: bloqueada
    assert client.post("/submissoes/objetiva", headers=p, json={
        "atividade_id": ativ["id"], "aluno_id": aluno, "respostas": {}}).status_code == 409

    # o aluno ve as alternativas, mas nao o gabarito
    # o aluno ve as alternativas, mas nunca o gabarito
    ta = token("aluno@domina.com")
    vistas = [a for a in client.get("/atividades", headers=ta).json() if a["id"] == ativ["id"]]
    if vistas:  # so se o aluno do seed estiver na 3º Ano A
        assert vistas[0]["questoes"][0]["alternativas"] and vistas[0]["questoes"][0]["resposta_correta"] is None


def test_objetiva_valida_gabarito_e_alternativa_marcada():
    g, p, t1, t2, materia = _setup()
    ruim = {"enunciado": "x", "alternativas": ["a", "b"], "resposta_correta": "D"}
    r = client.post("/atividades/lote", headers=p, json={"materia_id": materia, "turma_ids": [t1],
                    "titulo": "t", "tipo": "EXERCICIO", "questoes": [ruim]})
    assert r.status_code == 422
    ativ = _objetiva(p, materia, [t1]).json()[0]
    aluno = ativ["alunos"][-1]["id"]
    assert client.post("/submissoes/objetiva", headers=p, json={
        "atividade_id": ativ["id"], "aluno_id": aluno, "respostas": {"Q1": "Z"}}).status_code == 422
    # atividade discursiva nao aceita envio objetivo
    disc = _lote(p, materia, [t1]).json()[0]
    assert client.post("/submissoes/objetiva", headers=p, json={
        "atividade_id": disc["id"], "aluno_id": disc["alunos"][0]["id"], "respostas": {}}).status_code == 422


def test_revisao_do_professor_mostra_so_o_que_propos_ou_corrigiu():
    from app.database import SessionLocal
    from app.models.usuario import Correcao
    g, p, t1, t2, materia = _setup()
    if "prof2" not in _cache:
        r = client.post("/usuarios", headers=g, json={"nome": "Prof Dois", "email": "prof.dois@x.com", "senha": "123456",
                        "perfil": "PROFESSOR", "turma_id": t1})
        _cache["prof2"], _cache["prof2_id"] = True, r.json()["id"]
    p2 = token("prof.dois@x.com", "123456")
    ativ = _lote(p, materia, [t1]).json()[0]   # proposta pelo professor 1
    aluno = ativ["alunos"][0]["id"]
    sub = client.post("/submissoes/texto", headers=p, json={"atividade_id": ativ["id"], "aluno_id": aluno, "texto": "x = 5"}).json()

    ids = lambda h: {s["id"] for s in client.get("/submissoes", headers=h).json()}  # noqa: E731
    assert sub["id"] in ids(p)                  # quem propos ve
    assert sub["id"] not in ids(p2)             # o outro professor da mesma turma nao
    assert sub["id"] in ids(g)                  # gestor ve tudo
    assert [a for a in client.get("/atividades", headers=p2).json() if a["id"] == ativ["id"]][0]["na_minha_revisao"] is False
    assert [a for a in client.get("/atividades", headers=p).json() if a["id"] == ativ["id"]][0]["na_minha_revisao"] is True

    import uuid
    from app.models.enum import StatusCorrecaoEnum
    with SessionLocal() as db:                  # o professor 2 corrige (aprova) -> passa a ver
        db.add(Correcao(submissao_id=uuid.UUID(sub["id"]), nota_ia=100, nota_professor=100, confianca=1,
                        status=StatusCorrecaoEnum.APROVADA, modelo_usado="m", versao_prompt="v",
                        revisado_por=uuid.UUID(_cache["prof2_id"])))
        db.commit()
    assert sub["id"] in ids(p2)


def test_atividade_sem_autor_nao_aparece_para_professor_so_para_gestor():
    import uuid
    from app.database import SessionLocal
    from app.models.usuario import Atividade
    g, p, t1, t2, materia = _setup()
    ativ = _lote(p, materia, [t1]).json()[0]
    sub = client.post("/submissoes/texto", headers=p, json={"atividade_id": ativ["id"], "aluno_id": ativ["alunos"][0]["id"], "texto": "x"}).json()
    with SessionLocal() as db:  # simula atividade antiga: sem autor
        db.get(Atividade, uuid.UUID(ativ["id"])).criado_por = None
        db.commit()
    ids = lambda h: {s["id"] for s in client.get("/submissoes", headers=h).json()}  # noqa: E731
    assert sub["id"] not in ids(p)          # nem o professor da turma: nao ha "todos da turma"
    assert sub["id"] in ids(g)


def test_materia_de_redacao_nasce_com_as_5_competencias():
    from app.database import SessionLocal
    from app.models.usuario import Tema
    import uuid
    g, *_ = _setup()
    m = client.post("/materias", headers=g, json={"nome": "Redação nova", "tipo": "REDACAO_ENEM"}).json()
    with SessionLocal() as db:
        codigos = sorted(c for (c,) in db.query(Tema.habilidade_codigo).filter_by(materia_id=uuid.UUID(m["id"]), atividade_id=None))
    assert codigos == ["C1", "C2", "C3", "C4", "C5"]


def test_simbolos_unicode_de_quimica_e_matematica_voltam_intactos():
    g, p, t1, t2, materia = _setup()
    enun, gab = "Balanceie: H₂SO₄ + NaOH ⇌ Na₂SO₄ + H₂O; calcule √(x²) ≤ π", "2H⁺ + SO₄²⁻ → Δ ½ ∫ α"
    r = client.post("/atividades/lote", headers=p, json={"materia_id": materia, "turma_ids": [t1], "titulo": "Química ⚗",
                    "tipo": "EXERCICIO", "questoes": [{"enunciado": enun, "resposta_correta": gab}]})
    assert r.status_code == 201, r.text
    q = r.json()[0]["questoes"][0]
    assert (q["enunciado"], q["resposta_correta"]) == (enun, gab)
