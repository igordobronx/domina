"""Calendario por escola: todos da escola veem o mesmo dado; o resto e RBAC no backend."""
from tests.test_rbac import A, B, client, escola_id, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)

from app.feriados import feriados

PERIODO = {"de": "2030-03-01", "ate": "2030-03-31"}


def _turma_da_escola():
    # a turma do professor do seed (escola A)
    return client.get("/turmas/minhas", headers=token("professor@domina.com")).json()[0]["id"]


def _evento(h, **extra):
    return client.post("/eventos", headers=h, json={"titulo": "Prova de Química", "tipo": "PROVA",
                                                    "inicio": "2030-03-10", **extra})


def _titulos(h, **q):
    r = client.get("/calendario", headers=h, params={**PERIODO, **q})
    assert r.status_code == 200, r.text
    return [i["titulo"] for i in r.json()]


def test_evento_da_escola_toda_aparece_para_todos_e_nao_vaza_para_outra_escola():
    assert _evento(token("gestor@domina.com"), titulo="Reunião de pais", tipo="REUNIAO").status_code == 201
    for email in ("aluno@domina.com", "professor@domina.com", "gestor@domina.com"):
        assert "Reunião de pais" in _titulos(token(email))
    assert "Reunião de pais" not in _titulos(token("gestor2@domina.com"))


def test_aluno_nao_cria_e_professor_so_para_a_propria_turma():
    assert _evento(token("aluno@domina.com")).status_code == 403
    p = token("professor@domina.com")
    assert _evento(p).status_code == 403  # sem turma = escola toda: so gestor
    assert _evento(p, turma_id=_turma_da_escola()).status_code == 201


def test_professor_nao_apaga_evento_do_gestor_mas_gestor_apaga_o_dele():
    g, p = token("gestor@domina.com"), token("professor@domina.com")
    eid = _evento(g, titulo="Feira").json()["id"].split(":")[1]
    assert client.delete(f"/eventos/{eid}", headers=p).status_code == 403
    assert client.delete(f"/eventos/{eid}", headers=token("gestor2@domina.com")).status_code == 404
    assert client.delete(f"/eventos/{eid}", headers=g).status_code == 204
    assert "Feira" not in _titulos(g)


def test_aluno_nao_ve_evento_de_turma_alheia_e_feriado_vem_pronto():
    g = token("gestor@domina.com")
    outra = client.post("/turmas", headers=g, json={"nome": "Turma Fantasma", "ano": 2030})
    if outra.status_code in (200, 201):
        _evento(g, titulo="So da fantasma", turma_id=outra.json()["id"])
        assert "So da fantasma" not in _titulos(token("aluno@domina.com"))
        assert "So da fantasma" in _titulos(g)
    assert "Sexta-feira Santa" in _titulos(token("aluno@domina.com"), de="2030-04-01", ate="2030-04-30")


def test_admin_precisa_da_escola_e_feriados_calculados():
    adm = token("admin@domina.com")
    assert client.get("/calendario", headers=adm).status_code == 422
    assert client.get("/calendario", headers=adm, params={"escola_id": escola_id(A)}).status_code == 200
    d = dict((n, d) for d, n in feriados(2026))
    assert str(d["Carnaval"]) == "2026-02-17" and str(d["Corpus Christi"]) == "2026-06-04"
