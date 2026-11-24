"""Notificacoes: eventos (atividade nova, envio, IA corrigiu) e alertas por tempo (prazo, feriado, nivel).

    cd backend && python -m pytest tests/test_avisos.py
"""
from datetime import timedelta

from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)
from vinculo_teste import vincular  # noqa: E402

from app import avisos  # noqa: E402
from app.gamificacao import hoje_local  # noqa: E402

_c = {}


def _setup():
    g = token("gestor@domina.com")
    if not _c:
        turma = client.post("/turmas", headers=g, json={"nome": "Turma Aviso", "ano": 2026}).json()["id"]
        mk = lambda nome, email, perfil: client.post("/usuarios", headers=g, json={  # noqa: E731
            "nome": nome, "email": email, "senha": "123456", "perfil": perfil, "turma_id": turma}).json()["id"]
        mk("Prof Aviso", "prof.aviso@x.com", "PROFESSOR")
        mk("Ana Aviso", "ana.aviso@x.com", "ALUNO")
        mk("Bia Aviso", "bia.aviso@x.com", "ALUNO")
        materia = client.post("/materias", headers=g, json={"nome": "Mat Aviso", "tipo": "MATERIA_OBJETIVA"}).json()["id"]
        vincular("prof.aviso@x.com", turma, materia)
        _c.update(turma=turma, materia=materia)
    return token("prof.aviso@x.com", "123456"), token("ana.aviso@x.com", "123456"), token("bia.aviso@x.com", "123456"), _c


def _prova(p, c, titulo, prazo=None):
    corpo = {"materia_id": c["materia"], "turma_ids": [c["turma"]], "titulo": titulo, "tipo": "PROVA_OBJETIVA",
             "valor_total": 10, "questoes": [{"enunciado": "1+1?", "alternativas": ["1", "2"], "resposta_correta": "B"}]}
    if prazo:
        corpo["prazo"] = str(prazo)
    return client.post("/atividades/lote", headers=p, json=corpo).json()[0]


def _avisos(h):
    avisos._ultima.clear()  # sem esperar o intervalo entre conferencias
    return client.get("/avisos", headers=h).json()


def test_atividade_nova_avisa_os_alunos_da_turma_e_so_eles():
    p, ana, bia, c = _setup()
    _prova(p, c, "Prova Nova Aviso")
    j = _avisos(ana)
    novo = [i for i in j["itens"] if i["tipo"] == "ATIVIDADE_NOVA"]
    assert novo and "Prova Nova Aviso" in novo[0]["texto"] and novo[0]["destino"] == "atividades"
    assert j["nao_lidos"] >= 1
    assert not [i for i in _avisos(p)["itens"] if i["tipo"] == "ATIVIDADE_NOVA"]  # o professor nao recebe


def test_envio_do_aluno_avisa_o_professor_agrupado():
    p, ana, bia, c = _setup()
    ativ = _prova(p, c, "Prova Envio Aviso")
    for h, nome in ((ana, "Ana Aviso"), (bia, "Bia Aviso")):
        aluno_id = next(a["id"] for a in ativ["alunos"] if a["nome"] == nome)
        r = client.post("/submissoes/objetiva", headers=h, json={"atividade_id": ativ["id"], "aluno_id": aluno_id, "respostas": {"Q1": "B"}})
        assert r.status_code == 201, r.text
    envios = [i for i in _avisos(p)["itens"] if i["tipo"] == "ENVIO" and "Prova Envio Aviso" in i["texto"]]
    assert len(envios) == 1 and "2 novos envios" in envios[0]["texto"] and envios[0]["destino"] == "revisoes"


def test_prazo_chegando_avisa_uma_vez_e_so_quem_nao_enviou():
    p, ana, bia, c = _setup()
    _prova(p, c, "Prova Prazo Aviso", prazo=hoje_local() + timedelta(days=1))
    for _ in range(2):  # chamar de novo nao repete
        j = _avisos(ana)
    prazo = [i for i in j["itens"] if i["tipo"] == "PRAZO" and "Prova Prazo Aviso" in i["texto"]]
    assert len(prazo) == 1 and "amanhã" in prazo[0]["texto"]


def test_nivel_primeira_conferencia_nao_avisa_e_marcador_nao_aparece():
    p, ana, bia, c = _setup()
    j = _avisos(bia)
    assert not [i for i in j["itens"] if i["tipo"] in ("NIVEL", "MARCADOR")]


def test_feriado_amanha_aparece_para_todos(monkeypatch):
    p, ana, bia, c = _setup()
    amanha = hoje_local() + timedelta(days=1)
    monkeypatch.setattr(avisos, "feriados", lambda ano: [(amanha, "Dia de Teste")])
    assert [i for i in _avisos(ana)["itens"] if i["tipo"] == "FERIADO" and "Dia de Teste" in i["texto"]]
    assert [i for i in _avisos(p)["itens"] if i["tipo"] == "FERIADO"]


def test_marcar_lidos_zera_o_contador():
    p, ana, bia, c = _setup()
    assert client.post("/avisos/lidos", headers=ana).status_code == 204
    assert _avisos(ana)["nao_lidos"] == 0
