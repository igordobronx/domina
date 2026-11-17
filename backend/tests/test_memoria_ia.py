"""Memoria da IA por materia (RAG, app/ia): o professor sobe material e aprova correcoes; a IA
passa a receber isso como contexto na proxima correcao de exatas e ao sugerir exercicios.

    cd backend && python -m pytest tests/test_memoria_ia.py
Sem chamar API nenhuma: busca por palavras (IA_EMBEDDINGS=local) e Gemini/Claude falsos.
"""
import json
import os
import tempfile
from types import SimpleNamespace

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
os.environ.setdefault("ANTHROPIC_API_KEY", "falsa")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")
os.environ.setdefault("IA_EMBEDDINGS", "local")

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
import app.correcao_exatas as exatas_mod  # noqa: E402
import app.exercicios_ia as exercicios_mod  # noqa: E402
from app import correcao as redacao_mod  # noqa: E402
from app.ia.extracao import dividir  # noqa: E402
from app.main import app  # noqa: E402

seed.run_seed()
client = TestClient(app)

RUBRICA = (
    "Critérios do professor Beto para equações do primeiro grau.\n\n"
    "Sempre exigir a verificação final: o aluno deve substituir o valor de x na equação original.\n\n"
    "Resposta sem unidade em problema de velocidade perde metade dos pontos da questão."
)


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def nova_materia(nome):
    r = client.post("/materias", headers=token("gestor@domina.com"), json={"nome": nome, "tipo": "MATERIA_OBJETIVA"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def subir(prof, materia_id, nome, conteudo, tipo="RUBRICA"):
    return client.post(f"/materias/{materia_id}/documentos", headers=prof,
                       files={"file": (nome, conteudo)}, data={"tipo": tipo})


def espia_gemini(notas, vistos):
    def gerar(contents, config):
        vistos.append(contents if isinstance(contents, str) else contents[-1])
        payload = {"questoes": [{"codigo": f"Q{i+1}", "nota": n, "justificativa": "bate com o gabarito"}
                                for i, n in enumerate(notas)], "confianca": 0.9}
        return SimpleNamespace(text=json.dumps(payload)), exatas_mod.MODELO_PRINCIPAL
    return gerar


def test_dividir_corta_em_trechos_sem_perder_texto():
    texto = "\n\n".join(f"Parágrafo {i} " + "palavra " * 60 for i in range(10))
    trechos = dividir(texto, tamanho=600, sobra=50)
    assert len(trechos) > 5 and all(len(t) <= 700 for t in trechos)
    assert all(f"Parágrafo {i} " in " ".join(trechos) for i in range(10))


def test_material_e_lido_na_hora_e_formato_desconhecido_vira_erro():
    prof = token("professor@domina.com")
    materia_id = nova_materia("Matemática memória 1")

    r = subir(prof, materia_id, "rubrica.txt", RUBRICA.encode())
    assert r.status_code == 201, r.text
    assert r.json()["status_processamento"] == "PROCESSADO" and r.json()["detalhe"] is None

    r = subir(prof, materia_id, "planilha.xlsx", b"\x00\x01\x02\x03" * 10)
    assert r.status_code == 201, r.text
    assert r.json()["status_processamento"] == "ERRO" and "PDF" in r.json()["detalhe"]

    resumo = client.get(f"/materias/{materia_id}/ia", headers=prof).json()
    assert resumo == {"trechos_de_material": 1, "correcoes_aprendidas": 0, "instrucoes": 0}
    assert client.get(f"/materias/{materia_id}/ia", headers=token("aluno@domina.com")).status_code == 403


def test_correcao_de_exatas_usa_material_e_correcoes_aprovadas_do_professor():
    prof, aluno, aluno2 = token("professor@domina.com"), token("aluno@domina.com"), token("aluno2@domina.com")
    materia_id = nova_materia("Matemática memória 2")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": materia_id, "turma_id": turma_id, "titulo": "Lista de equações", "tipo": "EXERCICIO",
        "questoes": [{"enunciado": "Resolva a equação 2x + 3 = 7 e faça a verificação", "resposta_correta": "x = 2"}],
    }).json()
    vistos = []
    original, exatas_mod.gerar = exatas_mod.gerar, espia_gemini([200], vistos)
    try:
        # 1) memoria vazia: o prompt sai como sempre saiu
        sub1 = client.post("/submissoes/texto", headers=aluno,
                           json={"atividade_id": atividade["id"], "texto": "x = 2, sem verificação"}).json()
        assert client.post(f"/submissoes/{sub1['id']}/corrigir", headers=prof, json={}).status_code == 201
        assert "MEMÓRIA DO DOMINA" not in vistos[-1]

        # 2) o professor sobe a rubrica e aprova a correcao BAIXANDO a nota da IA
        assert subir(prof, materia_id, "rubrica.txt", RUBRICA.encode()).json()["status_processamento"] == "PROCESSADO"
        r = client.put(f"/submissoes/{sub1['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": "Q1", "nota": 500}], "feedback": "Faltou a verificação final.",
            "motivo_mudanca": "Sem a verificação eu só dou metade da questão.",
        })
        assert r.status_code == 200, r.text
        assert client.get(f"/materias/{materia_id}/ia", headers=prof).json() == {
            "trechos_de_material": 1, "correcoes_aprendidas": 1, "instrucoes": 0}

        # 3) na proxima correcao a IA recebe a rubrica e o exemplo do jeito do professor
        sub2 = client.post("/submissoes/texto", headers=aluno2,
                           json={"atividade_id": atividade["id"], "texto": "x = 2 (não fiz a verificação)"}).json()
        assert client.post(f"/submissoes/{sub2['id']}/corrigir", headers=prof, json={}).status_code == 201
        prompt = vistos[-1]
        assert "MEMÓRIA DO DOMINA" in prompt
        assert "exigir a verificação final" in prompt  # trecho da rubrica
        assert "Nota do professor: 500 de 1000" in prompt and "o professor CORRIGIU a nota" in prompt
        assert "a IA ERROU aqui, foi generosa demais" in prompt  # ela deu 1000 e ele baixou para 500
        assert "Sem a verificação eu só dou metade da questão." in prompt  # o porque, escrito pelo professor
        assert "Faltou a verificação final." in prompt
        assert prompt.index("MEMÓRIA DO DOMINA") < prompt.index("Respostas do aluno")
    finally:
        exatas_mod.gerar = original


def test_materia_teorica_compara_o_conteudo_e_nao_as_palavras():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    r = client.post("/materias", headers=token("gestor@domina.com"), json={"nome": "Teoria musical", "tipo": "MATERIA_DISCURSIVA"})
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": r.json()["id"], "turma_id": turma_id, "titulo": "Escalas", "tipo": "EXERCICIO",
        "questoes": [{"enunciado": "O que é uma escala maior?", "resposta_correta": "Sequência tom, tom, semitom, tom, tom, tom, semitom."}],
    }).json()
    vistos = []
    original, exatas_mod.gerar = exatas_mod.gerar, espia_gemini([200], vistos)
    try:
        sub = client.post("/submissoes/texto", headers=aluno,
                          json={"atividade_id": atividade["id"], "texto": "T T ST T T T ST"}).json()
        assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 201
        assert "matéria TEÓRICA" in vistos[-1]
    finally:
        exatas_mod.gerar = original


def test_memoria_nao_vaza_entre_materias():
    prof = token("professor@domina.com")
    com, sem = nova_materia("Física memória"), nova_materia("Química memória")
    subir(prof, com, "rubrica.txt", RUBRICA.encode())
    vistos = []

    def falso(prompt, schema, **kw):
        vistos.append(prompt)
        return schema.model_validate({"exercicios": [{"titulo": "t", "enunciado": "e", "resposta_exemplo": "r"}]}), "falso"

    original, exercicios_mod.gerar_json = exercicios_mod.gerar_json, falso
    try:
        pedido = {"assunto": "equações com verificação final", "tipo": "DISCURSIVO", "quantidade": 1}
        assert client.post("/exercicios/sugerir", headers=prof, json={**pedido, "materia_id": com}).status_code == 200
        assert "exigir a verificação final" in vistos[-1]  # exercicio sai do material do professor
        assert client.post("/exercicios/sugerir", headers=prof, json={**pedido, "materia_id": sem}).status_code == 200
        assert "MEMÓRIA DO DOMINA" not in vistos[-1]
    finally:
        exercicios_mod.gerar_json = original


def _pdf_escaneado(paginas=2):
    # PDF so com imagem (sem texto dentro), como um material escaneado
    import io
    from PIL import Image
    folhas = [Image.new("RGB", (300, 400), "white") for _ in range(paginas)]
    saida = io.BytesIO()
    folhas[0].save(saida, "PDF", save_all=True, append_images=folhas[1:])
    return saida.getvalue()


def test_material_em_foto_e_pdf_escaneado_e_lido_pelo_ocr():
    import io
    from PIL import Image
    import app.ocr.gemini as gemini_mod
    prof = token("professor@domina.com")
    materia_id = nova_materia("Música memória")
    chamadas = []

    def gerar(contents, config):
        chamadas.append(len(contents) - 1)  # quantas imagens foram junto do pedido
        return SimpleNamespace(text="Escala maior: tom, tom, semitom, tom, tom, tom, semitom."), "falso"

    original, gemini_mod.gerar = gemini_mod.gerar, gerar
    try:
        foto = io.BytesIO()
        Image.new("RGB", (200, 200), "white").save(foto, "JPEG")
        r = subir(prof, materia_id, "quadro.jpg", foto.getvalue())
        assert r.json()["status_processamento"] == "PROCESSADO", r.text
        r = subir(prof, materia_id, "apostila_escaneada.pdf", _pdf_escaneado(2))
        assert r.json()["status_processamento"] == "PROCESSADO", r.text
        assert chamadas == [1, 2]  # 1 foto; depois as 2 paginas do PDF numa chamada so
        assert client.get(f"/materias/{materia_id}/ia", headers=prof).json()["trechos_de_material"] == 2
    finally:
        gemini_mod.gerar = original


def test_aluno_envia_a_prova_em_pdf_e_cada_pagina_vira_uma_folha():
    import app.routers.submissoes as sub_mod
    prof, aluno3 = token("professor@domina.com"), token("aluno3@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": nova_materia("Matemática PDF"), "turma_id": turma_id, "titulo": "Lista em PDF", "tipo": "EXERCICIO",
        "questoes": [{"enunciado": "2 + 2", "resposta_correta": "4"}],
    }).json()
    vistos = []

    def ocr_falso(b, m, exatas=False, extras=()):
        vistos.append(1 + len(extras))
        return "Q1: 4"

    original, sub_mod.ocr = sub_mod.ocr, ocr_falso
    try:
        r = client.post("/submissoes/imagem", headers=aluno3, data={"atividade_id": atividade["id"]},
                        files=[("files", ("prova.pdf", _pdf_escaneado(3), "application/pdf"))])
        assert r.status_code == 201, r.text
        assert vistos == [3] and r.json()["texto_ocr"] == "Q1: 4"
        assert client.get(f"/submissoes/{r.json()['id']}/imagem?pagina=2", headers=aluno3).status_code == 200
        r = client.post("/submissoes/imagem", headers=aluno3, data={"atividade_id": atividade["id"]},
                        files=[("files", ("grande.pdf", _pdf_escaneado(7), "application/pdf"))])
        assert r.status_code == 422 and "7 páginas" in r.json()["detail"]
    finally:
        sub_mod.ocr = original


def test_memoria_e_de_cada_professor_e_material_do_gestor_vale_para_todos():
    gestor, prof = token("gestor@domina.com"), token("professor@domina.com")
    r = client.post("/usuarios", headers=gestor, json={
        "nome": "Prof Outro", "email": "prof.outro@x.com", "senha": "123456", "perfil": "PROFESSOR"})
    assert r.status_code == 201, r.text
    outro = client.post("/auth/login", json={"email": "prof.outro@x.com", "senha": "123456"}).json()["access_token"]
    outro = {"Authorization": f"Bearer {outro}"}
    materia_id = nova_materia("História memória")
    subir(prof, materia_id, "do_beto.txt", RUBRICA.encode())
    subir(gestor, materia_id, "da_escola.txt", "Regra da escola: toda equação precisa de verificação com unidade.".encode())
    vistos = []

    def falso(prompt, schema, **kw):
        vistos.append(prompt)
        return schema.model_validate({"exercicios": [{"titulo": "t", "enunciado": "e", "resposta_exemplo": "r"}]}), "falso"

    original, exercicios_mod.gerar_json = exercicios_mod.gerar_json, falso
    try:
        pedido = {"materia_id": materia_id, "assunto": "equação com verificação final", "tipo": "DISCURSIVO", "quantidade": 1}
        assert client.post("/exercicios/sugerir", headers=prof, json=pedido).status_code == 200
        assert "professor Beto" in vistos[-1] and "Regra da escola" in vistos[-1]
        assert client.post("/exercicios/sugerir", headers=outro, json=pedido).status_code == 200
        assert "professor Beto" not in vistos[-1] and "Regra da escola" in vistos[-1]  # so o que e da escola
    finally:
        exercicios_mod.gerar_json = original
    assert client.get(f"/materias/{materia_id}/ia", headers=prof).json()["trechos_de_material"] == 2
    assert client.get(f"/materias/{materia_id}/ia", headers=outro).json()["trechos_de_material"] == 1
    # na tela "Treinar IA" cada professor ve o que ele enviou e o que e da escola (gestor)
    nomes = lambda h: sorted(d["nome_arquivo"] for d in client.get(f"/materias/{materia_id}/documentos", headers=h).json())  # noqa: E731
    assert nomes(prof) == ["da_escola.txt", "do_beto.txt"] and nomes(outro) == ["da_escola.txt"]
    assert len(nomes(gestor)) == 2
    import exportar_treino
    from app.database import SessionLocal
    with SessionLocal() as db:
        arquivo = os.path.join(_tmp, "materiais.jsonl")
        assert exportar_treino.exportar_materiais(db, arquivo) >= 2
        assert "Regra da escola" in open(arquivo, encoding="utf-8").read()


def test_redacao_usa_v14_puro_sem_material_e_o_material_do_professor_quando_existe():
    prof, aluno, aluno2 = token("professor@domina.com"), token("aluno@domina.com"), token("aluno2@domina.com")
    atividade = next(a for a in client.get("/atividades", headers=prof).json() if a["tipo"] == "REDACAO")
    materia_redacao = next(m["id"] for m in client.get("/materias", headers=prof).json() if m["nome"] == atividade["materia"])
    vistos = []
    nota = redacao_mod.ResultadoIA.model_validate({
        "competencias": [{"codigo": f"C{i}", "analise": "a", "nota": 160, "justificativa": "j",
                          "pontos": [{"trecho": "", "tipo": "acerto", "comentario": "c"}]} for i in range(1, 6)],
        "feedback_geral": "f", "confianca": 0.9})

    def falso(prompt, schema, **kw):
        vistos.append(prompt)
        return nota, redacao_mod.MODELO_PRINCIPAL

    original, redacao_mod.gerar_json = redacao_mod.gerar_json, falso
    try:
        texto = "A desigualdade social no Brasil exige uma proposta de intervenção detalhada. " * 5
        sub1 = client.post("/submissoes/texto", headers=aluno, json={"atividade_id": atividade["id"], "texto": texto}).json()
        assert client.post(f"/submissoes/{sub1['id']}/corrigir", headers=prof, json={}).status_code == 201
        assert vistos[-1] == redacao_mod.PROMPT.format(tema=atividade["titulo"], texto=sub1["texto_confirmado"], contexto="")

        # aprovar NAO muda a redacao seguinte (correcoes aprovadas nao viram exemplo na redacao)...
        r = client.put(f"/submissoes/{sub1['id']}/aprovar", headers=prof, json={
            "notas": [{"codigo": f"C{i}", "nota": 120} for i in range(1, 6)]})
        assert r.status_code == 200, r.text
        # ...mas o material que o professor sobe na materia entra como complemento
        orientacao = "Nesta turma, a proposta de intervenção deve sempre citar o agente responsável."
        assert subir(prof, materia_redacao, "orientacoes.txt", orientacao.encode()).json()["status_processamento"] == "PROCESSADO"
        sub2 = client.post("/submissoes/texto", headers=aluno2, json={"atividade_id": atividade["id"], "texto": texto}).json()
        assert client.post(f"/submissoes/{sub2['id']}/corrigir", headers=prof, json={}).status_code == 201
        assert orientacao in vistos[-1] and "Exemplo 1" not in vistos[-1]
        assert "Você é um corretor experiente da redação do ENEM" in vistos[-1]  # a base v14 continua la
    finally:
        redacao_mod.gerar_json = original


def test_cada_resposta_do_modelo_vira_material_de_treino_ligado_a_nota_do_professor():
    import app.ocr.gemini as gemini_mod
    import exportar_treino
    from app.database import SessionLocal
    from app.models.usuario import IaChamada
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": nova_materia("Matemática treino"), "turma_id": turma_id, "titulo": "Soma", "tipo": "EXERCICIO",
        "questoes": [{"enunciado": "Quanto é 2 + 2?", "resposta_correta": "4"}],
    }).json()
    resposta = json.dumps({"questoes": [{"codigo": "Q1", "nota": 200, "justificativa": "bate"}], "confianca": 0.9})
    falso = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: SimpleNamespace(text=resposta)))
    original, gemini_mod._client = gemini_mod._client, lambda: falso  # so a API e falsa: o registro roda de verdade
    try:
        sub = client.post("/submissoes/texto", headers=aluno, json={"atividade_id": atividade["id"], "texto": "Q1: 4"}).json()
        assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 201
    finally:
        gemini_mod._client = original
    with SessionLocal() as db:
        chamadas = [c for c in db.query(IaChamada).filter_by(tarefa="corrigir_gabarito") if "Quanto é 2 + 2?" in c.entrada]
        assert len(chamadas) == 1 and chamadas[0].saida == resposta and chamadas[0].correcao_id is not None
        # sem a decisao do professor: entra no treino com peso menor, nao e marcado e NUNCA e apagado
        arquivo = os.path.join(_tmp, "treino.jsonl")
        exportar_treino.exportar(db, arquivo, "corrigir_gabarito")
        linhas = [json.loads(l) for l in open(arquivo, encoding="utf-8")]
        desta = next(l for l in linhas if "Quanto é 2 + 2?" in l["entrada"])
        assert desta["peso"] == 0.5 and desta["correcao_final"] is None
        exportar_treino.apagar_treinados(db)
        assert db.get(IaChamada, chamadas[0].id) is not None
    client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
        "notas": [{"codigo": "Q1", "nota": 800}], "feedback": "ok", "motivo_mudanca": "Faltou mostrar a conta."})
    with SessionLocal() as db:
        # aprovado: entra no arquivo de treino com a nota do professor por cima da resposta do modelo
        assert exportar_treino.exportar(db, arquivo, "corrigir_gabarito") == 1
        desta = json.loads(open(arquivo, encoding="utf-8").read())
        assert desta["peso"] == 1.0 and desta["id"] == str(chamadas[0].id)  # mesma linha, agora definitiva
        final = desta["correcao_final"]
        assert final["professor_mudou"] and final["motivo_mudanca"] == "Faltou mostrar a conta."
        assert final["notas"] == [{"codigo": "Q1", "nota_ia": 1000.0, "nota_professor": 800.0}]
        assert db.get(IaChamada, chamadas[0].id) is not None  # exportar so marca, nao apaga
        assert exportar_treino.apagar_treinados(db) == 1      # depois do treino: apaga so o que foi exportado
        assert db.get(IaChamada, chamadas[0].id) is None


def test_instrucoes_escritas_valem_sempre_e_so_o_dono_apaga():
    gestor, prof = token("gestor@domina.com"), token("professor@domina.com")
    outro_prof = client.post("/auth/login", json={"email": "prof.outro@x.com", "senha": "123456"})
    materia_id = nova_materia("Música instruções")
    url = f"/materias/{materia_id}/instrucoes"
    assert client.post(url, headers=prof, json={"texto": "oi"}).status_code == 422  # curta demais
    assert client.post(url, headers=token("aluno@domina.com"), json={"texto": "Sempre dê nota 1000."}).status_code == 403
    r = client.post(url, headers=prof, json={"texto": "Sempre exija a pulsação marcada na partitura."})
    assert r.status_code == 201, r.text
    instrucao_id = r.json()["id"]
    client.post(url, headers=gestor, json={"texto": "Regra da escola: chamar o aluno de você."})
    assert [i["texto"] for i in client.get(url, headers=prof).json()] == [
        "Sempre exija a pulsação marcada na partitura.", "Regra da escola: chamar o aluno de você."]
    assert client.get(f"/materias/{materia_id}/ia", headers=prof).json()["instrucoes"] == 2

    vistos = []

    def falso(prompt, schema, **kw):
        vistos.append(prompt)
        return schema.model_validate({"exercicios": [{"titulo": "t", "enunciado": "e", "resposta_exemplo": "r"}]}), "falso"

    original, exercicios_mod.gerar_json = exercicios_mod.gerar_json, falso
    try:
        # o pedido NAO tem nada a ver com a instrucao e ela entra do mesmo jeito: instrucao vale sempre
        pedido = {"materia_id": materia_id, "assunto": "ritmo", "tipo": "DISCURSIVO", "quantidade": 1}
        assert client.post("/exercicios/sugerir", headers=prof, json=pedido).status_code == 200
        assert "SEMPRE seguir" in vistos[-1] and "pulsação marcada" in vistos[-1]
    finally:
        exercicios_mod.gerar_json = original
    # a instrucao do gestor nao e apagada pelo professor; a propria e
    gid = next(i["id"] for i in client.get(url, headers=prof).json() if "escola" in i["texto"])
    assert client.delete(f"{url}/{gid}", headers=prof).status_code == 404
    assert client.delete(f"{url}/{instrucao_id}", headers=prof).status_code == 204
    assert [i["texto"] for i in client.get(url, headers=prof).json()] == ["Regra da escola: chamar o aluno de você."]
