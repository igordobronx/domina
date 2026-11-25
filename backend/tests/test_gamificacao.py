"""XP, sequencia de dias e conquistas. As contas sao uma funcao pura (montar_xp); a rota e testada no fim."""
from datetime import date, timedelta

from tests.test_rbac import client, token  # noqa: F401  (primeiro: prepara o banco de teste)
from vinculo_teste import vincular  # noqa: E402

from app.gamificacao import Aprovacao, Envio, MetaFeita, Resposta, montar_xp
from app.metas import nivel_de

HOJE = date(2026, 11, 18)


def d(dias_atras: int) -> date:
    return HOJE - timedelta(days=dias_atras)


def xp_sem_conquistas(r: dict) -> int:
    return r["xp"] - 20 * sum(1 for c in r["conquistas"] if c["conquistada_em"])


def conquista(r: dict, codigo: str) -> dict:
    return next(c for c in r["conquistas"] if c["codigo"] == codigo)


def test_envio_no_prazo_vale_15_e_da_primeiro_passo():
    r = montar_xp([Envio(d(3), "Redação 1", no_prazo=True, redacao=True)], [], [], [], HOJE)
    assert xp_sem_conquistas(r) == 15
    assert conquista(r, "PRIMEIRO_PASSO")["conquistada_em"] == d(3)
    assert r["xp"] == 35  # 15 + 20 da conquista


def test_envio_fora_do_prazo_vale_10():
    r = montar_xp([Envio(d(3), "Prova", no_prazo=False, redacao=False)], [], [], [], HOJE)
    assert xp_sem_conquistas(r) == 10


def test_aprovacao_com_80_ou_mais_vale_15_e_abaixo_vale_5():
    alta = montar_xp([], [Aprovacao(d(2), "R1", pct=85, redacao=True, nota=850)], [], [], HOJE)
    baixa = montar_xp([], [Aprovacao(d(2), "R2", pct=70, redacao=True, nota=700)], [], [], HOJE)
    assert xp_sem_conquistas(alta) == 15
    assert xp_sem_conquistas(baixa) == 5


def test_exercicios_tem_teto_de_30_por_dia():
    r = montar_xp([], [], [Resposta(d(1), correta=True) for _ in range(10)], [], HOJE)
    assert xp_sem_conquistas(r) == 30
    # dois dias diferentes: cada um tem o seu teto
    r2 = montar_xp([], [], [Resposta(d(1), True), Resposta(d(5), False)], [], HOJE)
    assert xp_sem_conquistas(r2) == 5 + 2


def test_meta_vale_os_pontos_dela_e_da_meta_batida():
    r = montar_xp([], [], [], [MetaFeita(d(4), "Entregar 3", 50)], HOJE)
    assert xp_sem_conquistas(r) == 50
    assert conquista(r, "META_BATIDA")["conquistada_em"] == d(4)


def test_sete_dias_seguidos_dao_bonus_e_constancia():
    respostas = [Resposta(d(i), correta=False) for i in range(7)]  # hoje e os 6 dias antes
    r = montar_xp([], [], respostas, [], HOJE)
    assert xp_sem_conquistas(r) == 7 * 2 + 15
    assert r["sequencia"] == {"atual": 7, "melhor": 7, "estudou_hoje": True}
    assert conquista(r, "CONSTANCIA")["conquistada_em"] == HOJE
    assert conquista(r, "IMPARAVEL")["conquistada_em"] is None
    assert conquista(r, "IMPARAVEL")["progresso"] == 7


def test_sequencia_quebra_se_faltou_ontem_e_hoje():
    r = montar_xp([], [], [Resposta(d(2), False), Resposta(d(3), False)], [], HOJE)
    assert r["sequencia"] == {"atual": 0, "melhor": 2, "estudou_hoje": False}
    # estudou ontem: a sequencia continua viva
    r2 = montar_xp([], [], [Resposta(d(1), False), Resposta(d(2), False)], [], HOJE)
    assert r2["sequencia"]["atual"] == 2


def test_redator_e_nota_900():
    envios = [Envio(d(10 + i), f"R{i}", no_prazo=False, redacao=True) for i in range(5)]
    aprov = [Aprovacao(d(1), "R0", pct=92, redacao=True, nota=920)]
    r = montar_xp(envios, aprov, [], [], HOJE)
    assert conquista(r, "REDATOR")["conquistada_em"] == d(10)  # a 5a redacao, por data
    assert conquista(r, "NOTA_900")["conquistada_em"] == d(1)


def test_historico_mais_recente_primeiro_e_soma_bate():
    r = montar_xp([Envio(d(5), "R1", True, True)], [], [Resposta(d(1), True)], [], HOJE)
    datas = [h["data"] for h in r["historico"]]
    assert datas == sorted(datas, reverse=True)
    assert sum(h["xp"] for h in r["historico"]) == r["xp"]


def test_faixas_de_nivel():
    assert nivel_de(0)["nivel"] == 1
    assert nivel_de(79)["nivel"] == 1
    n = nivel_de(80)
    assert (n["nivel"], n["nome"], n["pontos_proximo"], n["nome_proximo"]) == (2, "Aprendiz", 300, "Explorador")
    assert nivel_de(1600)["nome"] == "Lenda" and nivel_de(1600)["pontos_proximo"] is None


def test_aluno_sem_nada():
    r = montar_xp([], [], [], [], HOJE)
    assert r["xp"] == 0 and r["historico"] == []
    assert r["sequencia"] == {"atual": 0, "melhor": 0, "estudou_hoje": False}
    assert len(r["conquistas"]) == 9 and not any(c["conquistada_em"] for c in r["conquistas"])


# ---------------- rota (banco de teste do RBAC) ----------------

_c = {}


def _setup():
    g = token("gestor@domina.com")
    if not _c:
        turma = client.post("/turmas", headers=g, json={"nome": "Turma XP", "ano": 2026}).json()["id"]
        mk = lambda nome, email, perfil: client.post("/usuarios", headers=g, json={  # noqa: E731
            "nome": nome, "email": email, "senha": "123456", "perfil": perfil, "turma_id": turma}).json()["id"]
        mk("Prof XP", "prof.xp@x.com", "PROFESSOR")
        a1 = mk("Ana XP", "ana.xp@x.com", "ALUNO")
        a2 = mk("Beto XP", "beto.xp@x.com", "ALUNO")
        materia = client.post("/materias", headers=g, json={"nome": "Mat XP", "area": "EXATAS"}).json()["id"]
        vincular("prof.xp@x.com", turma, materia)
        _c.update(turma=turma, a1=a1, a2=a2, materia=materia)
    return g, token("prof.xp@x.com", "123456"), _c


def _prova_acertada(prof, aluno_id, c):
    """Prova objetiva de 10 pontos que o aluno acerta: envio confirmado + correcao ja aprovada (100%)."""
    ativ = client.post("/atividades/lote", headers=prof, json={
        "materia_id": c["materia"], "turma_ids": [c["turma"]], "titulo": "Prova XP", "tipo": "PROVA_OBJETIVA",
        "valor_total": 10, "questoes": [{"enunciado": "1+1?", "alternativas": ["1", "2"], "resposta_correta": "B"}]}).json()[0]
    r = client.post("/submissoes/objetiva", headers=prof, json={"atividade_id": ativ["id"], "aluno_id": aluno_id, "respostas": {"Q1": "B"}})
    assert r.status_code == 201, r.text


def test_rota_aluno_novo_comeca_do_zero():
    _setup()
    r = client.get("/gamificacao/minha", headers=token("beto.xp@x.com", "123456"))
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["nivel"]["nivel"] == 1 and j["nivel"]["pontos"] == 0
    assert j["historico"] == [] and j["sequencia"]["atual"] == 0
    assert len(j["conquistas"]) == 9


def test_rota_envio_aprovado_da_xp_e_equipe_nao_acessa():
    g, p, c = _setup()
    _prova_acertada(p, c["a1"], c)
    j = client.get("/gamificacao/minha", headers=token("ana.xp@x.com", "123456")).json()
    # enviou (+10, sem prazo) + aprovada com 100% (+15) + conquista Primeiro passo (+20)
    assert j["nivel"]["pontos"] == 45
    assert any(h["motivo"].startswith("Conquista: Primeiro passo") for h in j["historico"])
    assert client.get("/gamificacao/minha", headers=p).status_code == 403
    assert client.get("/gamificacao/minha", headers=g).status_code == 403
    # /metas/minhas e o ranking usam o mesmo XP
    assert client.get("/metas/minhas", headers=token("ana.xp@x.com", "123456")).json()["nivel"]["pontos"] == 45
    rank = client.get(f"/metas/ranking?turma_id={c['turma']}", headers=p).json()
    assert rank[0]["nome"] == "Ana XP" and rank[0]["pontos"] == 45


def test_datas_do_banco_em_utc_viram_dia_de_brasilia():
    from datetime import datetime

    from app.gamificacao import dia_local
    # 22h de Brasilia no dia 18 = 01h UTC do dia 19 (o banco grava UTC)
    assert dia_local(datetime(2026, 11, 19, 1, 0)) == date(2026, 11, 18)
    assert dia_local(datetime(2026, 11, 19, 12, 0)) == date(2026, 11, 19)
