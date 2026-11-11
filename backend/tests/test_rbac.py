"""Administrador x Gestor: o isolamento por escola e garantido no backend (RBAC), nao so na tela.

    cd backend && python -m pytest tests/test_rbac.py
"""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
os.environ.setdefault("ANTHROPIC_API_KEY", "falsa")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.usuario import Escola  # noqa: E402

seed.run_seed()
client = TestClient(app)


def token(email, senha=seed.SENHA):
    r = client.post("/auth/login", json={"email": email, "senha": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def escola_id(nome):
    with SessionLocal() as db:
        return str(db.query(Escola).filter_by(nome=nome).first().id)


A, B = "COLEGIO PREPARA ENEM", "COLEGIO VESTIBULAR NORTE"


def novo(h, perfil, email, **extra):
    h = {**h, "X-Confirmar-Senha": seed.SENHA}  # reautenticacao: so criar GESTOR exige, o resto ignora
    return client.post("/usuarios", headers=h, json={"nome": "Fulano", "email": email, "senha": "123456",
                                                      "perfil": perfil, **extra})


def test_admin_cria_escola_gestor_e_professor():
    adm = token("admin@domina.com")
    r = client.post("/escolas", headers=adm, json={"nome": "Escola Nova", "cnpj": "11222333000144"})
    assert r.status_code == 201, r.text
    nova = r.json()["id"]
    assert novo(adm, "GESTOR", "g.nova@x.com", escola_id=nova).status_code == 201
    assert novo(adm, "PROFESSOR", "p.nova@x.com", escola_id=nova).status_code == 201
    assert novo(adm, "PROFESSOR", "sem.escola@x.com").status_code == 422  # admin precisa dizer a escola
    # o gestor recem-criado entra e so enxerga a propria escola
    assert client.get("/usuarios", headers=token("g.nova@x.com", "123456")).json()[0]["escola_nome"] == "Escola Nova"


def test_so_admin_gerencia_escolas():
    for email in ("gestor@domina.com", "professor@domina.com", "aluno@domina.com"):
        h = token(email)
        assert client.get("/escolas", headers=h).status_code == 403
        assert client.post("/escolas", headers=h, json={"nome": "X X", "cnpj": "11222333000155"}).status_code == 403
    assert client.get("/painel/plataforma", headers=token("gestor@domina.com")).status_code == 403


def test_gestor_cria_professor_e_aluno_so_na_propria_escola():
    g = token("gestor@domina.com")
    outra = escola_id(B)
    r = novo(g, "PROFESSOR", "prof.a@x.com", escola_id=outra)  # tenta forcar a outra escola
    assert r.status_code == 201 and r.json()["escola_nome"] == A
    assert novo(g, "ALUNO", "aluno.a@x.com").status_code == 201
    assert novo(g, "GESTOR", "gestor.a@x.com").status_code == 403  # gestor nao cria gestor
    assert novo(g, "GESTOR", "g2.a@x.com", escola_id=outra).status_code == 403


def test_professor_cria_aluno_mas_nao_professor():
    p = token("professor@domina.com")
    assert novo(p, "ALUNO", "aluno.do.prof@x.com").status_code == 201
    assert novo(p, "PROFESSOR", "prof.do.prof@x.com").status_code == 403
    assert novo(token("aluno@domina.com"), "ALUNO", "aluno.cria@x.com").status_code == 403
    # e matricula o aluno que criou numa turma dele
    turmas = client.get("/turmas/minhas", headers=p).json()
    aluno = next(u for u in client.get("/usuarios", headers=p).json() if u["email"] == "aluno.do.prof@x.com")
    r = client.post(f"/turmas/{turmas[0]['id']}/matricular", headers=p, json={"usuario_id": aluno["id"], "papel": "ALUNO"})
    assert r.status_code == 201, r.text


def test_gestor_nao_ve_outra_escola():
    g2 = token("gestor2@domina.com")
    a = escola_id(A)
    # custo e painel: pedir a escola de outro volta 404 (nem revela que existe)
    assert client.get("/painel/escola", params={"escola_id": a}, headers=g2).status_code == 404
    assert client.get("/custo-uso", params={"escola_id": a}, headers=g2).status_code == 404
    # sem parametro, vem a propria
    assert client.get("/painel/escola", headers=g2).json()["escola_nome"] == B
    assert client.get("/usuarios", params={"escola_id": a}, headers=g2).status_code == 404
    assert {u["escola_nome"] for u in client.get("/usuarios", headers=g2).json()} == {B}


def test_admin_ve_cada_escola_e_o_total():
    adm = token("admin@domina.com")
    a, b = escola_id(A), escola_id(B)
    ra = client.get("/painel/escola", params={"escola_id": a}, headers=adm).json()
    rb = client.get("/painel/escola", params={"escola_id": b}, headers=adm).json()
    assert ra["escola_nome"] == A and rb["escola_nome"] == B
    assert ra["alunos_ativos"] > 0 and rb["alunos_ativos"] == 0
    assert ra["receita"] == 1000 + 8 * ra["alunos_ativos"] and rb["receita"] == 1000
    assert client.get("/painel/escola", headers=adm).status_code == 422  # admin precisa dizer qual
    total = client.get("/painel/plataforma", headers=adm).json()
    assert total["totais"]["alunos_ativos"] == sum(e["alunos_ativos"] for e in total["escolas"])
    assert client.get("/custo-uso", params={"escola_id": b}, headers=adm).status_code == 200


def test_escola_desativada_nao_entra_mais():
    adm = token("admin@domina.com")
    r = client.post("/escolas", headers=adm, json={"nome": "Escola Temp", "cnpj": "55666777000188"})
    nova = r.json()["id"]
    novo(adm, "PROFESSOR", "p.temp@x.com", escola_id=nova)
    h = token("p.temp@x.com", "123456")
    assert client.put(f"/escolas/{nova}", headers={**adm, "X-Confirmar-Senha": seed.SENHA}, json={"ativa": False}).json()["ativa"] is False
    assert client.get("/usuarios/me", headers=h).status_code == 403  # token antigo tambem cai
    assert client.post("/auth/login", json={"email": "p.temp@x.com", "senha": "123456"}).status_code == 403


def _turma(h, nome):
    return client.post("/turmas", headers=h, json={"nome": nome, "ano": 2026}).json()["id"]


def test_conta_ja_nasce_na_turma_escolhida():
    g, p = token("gestor@domina.com"), token("professor@domina.com")
    turma = _turma(g, "Turma Nova")
    # gestor: professor e aluno direto na turma
    for perfil, email in (("PROFESSOR", "prof.turma@x.com"), ("ALUNO", "aluno.turma@x.com")):
        assert novo(g, perfil, email, turma_id=turma).status_code == 201
    membros = {m["email"]: m["papel"] for m in client.get(f"/turmas/{turma}/membros", headers=g).json()}
    assert membros == {"prof.turma@x.com": "PROFESSOR", "aluno.turma@x.com": "ALUNO"}
    # professor so coloca aluno em turma dele (nao nessa, onde nao da aula)
    assert novo(p, "ALUNO", "aluno.fora@x.com", turma_id=turma).status_code == 403
    propria = client.get("/turmas/minhas", headers=p).json()[0]["id"]
    assert novo(p, "ALUNO", "aluno.dele@x.com", turma_id=propria).status_code == 201
    # turma de outra escola: 404 e a conta NAO e criada
    t_outra = _turma(token("gestor2@domina.com"), "Turma Norte")
    assert novo(g, "ALUNO", "aluno.cruzado@x.com", turma_id=t_outra).status_code == 404
    assert novo(g, "ALUNO", "aluno.cruzado@x.com").status_code == 201  # email segue livre


def test_admin_lista_turmas_da_escola_e_cria_conta_nela():
    adm = token("admin@domina.com")
    b = escola_id(B)
    turma = _turma(token("gestor2@domina.com"), "Turma Admin")
    assert any(t["id"] == turma for t in client.get("/turmas/minhas", params={"escola_id": b}, headers=adm).json())
    assert novo(adm, "ALUNO", "aluno.adm@x.com", escola_id=b, turma_id=turma).status_code == 201
    assert novo(adm, "GESTOR", "gestor.turma@x.com", escola_id=b, turma_id=turma).status_code == 422
