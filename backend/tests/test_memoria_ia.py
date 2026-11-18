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
    r = client.post("/materias", headers=token("professor@domina.com"), json={"nome": nome, "tipo": "MATERIA_OBJETIVA"})
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


def test_material_do_tipo_outros_e_aceito():
    prof = token("professor@domina.com")
    r = subir(prof, nova_materia("Matemática outros"), "resumo.txt", RUBRICA.encode(), tipo="OUTRO")
    assert r.status_code == 201 and r.json()["tipo"] == "OUTRO" and r.json()["status_processamento"] == "PROCESSADO"


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

    assert subir(prof, materia_id, "planilha.xlsx", b"\x00\x01\x02\x03" * 10).status_code == 422  # formato nao aceito
    r = subir(prof, materia_id, "quebrado.pdf", b"isto nao e um pdf")  # aceito, mas a IA nao consegue ler
    assert r.status_code == 201, r.text
    assert r.json()["status_processamento"] == "ERRO" and r.json()["detalhe"]

    resumo = client.get(f"/materias/{materia_id}/ia", headers=prof).json()
    assert (resumo["trechos_de_material"], resumo["correcoes_aprendidas"], resumo["instrucoes"]) == (1, 0, 0)
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
        m = client.get(f"/materias/{materia_id}/ia", headers=prof).json()
        assert (m["trechos_de_material"], m["correcoes_aprendidas"], m["instrucoes"]) == (1, 1, 0)

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
        # o professor ve o que a IA usou (e o aluno nao pode ver o material dele)
        fontes = client.get(f"/submissoes/{sub2['id']}/fontes-ia", headers=prof).json()
        assert {f["tipo"] for f in fontes["fontes"]} == {"material", "exemplo"} and fontes["aviso"] is None
        assert "verificação final" in str(fontes["fontes"])
        assert client.get(f"/submissoes/{sub2['id']}/fontes-ia", headers=aluno2).status_code == 403
        assert client.get(f"/submissoes/{sub1['id']}/fontes-ia", headers=prof).json()["fontes"] == []  # memoria vazia na epoca
        assert "Faltou a verificação final." in prompt
        assert prompt.index("MEMÓRIA DO DOMINA") < prompt.index("Respostas do aluno")
    finally:
        exatas_mod.gerar = original


def test_materia_teorica_compara_o_conteudo_e_nao_as_palavras():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    r = client.post("/materias", headers=prof, json={"nome": "Teoria musical", "tipo": "MATERIA_DISCURSIVA"})
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
    # na lista de materiais o professor ve so o que ele enviou (regra da tela de materiais); o gestor ve tudo.
    # A IA, porem, usa tambem o material da escola (o gestor): ver os trechos acima.
    nomes = lambda h: sorted(d["nome_arquivo"] for d in client.get(f"/materias/{materia_id}/documentos", headers=h).json())  # noqa: E731
    assert nomes(prof) == ["do_beto.txt"] and nomes(outro) == []
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
    materia_treino = nova_materia("Matemática treino")
    atividade = client.post("/atividades", headers=prof, json={
        "materia_id": materia_treino, "turma_id": turma_id, "titulo": "Soma", "tipo": "EXERCICIO",
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
    # concordancia: a IA deu 1000 e o professor 800 (20% de diferenca) = discordou; sem revisao nao conta
    c = client.get(f"/materias/{materia_treino}/ia", headers=prof).json()
    assert (c["revisadas"], c["iguais"], c["proximas"], c["longe"], c["concordancia"]) == (1, 0, 0, 1, 0)
    assert client.get(f"/materias/{nova_materia('Sem revisao')}/ia", headers=prof).json()["concordancia"] is None


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


def test_aviso_so_quando_ha_revisoes_suficientes_e_a_concordancia_e_baixa():
    from app.ia.memoria import concorda_pouco
    assert not concorda_pouco({"revisadas": 5, "concordancia_recente": 0})      # poucas revisoes: nao julga
    assert not concorda_pouco({"revisadas": 30, "concordancia_recente": 80})    # concorda bem
    assert concorda_pouco({"revisadas": 30, "concordancia_recente": 40})        # erra o jeito dele


def test_motivo_repetido_vira_sugestao_de_instrucao_e_so_vira_instrucao_se_o_professor_aceitar():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    materia_id = nova_materia("Matemática sugestão")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    url = f"/materias/{materia_id}/sugestoes-instrucoes"
    vistos = []
    original, exatas_mod.gerar = exatas_mod.gerar, espia_gemini([200], vistos)
    try:
        for n in range(3):
            atv = client.post("/atividades", headers=prof, json={
                "materia_id": materia_id, "turma_id": turma_id, "titulo": f"Lista {n}", "tipo": "EXERCICIO",
                "questoes": [{"enunciado": "Quanto é 2 + 2?", "resposta_correta": "4"}]}).json()
            sub = client.post("/submissoes/texto", headers=aluno, json={"atividade_id": atv["id"], "texto": "Q1: 4"}).json()
            assert client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={}).status_code == 201
            assert client.get(url, headers=prof).json() == []  # com menos de 3 motivos iguais nao sugere
            r = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
                "notas": [{"codigo": "Q1", "nota": 500}], "feedback": "ok",
                "motivo_mudanca": "Faltou mostrar a conta completa passo a passo."})
            assert r.status_code == 200, r.text
    finally:
        exatas_mod.gerar = original
    sugestoes = client.get(url, headers=prof).json()
    assert len(sugestoes) == 1 and sugestoes[0]["vezes"] == 3 and "conta completa" in sugestoes[0]["texto"]
    # dispensar esconde; nada vira instrucao sozinho
    assert client.get(f"/materias/{materia_id}/instrucoes", headers=prof).json() == []
    assert client.post(url + "/dispensar", headers=prof, json={"correcao_ids": sugestoes[0]["correcao_ids"]}).status_code == 204
    assert client.get(url, headers=prof).json() == []
    assert client.get(url, headers=token("aluno@domina.com")).status_code == 403


def test_selo_de_prontidao_grafico_e_lista_de_erros_da_ia():
    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    materia_id = nova_materia("Matemática prontidão")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    ia = lambda: client.get(f"/materias/{materia_id}/ia", headers=prof).json()  # noqa: E731
    assert ia()["nivel"] == "SEM_TREINO" and ia()["falta"]
    assert client.post(f"/materias/{materia_id}/instrucoes", headers=prof, json={"texto": "Exijo a verificação."}).status_code == 201
    assert ia()["nivel"] == "APRENDENDO" and "revise mais 20" in " ".join(ia()["falta"])
    original, exatas_mod.gerar = exatas_mod.gerar, espia_gemini([200], [])
    try:
        for n in range(5):
            atv = client.post("/atividades", headers=prof, json={
                "materia_id": materia_id, "turma_id": turma_id, "titulo": f"Lista {n}", "tipo": "EXERCICIO",
                "questoes": [{"enunciado": "Quanto é 2 + 2?", "resposta_correta": "4"}]}).json()
            sub = client.post("/submissoes/texto", headers=aluno, json={"atividade_id": atv["id"], "texto": "Q1: 4"}).json()
            c = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
            assert c.status_code == 201
            ia_nota = c.json()["nota_ia"]
            nota = ia_nota / 2 if n == 0 else ia_nota  # so a primeira: a IA errou
            r = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
                "notas": [{"codigo": "Q1", "nota": nota}], "feedback": "ok", "explicacao_ruim": n == 1})
            assert r.status_code == 200, r.text
    finally:
        exatas_mod.gerar = original
    r = ia()
    # 1 de 5 com o professor em metade da nota da IA (1000 -> 500): total (4500-5000)/5000 = -10%; media por correcao 10%
    assert r["vies"] == -10 and r["diferenca_media"] == 10
    assert r["revisadas"] == 5 and [e["ate"] for e in r["evolucao"]] == [5] and r["evolucao"][0]["concordancia"] == 80
    erros = client.get(f"/materias/{materia_id}/erros-da-ia", headers=prof).json()
    assert len(erros) == 2 and erros[0]["nota_ia"] == 1000 and erros[0]["nota_professor"] == 500
    assert erros[1]["explicacao_ruim"] is True  # nota certa, mas a explicacao estava ruim
    assert client.get(f"/materias/{materia_id}/erros-da-ia", headers=aluno).status_code == 403


def test_jeito_de_corrigir_boa_correcao_vem_primeiro_e_esquecer_nao_apaga():
    import uuid

    import exportar_treino
    from app.database import SessionLocal
    from app.ia import memoria
    from app.models.usuario import IaChamada, IaTrecho

    prof, aluno = token("professor@domina.com"), token("aluno@domina.com")
    materia_id = nova_materia("Matemática jeito")
    turma_id = client.get("/turmas/minhas", headers=prof).json()[0]["id"]
    ia = lambda: client.get(f"/materias/{materia_id}/ia", headers=prof).json()  # noqa: E731
    subs = []
    original, exatas_mod.gerar = exatas_mod.gerar, espia_gemini([200], [])
    try:
        for n in range(3):
            atv = client.post("/atividades", headers=prof, json={
                "materia_id": materia_id, "turma_id": turma_id, "titulo": f"Equação {n}", "tipo": "EXERCICIO",
                "questoes": [{"enunciado": "Quanto é 2 + 2?", "resposta_correta": "4"}]}).json()
            sub = client.post("/submissoes/texto", headers=aluno, json={"atividade_id": atv["id"], "texto": "Q1: 4"}).json()
            c = client.post(f"/submissoes/{sub['id']}/corrigir", headers=prof, json={})
            assert c.status_code == 201
            r = client.put(f"/submissoes/{sub['id']}/aprovar", headers=prof, json={
                "notas": [{"codigo": "Q1", "nota": c.json()["nota_ia"] / 2}], "feedback": "ok"})  # professor mais rigoroso
            assert r.status_code == 200, r.text
            subs.append(sub["id"])
    finally:
        exatas_mod.gerar = original

    # 1) "seu jeito": 50% mais baixo que a IA em todas
    assert ia()["vies"] == -50 and ia()["diferenca_media"] == 50  # (500-1000)*3 / (1000*3); |500-1000|/1000 em cada

    # 2) boa/ma sem mudar a nota, mesmo depois de aprovada; a boa vem primeiro na busca
    r = client.put(f"/submissoes/{subs[2]}/avaliacao-ia", headers=prof, json={"avaliacao": "BOA"})
    assert r.status_code == 200 and r.json()["avaliacao_ia"] == "BOA" and r.json()["nota_professor"] == 500
    assert client.put(f"/submissoes/{subs[2]}/avaliacao-ia", headers=aluno, json={"avaliacao": "BOA"}).status_code == 403
    mid = uuid.UUID(materia_id)
    with SessionLocal() as db:
        prof_id = db.query(IaTrecho.professor_id).filter_by(materia_id=mid).first()[0]
        achados = memoria.buscar(db, mid, "Equação Quanto é 2 + 2", memoria.CORRECAO, 1, prof_id)
        assert len(achados) == 1 and "EXEMPLO MODELO" in achados[0].texto
    assert client.put(f"/submissoes/{subs[2]}/avaliacao-ia", headers=prof, json={"avaliacao": None}).json()["avaliacao_ia"] is None

    # 3) esquecer = tirar de uso: a lista vem com as que a IA mais errou primeiro; nada e apagado
    itens = client.get(f"/materias/{materia_id}/aprendido", headers=prof).json()
    assert len(itens) == 3 and all(i["em_uso"] for i in itens) and itens[0]["erro"] >= itens[-1]["erro"] > 0
    alvo = itens[0]
    with SessionLocal() as db:  # uma chamada ao modelo ligada a correcao que vai ser esquecida (o fake de exatas nao grava)
        cid = db.query(IaTrecho.correcao_id).filter_by(id=uuid.UUID(alvo["id"])).scalar()
        db.add(IaChamada(tarefa="corrigir_gabarito", modelo="falso", entrada="pedido", saida="resposta", correcao_id=cid))
        db.commit()
    assert client.put(f"/materias/{materia_id}/aprendido/{alvo['tipo']}/{alvo['id']}", headers=prof,
                      json={"em_uso": False}).status_code == 204
    assert ia()["correcoes_aprendidas"] == 2  # a memoria nao usa mais
    def no_treino():  # trechos desta materia que entram no material de treino (e as chamadas ligadas ao esquecido)
        with SessionLocal() as db:
            exportar_treino.exportar_materiais(db, f"{_tmp}/materiais.jsonl")
            exportar_treino.exportar(db, f"{_tmp}/treino.jsonl")
            trechos = [l for l in open(f"{_tmp}/materiais.jsonl", encoding="utf-8") if materia_id in l]
            correcao_do_alvo = db.query(IaTrecho.correcao_id).filter_by(id=uuid.UUID(alvo["id"])).scalar()
            chamadas = db.query(IaChamada.id).filter_by(correcao_id=correcao_do_alvo).all()
            texto = open(f"{_tmp}/treino.jsonl", encoding="utf-8").read()
            return len(trechos), sum(str(i) in texto for (i,) in chamadas), len(chamadas)

    with SessionLocal() as db:
        assert db.query(IaTrecho).filter_by(materia_id=mid, origem="CORRECAO").count() == 3  # mas continua guardada
    # o que foi esquecido NAO entra no treino da nossa IA (nem as chamadas dele), mas continua no banco
    trechos, chamadas_no_treino, chamadas = no_treino()
    assert trechos == 2 and chamadas > 0 and chamadas_no_treino == 0
    # aprovar de novo (reindexar) nao "destira"; e da para voltar a usar
    assert client.put(f"/submissoes/{subs[2]}/avaliacao-ia", headers=prof, json={"avaliacao": "MA"}).status_code == 200
    assert ia()["correcoes_aprendidas"] == 2
    assert client.put(f"/materias/{materia_id}/aprendido/{alvo['tipo']}/{alvo['id']}", headers=prof,
                      json={"em_uso": True}).status_code == 204
    assert ia()["correcoes_aprendidas"] == 3
    trechos, chamadas_no_treino, chamadas = no_treino()  # voltou a usar: volta para o treino
    assert trechos == 3 and chamadas_no_treino == chamadas
    # material: "Arquivar" (um botao so): a IA para de usar e o treino tambem ignora, sem apagar
    doc = subir(prof, materia_id, "rubrica.txt", RUBRICA.encode()).json()
    assert ia()["trechos_de_material"] > 0
    assert client.delete(f"/documentos/{doc['id']}", headers=prof).status_code == 204
    assert ia()["trechos_de_material"] == 0
    with SessionLocal() as db:
        assert db.query(IaTrecho).filter_by(materia_id=mid, origem="MATERIAL").count() > 0  # guardado
    assert no_treino()[0] == 3  # mas fora do treino
    # "Voltar a usar": volta para a memoria e para o treino
    lista = client.get("/documentos?incluir_inativos=true", headers=prof).json()
    assert next(d for d in lista if d["id"] == doc["id"])["ativo"] is False
    assert doc["id"] not in [d["id"] for d in client.get("/documentos", headers=prof).json()]
    assert client.put(f"/documentos/{doc['id']}/uso", headers=prof, json={"em_uso": True}).json()["ativo"] is True
    assert ia()["trechos_de_material"] > 0 and no_treino()[0] > 3
    assert client.put(f"/documentos/{doc['id']}/uso", headers=token("aluno@domina.com"), json={"em_uso": False}).status_code == 403
