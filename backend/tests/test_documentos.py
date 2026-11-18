"""Materiais: vinculo com materia, visibilidade por professor, baixar e arquivar.

    cd backend && python -m pytest tests/test_documentos.py
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
from app.main import app  # noqa: E402

seed.run_seed()
client = TestClient(app)


def token(email):
    r = client.post("/auth/login", json={"email": email, "senha": seed.SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _segundo_professor():
    from app.auth.security import hash_password
    from app.database import SessionLocal
    from app.models.enum import PerfilEnum
    from app.models.usuario import Escola, Usuario
    with SessionLocal() as db:
        if not db.query(Usuario).filter_by(email="prof.materiais@domina.com").first():
            db.add(Usuario(escola_id=db.query(Escola).first().id, nome="Outro Prof", email="prof.materiais@domina.com",
                           senha_hash=hash_password(seed.SENHA), perfil=PerfilEnum.PROFESSOR))
            db.commit()
    return token("prof.materiais@domina.com")


def _enviar(headers, materia_id, nome="rubrica.pdf", conteudo=b"%PDF-1.4 teste"):
    return client.post(f"/materias/{materia_id}/documentos", headers=headers, data={"tipo": "RUBRICA"},
                       files={"file": (nome, conteudo, "application/pdf")})


def test_envio_vincula_materia_valida_arquivo_baixa_e_arquiva():
    prof, outro, gestor = token("professor@domina.com"), _segundo_professor(), token("gestor@domina.com")
    materia = client.get("/materias", headers=prof).json()[0]

    r = _enviar(prof, materia["id"])
    assert r.status_code == 201, r.text
    doc = r.json()
    assert doc["materia_id"] == materia["id"] and doc["materia_nome"] == materia["nome"]
    assert doc["pode_baixar"] is True and doc["enviado_por_nome"]

    # so PDF, DOCX, TXT e imagem
    assert _enviar(prof, materia["id"], nome="virus.exe").status_code == 422
    # materia que nao existe
    assert _enviar(prof, "00000000-0000-0000-0000-000000000000").status_code == 404

    # o professor ve so o que enviou; o outro professor nao ve nada disso; o gestor ve tudo
    assert doc["id"] in [d["id"] for d in client.get("/documentos", headers=prof).json()]
    assert doc["id"] not in [d["id"] for d in client.get("/documentos", headers=outro).json()]
    assert doc["id"] in [d["id"] for d in client.get("/documentos", headers=gestor).json()]
    assert client.get(f"/documentos/{doc['id']}/arquivo", headers=outro).status_code == 404

    # baixar devolve o mesmo arquivo
    baixado = client.get(f"/documentos/{doc['id']}/arquivo", headers=prof)
    assert baixado.status_code == 200 and baixado.content == b"%PDF-1.4 teste"

    # aluno e gestor de outra escola nao entram
    assert client.get("/documentos", headers=token("aluno@domina.com")).status_code == 403
    assert doc["id"] not in [d["id"] for d in client.get("/documentos", headers=token("gestor2@domina.com")).json()]
    assert client.get(f"/documentos/{doc['id']}/arquivo", headers=token("gestor2@domina.com")).status_code == 404

    # excluir = arquivar: some da lista, e so quem enviou (ou o gestor) consegue
    assert client.delete(f"/documentos/{doc['id']}", headers=outro).status_code == 404
    assert client.delete(f"/documentos/{doc['id']}", headers=prof).status_code == 204
    assert doc["id"] not in [d["id"] for d in client.get("/documentos", headers=gestor).json()]
    assert client.get(f"/documentos/{doc['id']}/arquivo", headers=prof).status_code == 404

    from app.database import SessionLocal
    from app.models.usuario import DocumentoBase
    with SessionLocal() as db:  # o registro continua no banco, so arquivado
        assert db.get(DocumentoBase, __import__("uuid").UUID(doc["id"])).ativo is False
