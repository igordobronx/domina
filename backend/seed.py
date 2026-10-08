"""Popula o banco com o minimo para a demo. Pode rodar quantas vezes quiser:
o que ja existe e reaproveitado e as senhas sao regravadas.
Suba a API antes (e ela que cria as tabelas).

    python seed.py            (local)
    docker compose exec api python seed.py
"""
from app.auth.security import hash_password
from app.database import SessionLocal
from app.models.enum import PerfilEnum, TipoAtividadeEnum, TipoMateriaEnum, UsuarioTurmaPapelEnum
from app.models.usuario import Atividade, Escola, Materia, Tema, Turma, Usuario, UsuarioTurma

SENHA = "senha123"

# as 5 competencias da redacao do ENEM (INEP); cada uma vira um Tema da materia
COMPETENCIAS_ENEM = [
    ("C1", "Domínio da modalidade escrita formal da língua portuguesa"),
    ("C2", "Compreensão da proposta e aplicação de conceitos no texto dissertativo-argumentativo"),
    ("C3", "Seleção, organização e interpretação de informações e argumentos"),
    ("C4", "Conhecimento dos mecanismos linguísticos da argumentação"),
    ("C5", "Proposta de intervenção respeitando os direitos humanos"),
]


def get_or_create(db, model, defaults=None, **filtro):
    obj = db.query(model).filter_by(**filtro).first()
    if obj is None:
        obj = model(**filtro, **(defaults or {}))
        db.add(obj)
        db.flush()
    return obj


def usuario(db, escola, nome, email, perfil):
    u = get_or_create(db, Usuario, email=email,
                      defaults=dict(escola_id=escola.id, nome=nome, perfil=perfil, senha_hash=""))
    u.senha_hash = hash_password(SENHA)
    return u


def run_seed():
    db = SessionLocal()
    try:
        escola = get_or_create(db, Escola, nome="COLEGIO PREPARA ENEM", defaults=dict(cnpj="12345678000190"))

        professor = usuario(db, escola, "professor beto", "professor@domina.com", PerfilEnum.PROFESSOR)
        aluno = usuario(db, escola, "aluna ana", "aluno@domina.com", PerfilEnum.ALUNO)

        turma = get_or_create(db, Turma, escola_id=escola.id, nome="3º Ano A", defaults=dict(ano=2026))
        get_or_create(db, UsuarioTurma, usuario_id=professor.id, turma_id=turma.id,
                      defaults=dict(papel=UsuarioTurmaPapelEnum.PROFESSOR))
        get_or_create(db, UsuarioTurma, usuario_id=aluno.id, turma_id=turma.id,
                      defaults=dict(papel=UsuarioTurmaPapelEnum.ALUNO))

        materia = get_or_create(db, Materia, escola_id=escola.id, tipo=TipoMateriaEnum.REDACAO_ENEM,
                                defaults=dict(nome="Redação ENEM"))
        for codigo, nome in COMPETENCIAS_ENEM:
            get_or_create(db, Tema, materia_id=materia.id, habilidade_codigo=codigo, defaults=dict(nome=nome))

        atividade = get_or_create(db, Atividade, materia_id=materia.id, turma_id=turma.id,
                                  titulo="Redação 1 - tema livre", defaults=dict(tipo=TipoAtividadeEnum.REDACAO))
        db.commit()

        print("\nseed ok")
        print(f"escola:       {escola.nome}")
        print(f"professor:    professor@domina.com / {SENHA}")
        print(f"aluno:        aluno@domina.com / {SENHA}")
        print(f"atividade_id: {atividade.id}  (use no envio de redação)\n")
    except Exception:
        db.rollback()
        raise  # deixa o erro aparecer inteiro em vez de engolir
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
