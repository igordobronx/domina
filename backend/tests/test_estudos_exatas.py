"""Plano de estudo de exatas: o erro da correcao aprovada e guardado e vira exercicio.

    cd backend && python -m pytest tests/test_estudos_exatas.py
"""
import os
import re
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("GEMINI_API_KEY", "falsa")
os.environ.setdefault("ANTHROPIC_API_KEY", "falsa")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")

from fastapi.testclient import TestClient  # noqa: E402

import seed  # noqa: E402
import app.estudos as estudos_mod  # noqa: E402
from app.main import app  # noqa: E402

seed.run_seed()
client = TestClient(app)


def _montar():
    """Aluno novo com uma prova de matematica aprovada: Q1 tirou 20 de 50 (40%), Q2 tirou 45 de 50 (90%)."""
    from app.auth.security import hash_password
    from app.database import SessionLocal
    from app.models.enum import PerfilEnum, StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum, TipoMateriaEnum
    from app.models.usuario import Atividade, Correcao, CorrecaoCriterio, Escola, Materia, Submissao, Tema, Turma, Usuario
    with SessionLocal() as db:
        escola = db.query(Escola).first()
        aluno = Usuario(escola_id=escola.id, nome="Aluno Exatas", email="exatas@domina.com",
                        senha_hash=hash_password(seed.SENHA), perfil=PerfilEnum.ALUNO)
        mat = Materia(escola_id=escola.id, nome="Matemática", tipo=TipoMateriaEnum.MATERIA_DISCURSIVA)
        turma = db.query(Turma).filter_by(escola_id=escola.id).first()
        db.add_all([aluno, mat])
        db.flush()
        ativ = Atividade(materia_id=mat.id, turma_id=turma.id, titulo="Prova de funções",
                         tipo=TipoAtividadeEnum.PROVA_DISCURSIVA, valor_total=100)
        db.add(ativ)
        db.flush()
        q1 = Tema(materia_id=mat.id, atividade_id=ativ.id, nome="Determine a raiz de f(x)=2x-6", habilidade_codigo="Q1",
                  resposta_correta="x=3")
        q2 = Tema(materia_id=mat.id, atividade_id=ativ.id, nome="Calcule f(2) para f(x)=x+1", habilidade_codigo="Q2",
                  resposta_correta="3")
        sub = Submissao(atividade_id=ativ.id, aluno_id=aluno.id, tipo_envio=TipoEnvioEnum.TEXTO, conteudo_bruto="x")
        db.add_all([q1, q2, sub])
        db.flush()
        cor = Correcao(submissao_id=sub.id, nota_ia=65, nota_professor=65, confianca=1, status=StatusCorrecaoEnum.APROVADA,
                       modelo_usado="m", versao_prompt="v")
        db.add(cor)
        db.flush()
        db.add_all([
            CorrecaoCriterio(correcao_id=cor.id, tema_id=q1.id, nota=20, nota_professor=20,
                             justificativa="Trocou o sinal ao isolar x.",
                             pontos=[{"trecho": "x=-3", "tipo": "erro", "comentario": "Passou o 6 com o sinal errado."}]),
            CorrecaoCriterio(correcao_id=cor.id, tema_id=q2.id, nota=45, nota_professor=45, justificativa="Quase tudo certo."),
        ])
        db.commit()


def _aluno_id():
    from app.database import SessionLocal
    from app.models.usuario import Usuario
    with SessionLocal() as db:
        return db.query(Usuario).filter_by(email="exatas@domina.com").one().id


def _login():
    r = client.post("/auth/login", json={"email": "exatas@domina.com", "senha": seed.SENHA})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_erro_vira_exercicio_da_materia_ligado_ao_erro_e_so_uma_vez():
    from app.database import SessionLocal
    from app.models.usuario import ErroAluno, Exercicio
    _montar()
    prompts = []

    def falso(prompt, schema, temperature=0, model=None):
        prompts.append(prompt)
        refs = re.findall(r"^(E\d+)\.", prompt, re.MULTILINE)
        return schema.model_validate({"exercicios": [
            {"erro_ref": r, "titulo": "Raiz de função", "enunciado": "e", "opcoes": ["a", "b", "c", "d"],
             "resposta_correta": 1, "explicacao": "x"} for r in refs]}), "falso"

    original, estudos_mod.gerar_json = estudos_mod.gerar_json, falso
    try:
        aluno = _login()
        r = client.get("/estudos/meu", headers=aluno)
        assert r.status_code == 200, r.text
        itens = r.json()
        assert len(itens) == 1  # so a Q1 (40%) conta; a Q2 (90%) esta acima de 70%
        assert itens[0]["materia"] == "Matemática"
        assert "raiz de f(x)" in itens[0]["motivo"]
        assert "gabarito" not in str(itens[0]).lower() and "resposta_correta" not in itens[0]
        assert "Passou o 6 com o sinal errado" in prompts[0]  # a IA recebe onde ele errou
        # abrir de novo nao gera nada novo nem duplica o erro
        assert client.get("/estudos/meu", headers=aluno).json()[0]["id"] == itens[0]["id"]
        assert len(prompts) == 1
        with SessionLocal() as db:
            erros = db.query(ErroAluno).filter_by(aluno_id=_aluno_id()).all()
            assert len(erros) == 1 and float(erros[0].percentual) == 40.0 and erros[0].gabarito == "x=3"
            assert db.query(Exercicio).filter_by(erro_id=erros[0].id).count() == 1
        # responde (servidor confere) e some da lista
        res = client.post(f"/estudos/exercicios/{itens[0]['id']}/responder", headers=aluno, json={"opcao": 1})
        assert res.status_code == 200 and res.json()["correta"] is True
    finally:
        estudos_mod.gerar_json = original
