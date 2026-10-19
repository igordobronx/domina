"""Fluxo do aluno: login -> envia foto -> OCR (falso) -> confirma texto.

    cd backend && pip install -r requirements-dev.txt && python -m pytest
Roda com SQLite temporario e sem chamar o Google (o OCR e trocado por um falso).
"""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/teste.db"
os.environ["JWT_SECRET"] = "x" * 32
os.environ["GEMINI_API_KEY"] = "falsa"
os.environ["UPLOAD_DIR"] = f"{_tmp}/uploads"

from fastapi.testclient import TestClient  # noqa: E402

import app.routers.ocr as ocr_router  # noqa: E402
import seed  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.usuario import Atividade  # noqa: E402

seed.run_seed()
ocr_router.extract_text = lambda _bytes, _mime: "texto lido pelo ocr"
client = TestClient(app)
FOTO = {"file": ("redacao.jpg", b"\xff\xd8 bytes de foto", "image/jpeg")}


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def atividade_id():
    with SessionLocal() as db:
        return str(db.query(Atividade).first().id)


def test_fluxo_completo():
    aluno = token("aluno@domina.com")

    r = client.post("/submissoes/imagem", headers=aluno, files=FOTO, data={"atividade_id": atividade_id()})
    assert r.status_code == 201, r.text
    sub = r.json()
    assert sub["texto_ocr"] == "texto lido pelo ocr"
    assert sub["texto_confirmado"] is None

    r = client.put(f"/submissoes/{sub['id']}/confirmar", headers=aluno, json={"texto": "  texto corrigido  "})
    assert r.status_code == 200, r.text
    assert r.json()["texto_confirmado"] == "texto corrigido"
    assert r.json()["texto_ocr"] == "texto lido pelo ocr"  # original preservado

    # recarregar a tela: dono e professor da turma veem
    assert client.get(f"/submissoes/{sub['id']}", headers=aluno).json()["texto_confirmado"] == "texto corrigido"
    assert client.get(f"/submissoes/{sub['id']}", headers=token("professor@domina.com")).status_code == 200

    # confirmado nao muda mais
    r = client.put(f"/submissoes/{sub['id']}/confirmar", headers=aluno, json={"texto": "outro"})
    assert r.status_code == 409


def test_regras_de_acesso():
    aluno, prof = token("aluno@domina.com"), token("professor@domina.com")
    dados = {"atividade_id": atividade_id()}

    assert client.post("/submissoes/imagem", files=FOTO, data=dados).status_code == 401
    assert client.post("/submissoes/imagem", headers=prof, files=FOTO, data=dados).status_code == 422  # professor sem aluno_id
    sem_turma = {"atividade_id": "00000000-0000-0000-0000-000000000000"}
    assert client.post("/submissoes/imagem", headers=aluno, files=FOTO, data=sem_turma).status_code == 404

    pdf = {"file": ("x.pdf", b"%PDF", "application/pdf")}
    assert client.post("/submissoes/imagem", headers=aluno, files=pdf, data=dados).status_code == 400

    grande = {"file": ("g.jpg", b"0" * (ocr_router.MAX_IMAGEM_BYTES + 1), "image/jpeg")}
    assert client.post("/submissoes/imagem", headers=aluno, files=grande, data=dados).status_code == 413

    sub = client.post("/submissoes/imagem", headers=aluno, files=FOTO, data=dados).json()
    assert client.put(f"/submissoes/{sub['id']}/confirmar", headers=aluno, json={"texto": "   "}).status_code == 422


def test_ocr_sem_chave_responde_503():
    settings.GEMINI_API_KEY = None
    try:
        r = client.post("/ocr/extract", headers=token("aluno@domina.com"), files=FOTO)
        assert r.status_code == 503
    finally:
        settings.GEMINI_API_KEY = "falsa"


def test_imagem_sem_texto_responde_422():
    original, ocr_router.extract_text = ocr_router.extract_text, lambda _b, _m: ""
    try:
        assert client.post("/ocr/extract", headers=token("aluno@domina.com"), files=FOTO).status_code == 422
    finally:
        ocr_router.extract_text = original


def test_texto_publicado_responde_422():
    from app.ocr.gemini import TextoPublicado

    def recitacao(_b, _m):
        raise TextoPublicado()

    original, ocr_router.extract_text = ocr_router.extract_text, recitacao
    try:
        r = client.post("/ocr/extract", headers=token("aluno@domina.com"), files=FOTO)
        assert r.status_code == 422 and "publicada" in r.text
    finally:
        ocr_router.extract_text = original


def test_outro_aluno_nao_ve_submissao():
    from app.auth.security import hash_password
    from app.models.enum import PerfilEnum
    from app.models.usuario import Escola, Usuario

    with SessionLocal() as db:
        escola = db.query(Escola).first()
        db.add(Usuario(escola_id=escola.id, nome="intruso", email="intruso@domina.com",
                       senha_hash=hash_password(seed.SENHA), perfil=PerfilEnum.ALUNO))
        db.commit()
    sub = client.post("/submissoes/imagem", headers=token("aluno@domina.com"), files=FOTO,
                      data={"atividade_id": atividade_id()}).json()
    assert client.get(f"/submissoes/{sub['id']}", headers=token("intruso@domina.com")).status_code == 404


def test_falha_do_gemini_nao_vaza_detalhe():
    def quebra(_bytes, _mime):
        raise RuntimeError("API_KEY_INVALID segredo-interno")

    original, ocr_router.extract_text = ocr_router.extract_text, quebra
    try:
        r = client.post("/ocr/extract", headers=token("aluno@domina.com"), files=FOTO)
        assert r.status_code == 502
        assert "segredo-interno" not in r.text
    finally:
        ocr_router.extract_text = original


def test_gemini_usa_modelo_reserva_quando_cota_estoura():
    from types import SimpleNamespace

    from google.genai import errors

    from app.ocr import gemini

    chamados = []

    def gerar(model, contents, config):
        chamados.append(model)
        if model == settings.GEMINI_MODEL:
            raise errors.ClientError(429, {"error": {"message": "cota"}})
        return SimpleNamespace(candidates=[], text=" texto da reserva ")

    falso = SimpleNamespace(models=SimpleNamespace(generate_content=gerar))
    original, gemini._client = gemini._client, lambda: falso
    try:
        assert gemini.extract_text(b"img", "image/png") == "texto da reserva"
        assert chamados == [settings.GEMINI_MODEL, settings.GEMINI_MODEL_RESERVA]
    finally:
        gemini._client = original


def test_reduz_foto_grande_antes_do_gemini():
    import io

    from PIL import Image

    from app.ocr.gemini import LADO_MAXIMO, reduzir

    grande = io.BytesIO()
    Image.new("RGB", (3000, 4000), "white").save(grande, "PNG")
    dados, mime = reduzir(grande.getvalue(), "image/png")
    assert mime == "image/jpeg"
    assert max(Image.open(io.BytesIO(dados)).size) == LADO_MAXIMO

    # o que o Pillow nao abre passa direto (o Gemini le HEIC, por exemplo)
    assert reduzir(b"nao-e-imagem", "image/heic") == (b"nao-e-imagem", "image/heic")


def test_professor_envia_em_nome_do_aluno_e_gera_nota():
    from app import correcao as ia

    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    atividades = client.get("/atividades", headers=prof).json()
    assert atividades and atividades[0]["alunos"], atividades
    aluno_id = atividades[0]["alunos"][0]["id"]

    sub = client.post("/submissoes/imagem", headers=prof, files=FOTO,
                      data={"atividade_id": atividades[0]["id"], "aluno_id": aluno_id}).json()
    assert sub["aluno_id"] == aluno_id

    # nao corrige antes de confirmar
    assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 409
    assert client.put(f"/submissoes/{sub['id']}/confirmar", headers=prof, json={"texto": "redacao"}).status_code == 200

    nota_maxima = ia.ResultadoIA(
        competencias=[{"codigo": f"C{i}", "analise": "ok", "nota": 200, "justificativa": "ok"} for i in range(5, 0, -1)],
        feedback_geral="muito bom", confianca=0.9,
    )
    original, ia.corrigir = ia.corrigir, lambda texto, tema: (nota_maxima, settings.GEMINI_MODEL)
    try:
        # aluno nao gera nem ve a nota da IA antes da aprovacao (RN-01)
        assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=aluno, json={}).status_code == 403
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={"tema": "tema x"})
        assert r.status_code == 201, r.text
        c = r.json()
        assert c["nota_ia"] == 1000 and c["status"] == "PENDENTE"
        assert [k["codigo"] for k in c["criterios"]] == ["C1", "C2", "C3", "C4", "C5"]
        assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 409
        assert client.get(f"/submissoes/{sub['id']}/correcao", headers=prof).json()["nota_ia"] == 1000
        assert client.get(f"/submissoes/{sub['id']}/correcao", headers=aluno).status_code == 403

        # corrigida pelo modelo reserva: sempre "requer atencao", mesmo com confianca alta
        ia.corrigir = lambda texto, tema: (nota_maxima, settings.GEMINI_MODEL_RESERVA)
        sub2 = client.post("/submissoes/imagem", headers=prof, files=FOTO,
                           data={"atividade_id": atividades[0]["id"], "aluno_id": aluno_id}).json()
        client.put(f"/submissoes/{sub2['id']}/confirmar", headers=prof, json={"texto": "redacao"})
        assert client.post(f"/submissoes/{sub2['id']}/corrigir", headers=prof, json={}).json()["status"] == "REQUER_ATENCAO"
    finally:
        ia.corrigir = original


def test_nota_da_ia_vira_nivel_valido_do_enem():
    from app.correcao import ResultadoIA

    r = ResultadoIA.model_validate({
        "competencias": [{"codigo": f"C{i}", "analise": "x", "nota": n, "justificativa": "x"} for i, n in zip(range(1, 6), [130, 200, 15, 199, 60])],
        "feedback_geral": "x", "confianca": 0.5,
    })
    assert [c.nota for c in r.competencias] == [120, 200, 0, 200, 40]
    try:
        ResultadoIA.model_validate({"competencias": [{"codigo": "C1", "analise": "x", "nota": 0, "justificativa": "x"}] * 5,
                                    "feedback_geral": "x", "confianca": 0.5})
        raise AssertionError("aceitou competencia repetida")
    except ValueError:
        pass


def test_corrigir_faz_media_de_2_correcoes_e_3a_se_discrepar():
    from app import correcao as ia

    def resultado(notas, confianca=0.9):
        return ia.ResultadoIA(
            competencias=[{"codigo": f"C{i}", "analise": "x", "nota": n, "justificativa": "x"} for i, n in zip(range(1, 6), notas)],
            feedback_geral="x", confianca=confianca,
        )

    def com(*respostas):
        fila = list(respostas)
        ia._uma_correcao = lambda texto, tema, temperatura: fila.pop(0)
        return fila

    original = ia._uma_correcao
    try:
        # como no ENEM: 160 e 200 viram 180 (a media nao volta para o nivel de 40)
        com((resultado([160, 200, 160, 120, 200]), settings.GEMINI_MODEL),
            (resultado([200, 200, 120, 120, 160], 0.7), settings.GEMINI_MODEL))
        r, modelo = ia.corrigir("texto", "tema")
        assert [c.nota for c in r.competencias] == [180, 200, 140, 120, 180]
        # confianca vem da divergencia entre as 2 (40 pontos no total), nao da autoavaliacao do modelo
        assert modelo == settings.GEMINI_MODEL and r.confianca == 1 - 40 / 250

        # diferenca de 120 numa competencia: 3a correcao, media do par mais proximo e vai para o professor
        sobra = com((resultado([200, 200, 200, 200, 200]), settings.GEMINI_MODEL),
                    (resultado([200, 200, 80, 200, 200]), settings.GEMINI_MODEL),
                    (resultado([200, 200, 160, 200, 200]), settings.GEMINI_MODEL_RESERVA))
        r, modelo = ia.corrigir("texto", "tema")
        assert not sobra and [c.nota for c in r.competencias] == [200, 200, 180, 200, 200]
        assert r.confianca < 0.6 and modelo == settings.GEMINI_MODEL_RESERVA
    finally:
        ia._uma_correcao = original
