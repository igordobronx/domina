"""O professor so ve estatistica de aluno nas materias que leciona na turma do aluno; gestor ve tudo."""
import uuid

from tests.test_rbac import client, token  # noqa: F401  (reusa o banco/seed do teste de RBAC)
from vinculo_teste import vincular

_c = {}


def _setup():
    from app.auth.security import hash_password
    from app.database import SessionLocal
    from app.models.enum import PerfilEnum, StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum, TipoMateriaEnum, UsuarioTurmaPapelEnum
    from app.models.usuario import Atividade, Correcao, CorrecaoCriterio, Materia, Submissao, Tema, Turma, Usuario, UsuarioTurma
    if _c:
        return _c
    with SessionLocal() as db:
        aluno = db.query(Usuario).filter_by(email="aluno@domina.com").one()
        turma = db.query(Turma).filter_by(nome="3º Ano A").one()
        prof = Usuario(escola_id=turma.escola_id, nome="Prof Quim", email="prof.quim@x.com",
                       senha_hash=hash_password("123456"), perfil=PerfilEnum.PROFESSOR)
        db.add(prof)
        db.flush()
        db.add(UsuarioTurma(usuario_id=prof.id, turma_id=turma.id, papel=UsuarioTurmaPapelEnum.PROFESSOR))
        mat = Materia(escola_id=turma.escola_id, nome="Quimica Escopo", tipo=TipoMateriaEnum.MATERIA_DISCURSIVA)
        db.add(mat)
        db.flush()
        ativ = Atividade(materia_id=mat.id, turma_id=turma.id, titulo="Prova Quim", tipo=TipoAtividadeEnum.PROVA_DISCURSIVA,
                         valor_total=100)
        db.add(ativ)
        db.flush()
        q = Tema(materia_id=mat.id, atividade_id=ativ.id, nome="Q", habilidade_codigo="Q1", resposta_correta="x")
        sub = Submissao(atividade_id=ativ.id, aluno_id=aluno.id, tipo_envio=TipoEnvioEnum.TEXTO, conteudo_bruto="x")
        db.add_all([q, sub])
        db.flush()
        cor = Correcao(submissao_id=sub.id, nota_ia=60, nota_professor=60, confianca=1, status=StatusCorrecaoEnum.APROVADA,
                       modelo_usado="m", versao_prompt="v")
        db.add(cor)
        db.flush()
        db.add(CorrecaoCriterio(correcao_id=cor.id, tema_id=q.id, nota=60, nota_professor=60, justificativa="ok"))
        db.commit()
        _c.update(aluno=str(aluno.id), turma=str(turma.id), materia=str(mat.id))
    vincular("prof.quim@x.com", _c["turma"], _c["materia"])
    return _c


def test_professor_de_quimica_nao_ve_redacao_e_gestor_ve_tudo():
    c = _setup()
    quim, gestor = token("prof.quim@x.com", "123456"), token("gestor@domina.com")
    ev = client.get(f"/alunos/{c['aluno']}/evolucao", headers=quim).json()
    assert [e["materia"] for e in ev] == ["Quimica Escopo"]
    assert client.get(f"/alunos/{c['aluno']}/dominio", headers=quim).json() == []  # C1-C5 e de redacao
    assert client.get(f"/alunos/{c['aluno']}/pratica", headers=quim).json() == []

    dom = client.get(f"/alunos/{c['aluno']}/dominio", headers=gestor).json()
    assert dom and all(d["materia"] for d in dom)  # redacao, com o nome da materia
    assert "Quimica Escopo" in [e["materia"] for e in client.get(f"/alunos/{c['aluno']}/evolucao", headers=gestor).json()]

    # o professor de redacao (Beto) nao ve a quimica
    beto = token("professor@domina.com")
    assert "Quimica Escopo" not in [e["materia"] for e in client.get(f"/alunos/{c['aluno']}/evolucao", headers=beto).json()]
    assert client.get(f"/alunos/{c['aluno']}/dominio", headers=beto).json()  # redacao continua

    # aluno nao usa a rota de professor
    assert client.get(f"/alunos/{c['aluno']}/evolucao", headers=token("aluno@domina.com")).status_code == 403


def test_professor_so_lista_e_cria_com_as_materias_dele():
    c = _setup()
    quim = token("prof.quim@x.com", "123456")
    assert [m["nome"] for m in client.get("/materias", headers=quim).json()] == ["Quimica Escopo"]
    beto = token("professor@domina.com")
    r = client.post("/atividades", headers=beto, json={
        "materia_id": c["materia"], "turma_id": c["turma"], "titulo": "x", "tipo": "EXERCICIO",
        "questoes": [{"enunciado": "q", "resposta_correta": "r"}]})
    assert r.status_code == 403 and "não leciona" in r.json()["detail"]
    # materia que o professor cria passa a ser dele
    nova = client.post("/materias", headers=quim, json={"nome": "Quimica Nova", "tipo": "MATERIA_OBJETIVA"}).json()
    assert nova["id"] in [m["id"] for m in client.get("/materias", headers=quim).json()]
