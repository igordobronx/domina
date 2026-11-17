"""Plano de estudo: POST /estudos/meu/gerar gera exercicios (GET /estudos/meu so le os salvos) a partir do dominio real do aluno.

    cd backend && python -m pytest tests/test_estudos.py
Mesma base de tests/test_fluxo_envio.py (sqlite temporario, sem chamar o Google de verdade).
"""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
os.environ.setdefault("ANTHROPIC_API_KEY", "falsa")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")

import json  # noqa: E402
import re  # noqa: E402
from types import SimpleNamespace  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
import app.estudos as estudos_mod  # noqa: E402
from app.main import app  # noqa: E402

seed.run_seed()
client = TestClient(app)


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _claude_falso():
    # devolve um exercicio por competencia pedida no prompt, na mesma ordem (ja vem
    # ordenada da pior para a melhor, pelo router) -- assim o teste confere a ordem real.
    def gerar_json(prompt, schema, temperature=0, model=None):
        codigos = re.findall(r"^- (C\d)", prompt, re.MULTILINE)
        payload = {"exercicios": [
            {"habilidade_codigo": codigo, "titulo": "t", "enunciado": "e",
             "opcoes": ["a", "b", "c", "d"], "resposta_correta": 0, "explicacao": "x"}
            for codigo in codigos
        ]}
        return schema.model_validate(payload), "modelo-falso"
    return gerar_json


def test_professor_nao_usa_a_rota():
    assert client.get("/estudos/meu", headers=token("professor@domina.com")).status_code == 403


def test_sem_correcao_aprovada_responde_409():
    from app.auth.security import hash_password
    from app.database import SessionLocal
    from app.models.enum import PerfilEnum
    from app.models.usuario import Escola, Usuario

    with SessionLocal() as db:
        escola = db.query(Escola).first()
        db.add(Usuario(escola_id=escola.id, nome="aluno sem correcao", email="semcorrecao@domina.com",
                       senha_hash=hash_password(seed.SENHA), perfil=PerfilEnum.ALUNO))
        db.commit()
    r = client.get("/estudos/meu", headers=token("semcorrecao@domina.com"))
    assert r.status_code == 409


def _limpar_pratica(email):
    """Apaga exercicios/respostas do aluno (outros testes do mesmo banco, como o do agente, tambem geram reforco)."""
    from app.database import SessionLocal
    from app.models.usuario import Exercicio, ExercicioResposta, Usuario
    with SessionLocal() as db:
        aid = db.query(Usuario).filter_by(email=email).one().id
        ids = [i for (i,) in db.query(Exercicio.id).filter_by(aluno_id=aid)]
        db.query(ExercicioResposta).filter(ExercicioResposta.exercicio_id.in_(ids)).delete(synchronize_session=False)
        db.query(Exercicio).filter(Exercicio.id.in_(ids)).delete(synchronize_session=False)
        db.commit()


def _com_claude_falso():
    chamadas = []

    def gerar_contado(prompt, schema, temperature=0, model=None):
        chamadas.append(model)
        return _claude_falso()(prompt, schema)

    original, estudos_mod.gerar_json = estudos_mod.gerar_json, gerar_contado
    return chamadas, original


def test_gera_salva_e_nao_regera_enquanto_ha_pendentes_sem_vazar_gabarito():
    _limpar_pratica("aluno@domina.com")
    chamadas, original = _com_claude_falso()
    try:
        aluno = token("aluno@domina.com")
        assert client.get("/estudos/meu", headers=aluno).json() == []  # abrir a tela nao chama a IA
        assert chamadas == []
        r1 = client.post("/estudos/meu/gerar", headers=aluno)
        assert r1.status_code == 200, r1.text
        geradas = len(chamadas)  # 1 (redacao) + 1 se o aluno tiver erros de exatas vindos de outros testes
        todos = r1.json()
        exercicios = [e for e in todos if e["habilidade_codigo"]]  # so os de redacao (C1-C5)
        assert len(exercicios) == 3
        assert exercicios[0]["habilidade_codigo"] == "C4"  # ponto fraco de proposito do seed (ver seed.py)
        assert all("resposta_correta" not in e and "explicacao" not in e for e in todos)  # sem gabarito
        # abrir de novo ou pedir de novo com exercicio por fazer: os MESMOS, sem chamar o Claude
        assert client.get("/estudos/meu", headers=aluno).json() == todos
        assert client.post("/estudos/meu/gerar", headers=aluno).json() == todos
        assert len(chamadas) == geradas and set(chamadas) == {estudos_mod.settings.ANTHROPIC_MODEL_HAIKU}
    finally:
        estudos_mod.gerar_json = original


def test_responder_o_servidor_confere_salva_e_nao_mexe_no_dominio():
    _limpar_pratica("aluno@domina.com")
    chamadas, original = _com_claude_falso()
    try:
        aluno, outro = token("aluno@domina.com"), token("aluno2@domina.com")
        exercicios = client.post("/estudos/meu/gerar", headers=aluno).json()
        dominio_antes = client.get("/dominio/meu", headers=aluno).json()
        ex = exercicios[0]
        url = f"/estudos/exercicios/{ex['id']}/responder"
        assert client.post(url, headers=outro, json={"opcao": 0}).status_code == 404   # de outro aluno
        assert client.post(url, headers=aluno, json={"opcao": 9}).status_code == 422   # alternativa fora do intervalo
        r = client.post(url, headers=aluno, json={"opcao": 0})                         # a certa e a 0 no falso
        assert r.status_code == 200 and r.json() == {"correta": True, "resposta_correta": 0, "explicacao": "x"}
        assert client.post(url, headers=aluno, json={"opcao": 1}).status_code == 409   # so uma vez
        assert client.post(f"/estudos/exercicios/{exercicios[1]['id']}/responder", headers=aluno, json={"opcao": 2}).json()["correta"] is False
        # os 3 continuam na tela: o por fazer primeiro; os feitos trazem a resposta e o gabarito
        tela = client.get("/estudos/meu", headers=aluno).json()
        assert tela[0]["id"] == exercicios[2]["id"] and "resposta_correta" not in tela[0]
        feitos = {e["id"]: e for e in tela[1:]}
        assert set(feitos) == {exercicios[0]["id"], exercicios[1]["id"]}
        assert feitos[ex["id"]]["respondida"] == 0 and feitos[ex["id"]]["correta"] is True
        assert feitos[exercicios[1]["id"]]["respondida"] == 2 and feitos[exercicios[1]["id"]]["correta"] is False
        # pratica salva por competencia, separada do dominio (que nao mudou)
        pratica = {p["habilidade_codigo"]: p for p in client.get("/estudos/minha-pratica", headers=aluno).json()}
        assert pratica[ex["habilidade_codigo"]] == {"habilidade_codigo": ex["habilidade_codigo"], "respondidos": 1, "acertos": 1}
        assert client.get("/dominio/meu", headers=aluno).json() == dominio_antes
        # professor da turma ve a pratica do aluno; aluno nao ve a do colega
        from app.database import SessionLocal
        from app.models.usuario import Usuario
        with SessionLocal() as db:
            aid = str(db.query(Usuario).filter_by(email="aluno@domina.com").one().id)
        assert client.get(f"/alunos/{aid}/pratica", headers=token("professor@domina.com")).status_code == 200
        assert client.get(f"/alunos/{aid}/pratica", headers=outro).status_code == 403
    finally:
        estudos_mod.gerar_json = original


def test_terminou_os_pendentes_gera_novos_ate_o_limite_diario():
    _limpar_pratica("aluno@domina.com")
    import app.routers.estudos as r_est
    chamadas, original = _com_claude_falso()
    limite = r_est.LIMITE_DIARIO
    try:
        aluno = token("aluno@domina.com")
        primeiros = client.post("/estudos/meu/gerar", headers=aluno).json()  # gera o 1o plano e responde tudo
        for e in primeiros:
            client.post(f"/estudos/exercicios/{e['id']}/responder", headers=aluno, json={"opcao": 0})
        geradas = len(chamadas)
        # voltar a tela depois de responder tudo: os mesmos exercicios, sem IA
        assert {e["id"] for e in client.get("/estudos/meu", headers=aluno).json()} == {e["id"] for e in primeiros}
        assert len(chamadas) == geradas
        r_est.LIMITE_DIARIO = 0
        assert client.post("/estudos/meu/gerar", headers=aluno).status_code == 429  # acabou o plano e o limite diario ja foi
        r_est.LIMITE_DIARIO = 99
        novos = [e for e in client.post("/estudos/meu/gerar", headers=aluno).json() if "respondida" not in e]
        assert len(novos) >= 3 and len(chamadas) > geradas                    # so o botao gera um plano novo
    finally:
        r_est.LIMITE_DIARIO = limite
        estudos_mod.gerar_json = original


def test_meta_de_pratica_conclui_ao_responder():
    _limpar_pratica("aluno@domina.com")
    chamadas, original = _com_claude_falso()
    try:
        aluno, prof = token("aluno@domina.com"), token("professor@domina.com")
        turma = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
        m = client.post("/metas", headers=prof, json={"titulo": "Praticar", "tipo": "PRATICA_RESPONDIDOS", "alvo": 1,
                                                     "pontos": 20, "turma_id": turma})
        assert m.status_code == 201, m.text
        for e in client.post("/estudos/meu/gerar", headers=aluno).json()[:1]:
            client.post(f"/estudos/exercicios/{e['id']}/responder", headers=aluno, json={"opcao": 0})
        item = [x for x in client.get("/metas/minhas", headers=aluno).json()["metas"] if x["id"] == m.json()["id"]][0]
        assert item["status"] == "CONCLUIDA"
    finally:
        estudos_mod.gerar_json = original


def test_sem_chave_do_claude_responde_503():
    from app.config import settings

    original, settings.ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY, None
    try:
        r = client.post("/estudos/meu/gerar", headers=token("aluno2@domina.com"))
        assert r.status_code == 503
    finally:
        settings.ANTHROPIC_API_KEY = original
