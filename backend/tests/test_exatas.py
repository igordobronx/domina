"""Correcao de exercicios de materias exatas (matematica/fisica/quimica): gabarito -> IA confere
resposta por questao -> professor aprova -> aluno ve a nota (sem entrar na evolucao de redacao).

    cd backend && python -m pytest tests/test_exatas.py
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

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
import app.correcao_exatas as exatas_mod  # noqa: E402
from app.main import app  # noqa: E402

seed.run_seed()
client = TestClient(app)


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def criar_turma_e_materia(prof):
    gestor = token("gestor@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    materia = client.post("/materias", headers=gestor,
                          json={"nome": "Matemática", "tipo": "MATERIA_OBJETIVA"}).json()
    return turma_id, materia["id"]


def criar_atividade_com_gabarito(prof, turma_id, materia_id):
    payload = {
        "materia_id": materia_id, "turma_id": turma_id, "titulo": "Lista 1 - Equações", "tipo": "EXERCICIO",
        "questoes": [
            {"enunciado": "Resolva 2x + 3 = 7", "resposta_correta": "x = 2"},
            {"enunciado": "Resolva 3x = 9", "resposta_correta": "x = 3"},
        ],
    }
    r = client.post("/atividades", headers=prof, json=payload)
    assert r.status_code == 201, r.text
    atividade = r.json()
    # o aluno precisa ver o enunciado real de cada questao (nao um texto fixo de outra materia)
    assert atividade["questoes"] == [
        {"codigo": "Q1", "enunciado": "Resolva 2x + 3 = 7", "tem_imagem": False},
        {"codigo": "Q2", "enunciado": "Resolva 3x = 9", "tem_imagem": False},
    ]
    # sem valor_total explicito, assume 1000 (como a redacao) e divide pelas questoes
    assert atividade["valor_total"] == 1000.0
    return atividade


def _gemini_falso(notas):
    import json
    from types import SimpleNamespace

    def gerar(prompt, config):
        payload = {
            "questoes": [{"codigo": f"Q{i+1}", "nota": n, "justificativa": "x"} for i, n in enumerate(notas)],
            "confianca": 0.9,
        }
        return SimpleNamespace(text=json.dumps(payload)), "modelo-falso"
    return gerar


def test_atividade_de_exatas_exige_gabarito():
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    payload = {"materia_id": materia_id, "turma_id": turma_id, "titulo": "Sem gabarito", "tipo": "EXERCICIO"}
    assert client.post("/atividades", headers=prof, json=payload).status_code == 422


def test_fluxo_completo_exatas():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)
    assert atividade["materia"] == "Matemática"

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "Questão 1: x = 2\nQuestão 2: x = 5"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 0])
    try:
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        assert r.status_code == 201, r.text
        c = r.json()
        # IA acerta/erra na escala relativa 0..200, mas a nota guardada ja vem reescalada: 1000
        # de valor_total / 2 questoes = 500 cada, entao 200/200 vira 500 e 0/200 vira 0
        assert c["nota_ia"] == 500  # 500 + 0
        assert len(c["criterios"]) == 2
        codigos = sorted(k["codigo"] for k in c["criterios"])
        assert codigos == ["Q1", "Q2"]
        assert c["feedback"] == "500 de 1000 pontos: 1 questão(ões) certa(s), 0 com acerto parcial, 1 sem pontos."

        # aprovar com so 2 criterios (nao precisa ser exatamente 5 como na redacao)
        aprovacao = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 500}, {"codigo": "Q2", "nota": 0}],
            "feedback": "Revise a segunda equação.",
        })
        assert aprovacao.status_code == 200, aprovacao.text
        assert aprovacao.json()["nota_professor"] == 500

        # aluno ve a nota (RN-01: so depois de aprovada)
        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["atividade_id"] == atividade["id"])
        assert desta["nota"] == 500 and desta["status"] == "APROVADA"

        # exatas nao alimenta a evolucao de redacao (tema especifico da atividade, nunca se repete)
        dominio = client.get("/dominio/meu", headers=aluno).json()
        codigos_dominio = {d["habilidade_codigo"] for d in dominio}
        assert not codigos_dominio & {"Q1", "Q2"}
    finally:
        exatas_mod.gerar = original


def test_aluno_gera_propria_correcao_exatas_e_professor_aprova_depois():
    # mesma RN-01 relaxada do test_fluxo_envio.py, aqui pro lado de exatas
    prof, aluno = token("professor@domina.com"), token("aluno2@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "x = 2 e x = 3"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 200])
    try:
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=aluno, json={})
        assert r.status_code == 201, r.text

        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["id"] == sub["id"])
        # _gemini_falso usa um "modelo-falso" (nao o configurado), entao vai pra REQUER_ATENCAO;
        # a nota provisoria (nota_ia) ja aparece pro aluno de qualquer jeito
        assert desta["status"] == "REQUER_ATENCAO" and desta["nota"] == 1000  # 500 + 500, provisorio

        aprovacao = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 500}, {"codigo": "Q2", "nota": 500}],
        })
        assert aprovacao.status_code == 200, aprovacao.text

        minha = client.get("/submissoes/minhas", headers=aluno).json()
        desta = next(m for m in minha if m["id"] == sub["id"])
        assert desta["status"] == "APROVADA" and desta["nota"] == 1000
    finally:
        exatas_mod.gerar = original


def test_aprovar_exige_todos_os_criterios():
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)
    aluno = token("aluno2@domina.com")
    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "x = 2 e x = 3"}).json()

    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 200])
    try:
        client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        r = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof,
                       json={"notas": [{"codigo": "Q1", "nota": 200}]})  # faltou Q2
        assert r.status_code == 422
    finally:
        exatas_mod.gerar = original


def test_valor_total_configuravel_e_dividido_pelas_questoes():
    # professor define o valor total da atividade (em vez de cada questao valer 200 fixo);
    # o sistema divide igualmente entre as questoes cadastradas
    prof, aluno = token("professor@domina.com"), token("aluno3@domina.com")
    gestor = token("gestor@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    materia = client.post("/materias", headers=gestor,
                          json={"nome": "Física II", "tipo": "MATERIA_OBJETIVA"}).json()
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": materia["id"], "turma_id": turma_id, "titulo": "Prova - 4 questões", "tipo": "PROVA_OBJETIVA",
        "valor_total": 400,
        "questoes": [
            {"enunciado": f"Questão {i}", "resposta_correta": f"resposta {i}"} for i in range(1, 5)
        ],
    }).json()
    assert atividade["valor_total"] == 400.0  # 4 questoes -> 100 pontos cada

    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "respostas quaisquer"}).json()
    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([200, 200, 80, 0])
    try:
        r = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
        assert r.status_code == 201, r.text
        c = r.json()
        # 200/200 * 100 = 100, 80/200 * 100 = 40, 0 -> 0
        notas = {k["codigo"]: k["nota"] for k in c["criterios"]}
        assert notas == {"Q1": 100.0, "Q2": 100.0, "Q3": 40.0, "Q4": 0.0}
        assert c["nota_ia"] == 240.0

        # professor nao pode dar mais do que o valor da questao (100) na aprovacao
        excesso = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": f"Q{i}", "nota": 200 if i == 1 else notas[f"Q{i}"]} for i in range(1, 5)],
        })
        assert excesso.status_code == 422

        ok = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": k, "nota": v} for k, v in notas.items()],
            "feedback": "Bom trabalho.",
        })
        assert ok.status_code == 200, ok.text
        assert ok.json()["nota_professor"] == 240.0
    finally:
        exatas_mod.gerar = original


def test_so_professor_ou_gestor_criam_materia():
    aluno = token("aluno@domina.com")
    r = client.post("/materias", headers=aluno, json={"nome": "Física", "tipo": "MATERIA_OBJETIVA"})
    assert r.status_code == 403


def test_enunciado_longo_nao_quebra_a_criacao():
    # bug real: Tema.nome era VARCHAR(150) no Postgres, mas um enunciado de prova discursiva
    # (gerado por IA, com contexto/formatacao) facilmente passa disso -> 500 ("Failed to fetch"
    # no navegador). Tema.nome agora e Text; este teste cobre a validacao do pydantic (max 2000).
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    enunciado_longo = "### **Questão 1** (Geometria Plana) " + "Lorem ipsum dolor sit amet. " * 50
    assert len(enunciado_longo) > 150
    r = client.post("/atividades", headers=prof, json={
        "materia_id": materia_id, "turma_id": turma_id, "titulo": "Prova discursiva", "tipo": "PROVA_DISCURSIVA",
        "questoes": [{"enunciado": enunciado_longo, "resposta_correta": "x = 42"}],
    })
    assert r.status_code == 201, r.text
    assert r.json()["questoes"][0]["enunciado"] == enunciado_longo.strip()


def test_figura_da_questao_vai_para_o_aluno_e_para_o_corretor():
    from io import BytesIO

    from PIL import Image

    def png(cor):
        b = BytesIO()
        Image.new("RGB", (40, 20), cor).save(b, "PNG")
        return b.getvalue()

    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    gestor2 = token("gestor2@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)
    url = f"/atividades/{atividade['id']}/questoes/Q1/imagem"

    assert client.get(url, headers=aluno).status_code == 404  # ainda sem figura
    r = client.post(url, headers=prof, files={"file": ("pka.png", png("red"), "image/png")})
    assert r.status_code == 204, r.text
    # texto nao e figura; aluno nao anexa; gestor de outra escola nao enxerga
    assert client.post(url, headers=prof, files={"file": ("x.txt", b"oi", "text/plain")}).status_code == 400
    assert client.post(url, headers=aluno, files={"file": ("a.png", png("red"), "image/png")}).status_code in (403, 404)
    assert client.get(url, headers=gestor2).status_code == 404
    assert client.post(f"/atividades/{atividade['id']}/questoes/Q9/imagem", headers=prof,
                       files={"file": ("a.png", png("red"), "image/png")}).status_code == 404

    # aluno da turma ve a figura; a atividade avisa quais questoes tem figura
    assert client.get(url, headers=aluno).headers["content-type"] == "image/png"
    qs = client.get("/atividades", headers=aluno).json()
    questoes = next(a for a in qs if a["id"] == atividade["id"])["questoes"]
    assert [q["tem_imagem"] for q in questoes] == [True, False]

    # trocar apaga a antiga do disco
    import uuid

    from app.database import SessionLocal
    from app.models.usuario import Tema
    with SessionLocal() as db:
        antiga = db.query(Tema).filter_by(atividade_id=uuid.UUID(atividade["id"]), habilidade_codigo="Q1").first().imagem
    client.post(url, headers=prof, files={"file": ("pka2.png", png("blue"), "image/png")})
    import os
    assert not os.path.exists(antiga)

    # o corretor recebe a figura junto do enunciado
    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "Q1: x = 2\nQ2: x = 3"}).json()
    recebido = {}
    gemini = _gemini_falso([200, 200])

    def espia(contents, config):
        recebido["contents"] = contents
        return gemini(contents, config)

    original, exatas_mod.gerar = exatas_mod.gerar, espia
    try:
        assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 201
    finally:
        exatas_mod.gerar = original
    partes = recebido["contents"]
    assert isinstance(partes, list) and partes[0] == "Figura da questão Q1:" and len(partes) == 3  # rotulo, imagem, prompt
    assert "figuras das questões" in partes[-1]

    # remover volta ao normal
    assert client.delete(url, headers=prof).status_code == 204
    assert client.get(url, headers=aluno).status_code == 404


def test_gabarito_discursivo_longo_e_aceito():
    # quimica discursiva: gabarito com mecanismo e nomes passa facilmente de 500 caracteres
    prof = token("professor@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    payload = {"materia_id": materia_id, "turma_id": turma_id, "titulo": "Química p1", "tipo": "PROVA_DISCURSIVA",
               "questoes": [{"enunciado": "e" * 3000, "resposta_correta": "g" * 3000}], "valor_total": 100}
    assert client.post("/atividades", headers=prof, json=payload).status_code == 201
    payload["questoes"][0]["resposta_correta"] = "g" * 5001  # ainda ha um teto
    assert client.post("/atividades", headers=prof, json=payload).status_code == 422


def test_folha_de_exatas_usa_ocr_de_desenhos_e_a_foto_manda_na_correcao():
    import io

    import app.routers.ocr as ocr_router
    from PIL import Image

    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)
    foto = io.BytesIO()
    Image.new("RGB", (60, 40), "white").save(foto, "PNG")

    chamadas = []

    def ocr_falso(_b, _m, exatas=False):
        chamadas.append(exatas)
        return "Q1: x = 2\n[desenho: estrutura com dois Br]"

    original_ocr, ocr_router.extract_text = ocr_router.extract_text, ocr_falso
    try:
        r = client.post("/submissoes/imagem", headers=aluno, data={"atividade_id": atividade["id"]},
                        files={"file": ("folha.png", foto.getvalue(), "image/png")})
    finally:
        ocr_router.extract_text = original_ocr
    assert r.status_code == 201, r.text
    assert chamadas == [True]  # materia de exatas -> OCR que le colunas e desenhos
    sub = r.json()
    client.put(f"/submissoes/{sub['id']}/confirmar", headers=aluno, json={"texto": "Q1: x = 2\n[desenho: estrutura com dois Br]"})

    recebido = {}
    gemini = _gemini_falso([80, 200])

    def espia(contents, config):
        recebido["contents"] = contents
        return gemini(contents, config)

    original, exatas_mod.gerar = exatas_mod.gerar, espia
    try:
        c = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).json()
    finally:
        exatas_mod.gerar = original
    prompt = recebido["contents"][-1]
    assert "FONTE PRINCIPAL" in prompt and "É resposta" in prompt  # foto manda; desenho conta
    # acerto parcial aparece no feedback (antes dizia "0/2 corretas" mesmo com pontos)
    assert "1 questão(ões) certa(s), 1 com acerto parcial, 0 sem pontos" in c["feedback"]


def test_professor_da_qualquer_nota_em_exatas_ate_o_valor_da_questao():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    turma_id, materia_id = criar_turma_e_materia(prof)
    atividade = criar_atividade_com_gabarito(prof, turma_id, materia_id)  # 1000 pontos / 2 questoes = 500 cada
    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade["id"], "texto": "Q1: x = 2\nQ2: x = 3"}).json()
    original, exatas_mod.gerar = exatas_mod.gerar, _gemini_falso([80, 200])
    try:
        assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 201
    finally:
        exatas_mod.gerar = original
    url = f"/submissoes/{sub['id']}/aprovar"
    acima = {"notas": [{"codigo": "Q1", "nota": 500.5}, {"codigo": "Q2", "nota": 10}], "feedback": "x"}
    assert client.put(url, headers=prof, json=acima).status_code == 422  # passa do valor da questao
    livre = {"notas": [{"codigo": "Q1", "nota": 123.45}, {"codigo": "Q2", "nota": 7.5}], "feedback": "x"}
    r = client.put(url, headers=prof, json=livre)
    assert r.status_code == 200, r.text
    assert r.json()["nota_professor"] == 130.95  # sem escala de 40 em 40 em exatas
