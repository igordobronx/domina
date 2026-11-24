"""Assuntos dentro da materia: dono, escola, busca da IA por assunto, material/instrucao/atividade/exercicio.

    cd backend && python -m pytest tests/test_assuntos.py
"""
import uuid

from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)
from vinculo_teste import vincular  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.ia import memoria  # noqa: E402
from app.models.usuario import IaTrecho, Usuario  # noqa: E402

_c = {}


def _setup():
    g = token("gestor@domina.com")
    if not _c:
        turma = client.post("/turmas", headers=g, json={"nome": "Turma Assunto", "ano": 2026}).json()["id"]
        for nome, email in (("Prof A", "prof.a.assunto@x.com"), ("Prof B", "prof.b.assunto@x.com")):
            client.post("/usuarios", headers=g, json={"nome": nome, "email": email, "senha": "123456",
                                                     "perfil": "PROFESSOR", "turma_id": turma})
        materia = client.post("/materias", headers=g, json={"nome": "Mat Assunto", "area": "EXATAS"}).json()["id"]
        vincular("prof.a.assunto@x.com", turma, materia)
        vincular("prof.b.assunto@x.com", turma, materia)
        _c.update(turma=turma, materia=materia)
    return (token("prof.a.assunto@x.com", "123456"), token("prof.b.assunto@x.com", "123456"), g, _c)


def _criar(h, materia, nome):
    return client.post(f"/materias/{materia}/assuntos", headers=h, json={"nome": nome})


def _nomes(h, materia, **q):
    return {a["nome"] for a in client.get(f"/materias/{materia}/assuntos", headers=h, params=q).json()}


def test_dono_escola_e_tirar_de_uso():
    a, b, g, c = _setup()
    m = c["materia"]
    r = _criar(a, m, "Função afim")
    assert r.status_code == 201 and r.json()["da_escola"] is False
    assert _criar(a, m, "função AFIM").status_code == 409  # mesmo nome, so muda a caixa
    escola = _criar(g, m, "Revisão geral")
    assert escola.status_code == 201 and escola.json()["da_escola"] is True

    # privado: o professor B nao ve o do A; os da escola todos veem
    assert _nomes(a, m) == {"Função afim", "Revisão geral"}
    assert _nomes(b, m) == {"Revisão geral"}
    assert _nomes(g, m) == {"Função afim", "Revisão geral"}

    # o professor nao muda assunto da escola nem o de outro; o gestor muda o da escola
    assert client.patch(f"/assuntos/{escola.json()['id']}", headers=a, json={"nome": "x"}).status_code == 403
    assert client.patch(f"/assuntos/{r.json()['id']}", headers=b, json={"nome": "x"}).status_code == 404
    assert client.patch(f"/assuntos/{escola.json()['id']}", headers=g, json={"nome": "Revisão"}).status_code == 200

    # tirar de uso some da lista (volta com incluir_inativos) e nao pode mais ser usado
    assert client.patch(f"/assuntos/{r.json()['id']}", headers=a, json={"ativo": False}).status_code == 200
    assert "Função afim" not in _nomes(a, m)
    assert "Função afim" in _nomes(a, m, incluir_inativos=True)
    doc = client.post(f"/materias/{m}/documentos", headers=a, data={"tipo": "OUTRO", "assunto_id": r.json()["id"]},
                      files={"file": ("a.txt", b"conteudo", "text/plain")})
    assert doc.status_code == 422


def test_material_instrucao_atividade_e_exercicio_com_assunto():
    a, b, g, c = _setup()
    m = c["materia"]
    ass = _criar(a, m, "Logaritmo").json()["id"]
    alheio = _criar(b, m, "Geometria").json()["id"]

    # material: fica no assunto; assunto de outro professor = 404
    texto = b"Logaritmo e o expoente. " * 20
    ok = client.post(f"/materias/{m}/documentos", headers=a, data={"tipo": "APOSTILA", "assunto_id": ass},
                     files={"file": ("log.txt", texto, "text/plain")})
    assert ok.status_code == 201 and ok.json()["assunto_id"] == ass
    assert client.post(f"/materias/{m}/documentos", headers=a, data={"tipo": "APOSTILA", "assunto_id": alheio},
                       files={"file": ("x.txt", texto, "text/plain")}).status_code == 404
    lista = client.get(f"/materias/{m}/assuntos", headers=a).json()
    assert next(x for x in lista if x["id"] == ass)["materiais"] >= 1

    # instrucao: vale so no pedido do assunto
    assert client.post(f"/materias/{m}/instrucoes", headers=a,
                       json={"texto": "Sempre use log na base 10.", "assunto_id": ass}).status_code == 201
    assert client.post(f"/materias/{m}/instrucoes", headers=a,
                       json={"texto": "Instrução geral da matéria."}).status_code == 201
    with SessionLocal() as db:
        uid = db.query(Usuario).filter_by(email="prof.a.assunto@x.com").one().id
        so_geral = [t.texto for t in memoria.instrucoes_de(db, uuid.UUID(m), uid)]
        com_assunto = [t.texto for t in memoria.instrucoes_de(db, uuid.UUID(m), uid, uuid.UUID(ass))]
        assert so_geral == ["Instrução geral da matéria."]
        assert set(com_assunto) == {"Instrução geral da matéria.", "Sempre use log na base 10."}

    # atividade e exercicio guardam o assunto; assunto alheio e recusado
    corpo = {"materia_id": m, "titulo": "Prova log", "tipo": "PROVA_OBJETIVA", "turma_id": c["turma"],
             "questoes": [{"enunciado": "log10(100)?", "resposta_correta": "2"}]}
    r = client.post("/atividades", headers=a, json={**corpo, "assunto_id": ass})
    assert r.status_code == 201, r.text
    assert client.post("/atividades", headers=a, json={**corpo, "assunto_id": alheio}).status_code == 404
    from app.models.usuario import Atividade
    with SessionLocal() as db:
        assert str(db.get(Atividade, uuid.UUID(r.json()["id"])).assunto_id) == ass

    ex = {"titulo": "Log", "assunto": "Logaritmo", "materia_id": m, "turma_id": c["turma"], "tipo": "OBJETIVO",
          "enunciado": "log10(10)?", "alternativas": ["0", "1"], "resposta_correta": 1}
    assert client.post("/exercicios", headers=a, json={**ex, "assunto_id": ass}).status_code == 201
    assert client.post("/exercicios", headers=a, json={**ex, "assunto_id": alheio}).status_code == 404


def test_busca_prefere_o_assunto_e_ignora_o_de_outros():
    a, b, g, c = _setup()
    m = uuid.UUID(c["materia"])
    with SessionLocal() as db:
        uid = db.query(Usuario).filter_by(email="prof.a.assunto@x.com").one().id
        x = uuid.UUID(_criar(a, c["materia"], "Assunto X").json()["id"])
        y = uuid.UUID(_criar(a, c["materia"], "Assunto Y").json()["id"])
        for ass, texto in ((x, "potencia base expoente em X"), (y, "potencia base expoente em Y"),
                           (None, "potencia base expoente geral")):
            db.add(IaTrecho(materia_id=m, professor_id=uid, origem=memoria.MATERIAL, assunto_id=ass,
                            titulo="t", texto=texto))
        db.commit()
        com_x = {t.texto for t in memoria.buscar(db, m, "potencia base expoente", memoria.MATERIAL, 10, uid, x)}
        assert "potencia base expoente em X" in com_x and "potencia base expoente geral" in com_x
        assert "potencia base expoente em Y" not in com_x          # outro assunto nao entra
        primeiro = memoria.buscar(db, m, "potencia base expoente", memoria.MATERIAL, 1, uid, x)[0]
        assert primeiro.assunto_id == x                              # o do assunto vem antes do Geral
        sem = {t.texto for t in memoria.buscar(db, m, "potencia base expoente", memoria.MATERIAL, 10, uid)}
        assert "potencia base expoente em Y" in sem                  # sem assunto: a materia toda, como antes
