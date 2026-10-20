"""Plano de estudo: GET /estudos/meu gera exercicios a partir do dominio real do aluno.

    cd backend && python -m pytest tests/test_estudos.py
Mesma base de tests/test_fluxo_envio.py (sqlite temporario, sem chamar o Google de verdade).
"""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
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


def _gemini_falso():
    # devolve um exercicio por competencia pedida no prompt, na mesma ordem (ja vem
    # ordenada da pior para a melhor, pelo router) -- assim o teste confere a ordem real.
    def gerar(prompt, config):
        codigos = re.findall(r"^- (C\d)", prompt, re.MULTILINE)
        payload = {"exercicios": [
            {"habilidade_codigo": codigo, "titulo": "t", "enunciado": "e",
             "opcoes": ["a", "b", "c", "d"], "resposta_correta": 0, "explicacao": "x"}
            for codigo in codigos
        ]}
        return SimpleNamespace(text=json.dumps(payload)), "modelo-falso"
    return gerar


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


def test_gera_exercicios_para_as_piores_competencias_e_usa_cache():
    chamadas = []

    def gerar_contado(prompt, config):
        chamadas.append(1)
        return _gemini_falso()(prompt, config)

    original, estudos_mod.gerar = estudos_mod.gerar, gerar_contado
    try:
        r1 = client.get("/estudos/meu", headers=token("aluno@domina.com"))
        assert r1.status_code == 200, r1.text
        exercicios = r1.json()
        assert len(exercicios) == 3
        assert exercicios[0]["habilidade_codigo"] == "C4"  # ponto fraco de proposito do seed (ver seed.py)

        # segunda chamada: mesmo perfil de dominio -> vem do cache, nao chama o Gemini de novo
        r2 = client.get("/estudos/meu", headers=token("aluno@domina.com"))
        assert r2.json() == exercicios
        assert len(chamadas) == 1
    finally:
        estudos_mod.gerar = original


def test_sem_chave_do_gemini_responde_503():
    from app.config import settings

    original, settings.GEMINI_API_KEY = settings.GEMINI_API_KEY, None
    try:
        r = client.get("/estudos/meu", headers=token("aluno2@domina.com"))
        assert r.status_code == 503
    finally:
        settings.GEMINI_API_KEY = original
