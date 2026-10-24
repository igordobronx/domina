"""Agente de correcao: o Claude (falso aqui) escolhe as ferramentas e o passo a passo fica gravado.

    cd backend && python -m pytest tests/test_agente.py
Mesma base de tests/test_fluxo_envio.py (sqlite temporario, sem chamar API de verdade).
"""
import os
import tempfile
import uuid

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
os.environ.setdefault("ANTHROPIC_API_KEY", "falsa")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")

from types import SimpleNamespace  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

import app.agente as agente_mod  # noqa: E402
import app.routers.agente as agente_router  # noqa: E402
import seed  # noqa: E402
from app import correcao as ia  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.estudos import ExercicioGerado  # noqa: E402
from app.main import app  # noqa: E402
from app.models.usuario import Atividade, AuditLog, CustoUso  # noqa: E402

seed.run_seed()
client = TestClient(app)


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def atividade_id():
    with SessionLocal() as db:
        return str(db.query(Atividade).first().id)


def _chamada(nome, **entrada):
    return SimpleNamespace(type="tool_use", id=f"id_{nome}", name=nome, input={"motivo": f"porque {nome}", **entrada})


def _cliente_roteirizado(roteiro):
    # cada chamada ao Claude devolve o proximo item do roteiro (uma lista de blocos)
    pedidos = []

    def create(**kwargs):
        pedidos.append(kwargs)
        return SimpleNamespace(stop_reason="tool_use", content=roteiro[len(pedidos) - 1],
                               usage=SimpleNamespace(input_tokens=100, output_tokens=20))

    falso = SimpleNamespace(messages=SimpleNamespace(create=create))
    falso.with_options = lambda **_: falso
    return falso, pedidos


def test_agente_decide_os_passos_e_grava_o_passo_a_passo():
    aluno, prof = token("aluno@domina.com"), token("professor@domina.com")
    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade_id(), "texto": "minha redacao sobre o tema"}).json()

    nota = ia.ResultadoIA(
        competencias=[{"codigo": f"C{i}", "analise": "ok", "nota": n, "justificativa": "ok",
                       "pontos": [{"trecho": "ok", "tipo": "acerto", "comentario": "ok"}]}
                      for i, n in zip(range(1, 6), [160, 160, 80, 160, 120])],
        feedback_geral="bom trabalho", confianca=0.9,
    )
    exercicio = ExercicioGerado(habilidade_codigo="C3", titulo="Argumento", enunciado="x",
                                opcoes=["a", "b", "c", "d"], resposta_correta=0, explicacao="x")
    roteiro = [
        [SimpleNamespace(type="text", text="Vou ler o envio."), _chamada("ler_envio")],
        [_chamada("corrigir_exatas")],  # escolha errada: a ferramenta devolve erro e o agente corrige o rumo
        [_chamada("corrigir_redacao_enem")],
        [_chamada("consultar_historico_aluno")],
        [_chamada("gerar_exercicios_reforco", competencias=["C3", "C5"])],
        [_chamada("sinalizar_professor", aviso="C3 muito abaixo das outras")],
        [_chamada("finalizar", mensagem_aluno="Mandou bem!", resumo_professor="Olhar a C3.")],
    ]
    falso, pedidos = _cliente_roteirizado(roteiro)
    originais = (agente_mod._client, ia.corrigir, agente_router.gerar_exercicios)
    agente_mod._client = lambda: falso
    ia.corrigir = lambda texto, tema: (nota, ia.MODELO_PRINCIPAL)
    agente_router.gerar_exercicios = lambda aluno_id, alvo: [exercicio]
    try:
        r = client.post(f"/submissoes/{sub['id']}/agente", headers=aluno, json={})
        assert r.status_code == 200, r.text
        corpo = r.json()
    finally:
        agente_mod._client, ia.corrigir, agente_router.gerar_exercicios = originais

    assert len(pedidos) == len(roteiro)  # parou no finalizar
    ferramentas = [p["ferramenta"] for p in corpo["passos"] if p["tipo"] == "ferramenta"]
    assert ferramentas == ["ler_envio", "corrigir_exatas", "corrigir_redacao_enem", "consultar_historico_aluno",
                           "gerar_exercicios_reforco", "sinalizar_professor", "finalizar"]
    assert corpo["passos"][0] == {"tipo": "pensamento", "texto": "Vou ler o envio."}
    assert corpo["passos"][2]["erro"] is True and corpo["passos"][1]["motivo"] == "porque ler_envio"
    assert corpo["correcao"]["nota_ia"] == 680 and corpo["correcao"]["status"] == "REQUER_ATENCAO"
    assert corpo["exercicios"][0]["titulo"] == "Argumento"
    assert corpo["mensagem_aluno"] == "Mandou bem!" and corpo["resumo_professor"] == "Olhar a C3."

    # log de auditoria (RF-42) e custo (RF-43): 7 chamadas ao Claude x 120 tokens
    with SessionLocal() as db:
        log = db.query(AuditLog).filter_by(acao="AGENTE_CORRIGIR", entidade_id=uuid.UUID(sub["id"])).all()
        assert len(log) == 1
        assert db.query(CustoUso).first().tokens_llm >= 7 * 120

    # o professor ve o mesmo passo a passo depois
    visto = client.get(f"/submissoes/{sub['id']}/agente", headers=prof)
    assert visto.status_code == 200 and visto.json()["passos"] == corpo["passos"]


def test_agente_que_cai_ainda_entrega_a_correcao():
    aluno = token("aluno@domina.com")
    sub = client.post("/submissoes/texto", headers=aluno,
                      json={"atividade_id": atividade_id(), "texto": "outra redacao"}).json()
    nota = ia.ResultadoIA(
        competencias=[{"codigo": f"C{i}", "analise": "ok", "nota": 120, "justificativa": "ok",
                       "pontos": [{"trecho": "ok", "tipo": "acerto", "comentario": "ok"}]} for i in range(1, 6)],
        feedback_geral="ok", confianca=0.9,
    )

    def quebra(**_):
        raise RuntimeError("API fora do ar")

    falso = SimpleNamespace(messages=SimpleNamespace(create=quebra))
    falso.with_options = lambda **_: falso
    originais = (agente_mod._client, ia.corrigir)
    agente_mod._client = lambda: falso
    ia.corrigir = lambda texto, tema: (nota, ia.MODELO_PRINCIPAL)
    try:
        r = client.post(f"/submissoes/{sub['id']}/agente", headers=aluno, json={})
    finally:
        agente_mod._client, ia.corrigir = originais
    assert r.status_code == 200, r.text
    assert r.json()["passos"][0]["tipo"] == "aviso" and r.json()["correcao"]["nota_ia"] == 600
