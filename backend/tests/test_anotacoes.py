"""Marcas do professor sobre a foto + avisos ao aluno.

    cd backend && python -m pytest tests/test_anotacoes.py
"""
import uuid

from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)
from vinculo_teste import vincular  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models.enum import StatusCorrecaoEnum  # noqa: E402
from app.models.usuario import Correcao  # noqa: E402

_c = {}


def _setup():
    g = token("gestor@domina.com")
    if not _c:
        turma = client.post("/turmas", headers=g, json={"nome": "Turma Marca", "ano": 2026}).json()["id"]
        mk = lambda nome, email, perfil: client.post("/usuarios", headers=g, json={  # noqa: E731
            "nome": nome, "email": email, "senha": "123456", "perfil": perfil, "turma_id": turma}).json()["id"]
        mk("Prof Marca", "prof.marca@x.com", "PROFESSOR")
        outra = client.post("/turmas", headers=g, json={"nome": "Turma Marca Alheia", "ano": 2026}).json()["id"]
        client.post("/usuarios", headers=g, json={"nome": "Outro Prof", "email": "prof2.marca@x.com", "senha": "123456",
                                                 "perfil": "PROFESSOR", "turma_id": outra})
        aluno = mk("Ana Marca", "ana.marca@x.com", "ALUNO")
        mk("Bia Marca", "bia.marca@x.com", "ALUNO")
        materia = client.post("/materias", headers=g, json={"nome": "Mat Marca", "area": "EXATAS"}).json()["id"]
        vincular("prof.marca@x.com", turma, materia)
        p = token("prof.marca@x.com", "123456")
        ativ = client.post("/atividades/lote", headers=p, json={
            "materia_id": materia, "turma_ids": [turma], "titulo": "Prova Marca", "tipo": "PROVA_OBJETIVA",
            "valor_total": 10, "questoes": [{"enunciado": "1+1?", "alternativas": ["1", "2"], "resposta_correta": "B"}]}).json()[0]
        sub = client.post("/submissoes/objetiva", headers=p, json={
            "atividade_id": ativ["id"], "aluno_id": aluno, "respostas": {"Q1": "B"}}).json()
        _c.update(sub=sub["id"])
    return _c["sub"]


def _status(sub, valor):
    with SessionLocal() as db:
        c = db.query(Correcao).filter_by(submissao_id=uuid.UUID(sub)).one()
        c.status = valor
        db.commit()


MARCA = {"pagina": 0, "x": 0.1, "y": 0.2, "largura": 0.3, "altura": 0.1, "tipo": "erro", "comentario": "Palavra em inglês."}


def test_professor_marca_e_aluno_so_ve_depois_de_aprovada():
    sub = _setup()
    p, aluno = token("prof.marca@x.com", "123456"), token("ana.marca@x.com", "123456")
    r = client.post(f"/submissoes/{sub}/anotacoes", headers=p, json=MARCA)
    assert r.status_code == 201 and r.json()["minha"] is True and r.json()["autor_nome"] == "Prof Marca"

    _status(sub, StatusCorrecaoEnum.PENDENTE)  # ainda nao aprovada: o aluno nao ve a marca do professor
    assert client.get(f"/submissoes/{sub}/anotacoes", headers=aluno).json() == []
    assert len(client.get(f"/submissoes/{sub}/anotacoes", headers=p).json()) == 1
    assert len(client.get(f"/submissoes/{sub}/anotacoes", headers=token("gestor@domina.com")).json()) == 1  # gestor le

    _status(sub, StatusCorrecaoEnum.APROVADA)
    visto = client.get(f"/submissoes/{sub}/anotacoes", headers=aluno).json()
    assert len(visto) == 1 and visto[0]["comentario"] == "Palavra em inglês." and visto[0]["minha"] is False


def test_permissoes_e_validacao():
    sub = _setup()
    p, aluno = token("prof.marca@x.com", "123456"), token("ana.marca@x.com", "123456")
    outro_aluno, outro_prof = token("bia.marca@x.com", "123456"), token("prof2.marca@x.com", "123456")
    assert client.post(f"/submissoes/{sub}/anotacoes", headers=aluno, json=MARCA).status_code == 403   # aluno nao marca
    assert client.post(f"/submissoes/{sub}/anotacoes", headers=token("gestor@domina.com"), json=MARCA).status_code == 403
    assert client.get(f"/submissoes/{sub}/anotacoes", headers=outro_aluno).status_code == 404            # nao e dele
    assert client.get(f"/submissoes/{sub}/anotacoes", headers=outro_prof).status_code == 404             # nem da turma dele
    assert client.post(f"/submissoes/{sub}/anotacoes", headers=p, json={**MARCA, "x": 0.9}).status_code == 422  # fora da folha
    assert client.post(f"/submissoes/{sub}/anotacoes", headers=p, json={**MARCA, "comentario": ""}).status_code == 422

    # so o autor edita e apaga
    ant = client.get(f"/submissoes/{sub}/anotacoes", headers=p).json()[0]["id"]
    assert client.patch(f"/anotacoes/{ant}", headers=outro_prof, json={"comentario": "x"}).status_code == 404
    assert client.patch(f"/anotacoes/{ant}", headers=p, json={"comentario": "Muito bom!", "tipo": "acerto"}).json()["tipo"] == "acerto"
    assert client.delete(f"/anotacoes/{ant}", headers=outro_prof).status_code == 404
    assert client.delete(f"/anotacoes/{ant}", headers=p).status_code == 204
    assert client.get(f"/submissoes/{sub}/anotacoes", headers=p).json() == []


def test_aprovar_avisa_o_aluno():
    sub = _setup()
    p, aluno, outro = token("prof.marca@x.com", "123456"), token("ana.marca@x.com", "123456"), token("bia.marca@x.com", "123456")
    _status(sub, StatusCorrecaoEnum.PENDENTE)
    r = client.put(f"/submissoes/{sub}/aprovar", headers=p, json={"notas": [{"codigo": "Q1", "nota": 10}], "feedback": "Muito bem."})
    assert r.status_code == 200, r.text
    corrigidas = [i for i in client.get("/avisos", headers=aluno).json()["itens"] if i["tipo"] == "CORRIGIDA"]
    assert len(corrigidas) == 1 and "corrigida" in corrigidas[0]["texto"] and corrigidas[0]["submissao_id"] == sub
    assert not [i for i in client.get("/avisos", headers=outro).json()["itens"] if i["tipo"] == "CORRIGIDA"]  # so dele
    assert client.post("/avisos/lidos", headers=aluno).status_code == 204
    assert client.get("/avisos", headers=aluno).json()["nao_lidos"] == 0
