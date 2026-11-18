"""O gestor cuida do cadastro: editar, senha, desativar, turmas e materia por turma."""
from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)


def _base():
    g = token("gestor@domina.com")
    t1 = next(t["id"] for t in client.get("/turmas/minhas", headers=g).json() if t["nome"] == "3º Ano A")
    t2 = client.post("/turmas", headers=g, json={"nome": "Turma Pessoas", "ano": 2026}).json()["id"]
    ms = client.get("/materias", headers=g).json()
    return g, t1, t2, ms[0]["id"], ms[1]["id"] if len(ms) > 1 else ms[0]["id"]


def test_professor_em_varias_turmas_com_materia_por_turma():
    g, t1, t2, m1, m2 = _base()
    r = client.post("/usuarios", headers=g, json={
        "nome": "Prof Pessoas", "email": "prof.pessoas@x.com", "senha": "123456", "perfil": "PROFESSOR",
        "turmas": [{"turma_id": t1, "materia_ids": [m1]}, {"turma_id": t2, "materia_ids": [m1, m2]}]})
    assert r.status_code == 201, r.text
    uid = r.json()["id"]
    v = {x["turma_id"]: set(x["materia_ids"]) for x in client.get(f"/usuarios/{uid}/vinculos", headers=g).json()["turmas"]}
    assert v == {t1: {m1}, t2: {m1, m2}}
    assert sorted(r.json()["turmas"]) == sorted(["3º Ano A", "Turma Pessoas"])

    # ele so cria atividade da materia que leciona naquela turma
    p = token("prof.pessoas@x.com", "123456")
    corpo = {"materia_id": m2, "turma_id": t1, "titulo": "x", "tipo": "EXERCICIO", "questoes": [{"enunciado": "q", "resposta_correta": "r"}]}
    if m1 != m2:
        assert client.post("/atividades", headers=p, json=corpo).status_code == 403

    # tira da turma t1 e deixa so uma materia na t2: o vinculo da turma removida some
    r = client.put(f"/usuarios/{uid}/vinculos", headers=g, json={"turmas": [{"turma_id": t2, "materia_ids": [m1]}]})
    assert r.status_code == 200
    assert [(x["turma_id"], x["materia_ids"]) for x in r.json()["turmas"]] == [(t2, [m1])]
    # aluno nao tem materia
    aluno = client.get("/usuarios", headers=g).json()
    aid = next(u["id"] for u in aluno if u["email"] == "aluno@domina.com")
    assert client.put(f"/usuarios/{aid}/vinculos", headers=g, json={"turmas": [{"turma_id": t1, "materia_ids": [m1]}]}).status_code == 422
    # materia/turma de outra escola ou inexistente
    assert client.put(f"/usuarios/{uid}/vinculos", headers=g, json={"turmas": [{"turma_id": "00000000-0000-0000-0000-000000000000"}]}).status_code == 404


def test_aluno_muda_de_turma_e_historico_fica():
    g, t1, t2, *_ = _base()
    aid = next(u["id"] for u in client.get("/usuarios", headers=g).json() if u["email"] == "aluno2@domina.com")
    antes = client.get(f"/usuarios/{aid}/vinculos", headers=g).json()["turmas"]
    ids = [x["turma_id"] for x in antes]
    assert client.put(f"/usuarios/{aid}/vinculos", headers=g, json={"turmas": [{"turma_id": t2}]}).status_code == 200
    assert [x["turma_id"] for x in client.get(f"/usuarios/{aid}/vinculos", headers=g).json()["turmas"]] == [t2]
    client.put(f"/usuarios/{aid}/vinculos", headers=g, json={"turmas": [{"turma_id": i} for i in ids]})  # devolve


def test_editar_senha_e_desativar():
    g, *_ = _base()
    r = client.post("/usuarios", headers=g, json={"nome": "Aluno Edit", "email": "edit.pessoas@x.com", "senha": "123456", "perfil": "ALUNO"})
    uid = r.json()["id"]
    assert client.put(f"/usuarios/{uid}", headers=g, json={"nome": "Aluno Editado", "email": "edit2.pessoas@x.com"}).json()["nome"] == "Aluno Editado"
    assert client.put(f"/usuarios/{uid}", headers=g, json={"nome": "x", "email": "professor@domina.com"}).status_code == 409

    # senha: pede a senha do gestor; a antiga deixa de valer
    assert client.put(f"/usuarios/{uid}/senha", headers=g, json={"senha": "novasenha1"}).status_code == 403
    assert client.put(f"/usuarios/{uid}/senha", headers={**g, "X-Confirmar-Senha": "errada"}, json={"senha": "novasenha1"}).status_code == 403
    assert client.put(f"/usuarios/{uid}/senha", headers={**g, "X-Confirmar-Senha": "senha123"}, json={"senha": "novasenha1"}).status_code == 204
    assert client.post("/auth/login", json={"email": "edit2.pessoas@x.com", "senha": "123456"}).status_code == 401
    aluno = token("edit2.pessoas@x.com", "novasenha1")
    assert client.get("/usuarios/me", headers=aluno).status_code == 200

    # desativar: nao entra mais e o token que ja existia cai; reativar volta
    assert client.put(f"/usuarios/{uid}/ativo", headers=g, json={"ativo": False}).json()["ativo"] is False
    assert client.post("/auth/login", json={"email": "edit2.pessoas@x.com", "senha": "novasenha1"}).status_code == 403
    assert client.get("/usuarios/me", headers=aluno).status_code == 401
    assert client.put(f"/usuarios/{uid}/ativo", headers=g, json={"ativo": True}).status_code == 200
    assert client.get("/usuarios/me", headers=aluno).status_code == 200


def test_permissoes():
    g, *_ = _base()
    gid = next(u["id"] for u in client.get("/usuarios", headers=g).json() if u["email"] == "gestor@domina.com")
    # gestor nao mexe em conta de gestor (nem na propria); so o admin
    assert client.put(f"/usuarios/{gid}", headers=g, json={"nome": "x", "email": "gestor@domina.com"}).status_code == 403
    # professor e aluno nao entram
    for email in ("professor@domina.com", "aluno@domina.com"):
        assert client.put(f"/usuarios/{gid}/ativo", headers=token(email), json={"ativo": False}).status_code == 403
    # gestor de outra escola nao enxerga a pessoa
    aid = next(u["id"] for u in client.get("/usuarios", headers=g).json() if u["email"] == "aluno@domina.com")
    g2 = token("gestor2@domina.com")
    assert client.put(f"/usuarios/{aid}/ativo", headers=g2, json={"ativo": False}).status_code == 404
    assert client.get(f"/usuarios/{aid}/vinculos", headers=g2).status_code == 404
