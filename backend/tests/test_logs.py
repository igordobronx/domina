"""Access log em JSON, eventos de seguranca no banco e IP atras de proxy."""
import json
import logging

from tests.test_rbac import client, escola_id, token  # noqa: F401  (reusa o banco/seed)

from app.config import settings
from app.database import SessionLocal
from app.models.usuario import EventoSeguranca


def _eventos(tipo):
    with SessionLocal() as db:
        return db.query(EventoSeguranca).filter_by(tipo=tipo).all()


def test_login_falho_e_ok_viram_evento_sem_senha():
    antes_f, antes_ok = len(_eventos("LOGIN_FALHA")), len(_eventos("LOGIN_OK"))
    r = client.post("/auth/login", json={"email": "aluno@domina.com", "senha": "senha-errada-123"})
    assert r.status_code == 401
    client.post("/auth/login", json={"email": "ninguem@x.com", "senha": "qualquer"})
    token("aluno@domina.com")
    falhas = _eventos("LOGIN_FALHA")
    assert len(falhas) == antes_f + 2 and len(_eventos("LOGIN_OK")) == antes_ok + 1
    assert falhas[-2].email_tentado == "aluno@domina.com" and falhas[-2].usuario_id is not None
    assert falhas[-1].usuario_id is None  # e-mail que nao existe
    # a senha nunca e gravada, nem na coluna nem no detalhe
    assert all("senha-errada" not in json.dumps([e.detalhe, e.email_tentado]) for e in falhas)


def test_403_vira_acesso_negado_com_usuario_e_request_id():
    h = token("aluno@domina.com")
    antes = len(_eventos("ACESSO_NEGADO"))
    r = client.get("/escolas", headers=h)
    assert r.status_code == 403
    novo = _eventos("ACESSO_NEGADO")[-1]
    assert len(_eventos("ACESSO_NEGADO")) == antes + 1
    assert novo.usuario_id is not None and novo.detalhe == "GET /escolas"
    assert novo.request_id == r.headers["X-Request-ID"]  # liga o evento ao access log


def test_sem_token_vira_nao_autenticado():
    assert client.get("/escolas").status_code == 401
    assert _eventos("NAO_AUTENTICADO")[-1].detalhe == "GET /escolas"


def test_access_log_json_sem_query_string_nem_token(caplog):
    h = token("gestor@domina.com")
    with caplog.at_level(logging.INFO, logger="domina.acesso"):
        client.get("/calendario?de=2030-03-01&ate=2030-03-31", headers=h)
    reg = [r for r in caplog.records if r.name == "domina.acesso"][-1]
    campos = reg.campos
    assert campos["rota"] == "/calendario" and campos["status"] == 200 and campos["usuario_id"]
    texto = json.dumps(campos) + reg.getMessage()
    assert "2030-03-01" not in texto and h["Authorization"][7:] not in texto


def test_ip_so_vem_do_proxy_quando_configurado(monkeypatch):
    def ip_da_falha():
        client.post("/auth/login", json={"email": "x@x.com", "senha": "y"}, headers={"X-Forwarded-For": "6.6.6.6, 203.0.113.9"})
        return _eventos("LOGIN_FALHA")[-1].ip
    monkeypatch.setattr(settings, "CONFIAR_PROXY", False)
    assert ip_da_falha() != "203.0.113.9"          # sem proxy, o cabecalho e ignorado (forjavel)
    monkeypatch.setattr(settings, "CONFIAR_PROXY", True)
    assert ip_da_falha() == "203.0.113.9"          # com proxy, vale o ultimo (o que o proxy acrescentou)


def test_cadeia_de_hash_detecta_alteracao_e_remocao():
    from sqlalchemy import text
    from app.seguranca import verificar_cadeia
    for _ in range(3):
        client.post("/auth/login", json={"email": "x@x.com", "senha": "y"})
    with SessionLocal() as db:
        assert verificar_cadeia(db)[0]
        seqs = [e.seq for e in db.query(EventoSeguranca).filter(EventoSeguranca.seq.isnot(None)).order_by(EventoSeguranca.seq)]
        meio = seqs[len(seqs) // 2]
        # 1) alterar o conteudo de uma linha
        db.execute(text("UPDATE evento_seguranca SET ip = '9.9.9.9' WHERE seq = :s"), {"s": meio}); db.commit()
        ok, msg = verificar_cadeia(db)
        assert not ok and str(meio) in msg
        db.execute(text("UPDATE evento_seguranca SET ip = 'testclient' WHERE seq = :s"), {"s": meio}); db.commit()
        assert verificar_cadeia(db)[0]
        # 2) apagar uma linha do meio
        db.execute(text("DELETE FROM evento_seguranca WHERE seq = :s"), {"s": meio}); db.commit()
        ok, msg = verificar_cadeia(db)
        assert not ok and "apagada" in msg


def test_auditoria_guarda_escola_ip_e_entra_na_cadeia():
    from sqlalchemy import text
    from app.auditoria import verificar_auditoria
    from app.models.usuario import AuditLog
    g = token("gestor@domina.com")
    r = client.post("/usuarios", headers=g, json={"nome": "Fulano", "email": "audit1@x.com", "senha": "123456", "perfil": "ALUNO"})
    assert r.status_code == 201
    with SessionLocal() as db:
        a = db.query(AuditLog).filter_by(acao="CRIAR", entidade="Usuario").order_by(AuditLog.seq.desc()).first()
        assert a.escola_id is not None and a.ip and a.resultado == "OK"
        assert a.request_id == r.headers["X-Request-ID"]
        assert verificar_auditoria(db)[0]
        db.execute(text("UPDATE audit_log SET acao = 'APROVAR' WHERE seq = :s"), {"s": a.seq}); db.commit()
        ok, msg = verificar_auditoria(db)
        assert not ok and "alterado" in msg
        db.execute(text("UPDATE audit_log SET acao = 'CRIAR' WHERE seq = :s"), {"s": a.seq}); db.commit()
        assert verificar_auditoria(db)[0]


def test_telas_de_log_so_para_quem_pode_e_gestor_so_ve_a_propria_escola():
    adm, ga, gb = token("admin@domina.com"), token("gestor@domina.com"), token("gestor2@domina.com")
    # seguranca e integridade: so admin
    for h in (ga, token("professor@domina.com"), token("aluno@domina.com")):
        assert client.get("/logs/seguranca", headers=h).status_code == 403
        assert client.get("/logs/integridade", headers=h).status_code == 403
    assert client.get("/logs/auditoria", headers=token("aluno@domina.com")).status_code == 403
    assert client.get("/logs/seguranca", headers=adm, params={"tipo": "LOGIN_FALHA"}).json()[0]["tipo"] == "LOGIN_FALHA"
    # auditoria: gestor so ve a propria escola e sem IP; admin ve tudo com IP
    client.post("/usuarios", headers=gb, json={"nome": "Z", "email": "auditb@x.com", "senha": "123456", "perfil": "ALUNO"})
    do_gestor = client.get("/logs/auditoria", headers=ga).json()
    assert do_gestor and all(l["escola"] == "COLEGIO PREPARA ENEM" for l in do_gestor)
    assert all(l["ip"] is None and l["request_id"] is None for l in do_gestor)
    do_admin = client.get("/logs/auditoria", headers=adm).json()
    assert {l["escola"] for l in do_admin} >= {"COLEGIO PREPARA ENEM", "COLEGIO VESTIBULAR NORTE"}
    assert any(l["ip"] for l in do_admin)
    # gestor forcando outra escola: 404
    assert client.get("/logs/auditoria", headers=ga, params={"escola_id": escola_id("COLEGIO VESTIBULAR NORTE")}).status_code == 404
    # consultar o log tambem fica registrado, e a integridade responde
    assert any(l["acao"] == "CONSULTAR" for l in client.get("/logs/auditoria", headers=adm).json())
    r = client.get("/logs/integridade", headers=adm).json()
    assert r["auditoria_ok"] and "integra" in r["auditoria"]


def test_acao_sensivel_pede_a_senha_de_novo():
    import seed
    adm = token("admin@domina.com")
    esc = client.post("/escolas", headers=adm, json={"nome": "Escola Reauth", "cnpj": "99888777000166"}).json()["id"]
    conta = {"nome": "G", "email": "g.reauth@x.com", "senha": "123456", "perfil": "GESTOR", "escola_id": esc}
    for h in ({}, {"X-Confirmar-Senha": "senha-errada"}):  # sem senha e com senha errada: 403
        assert client.post("/usuarios", headers={**adm, **h}, json=conta).status_code == 403
        assert client.put(f"/escolas/{esc}", headers={**adm, **h}, json={"ativa": False}).status_code == 403
    ok = {**adm, "X-Confirmar-Senha": seed.SENHA}
    assert client.post("/usuarios", headers=ok, json=conta).status_code == 201
    assert client.put(f"/escolas/{esc}", headers=ok, json={"ativa": False}).json()["ativa"] is False
    # editar so o nome nao pede a senha, e a senha enviada nunca aparece no log
    assert client.put(f"/escolas/{esc}", headers=adm, json={"nome": "Escola Reauth 2"}).status_code == 200
    assert all(seed.SENHA not in (e.detalhe or "") for e in _eventos("ACESSO_NEGADO"))


def test_retencao_apaga_so_o_comeco_e_a_cadeia_continua_valida():
    from datetime import timedelta
    from app.seguranca import verificar_cadeia
    from retencao import aplicar
    for _ in range(4):
        client.post("/auth/login", json={"email": "r@r.com", "senha": "y"})
    with SessionLocal() as db:
        # envelhece 2 linhas do INICIO da cadeia (a mais antiga primeiro, como na vida real)
        antigas = db.query(EventoSeguranca).filter(EventoSeguranca.seq.isnot(None)).order_by(EventoSeguranca.seq).limit(2).all()
        for e in antigas:
            e.criado_em = e.criado_em - timedelta(days=400)
        db.commit()
        total = db.query(EventoSeguranca).count()
        antes = verificar_cadeia(db)[0]  # o teste da cadeia, acima, deixou um buraco no meio: continua igual
        assert aplicar(db, 365)["evento_seguranca"] >= 2
        assert db.query(EventoSeguranca).count() <= total - 2
        assert verificar_cadeia(db)[0] == antes  # apagar o comeco nao quebra (nem conserta) a cadeia
