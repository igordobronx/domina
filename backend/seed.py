"""Popula o banco com o minimo para a demo. Pode rodar quantas vezes quiser:
o que ja existe e reaproveitado e as senhas sao regravadas.
Suba a API antes (e ela que cria as tabelas).

    python seed.py            (local)
    docker compose exec api python seed.py
"""
from app.auth.security import hash_password
from app.database import SessionLocal
from app.models.enum import (
    PerfilEnum, StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum, TipoMateriaEnum, UsuarioTurmaPapelEnum,
)
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, Escola, Materia, Submissao, Tema, Turma, Usuario, UsuarioTurma,
)
from app.routers.submissoes import _atualizar_dominio

SENHA = "senha123"

# as 5 competencias da redacao do ENEM (INEP); cada uma vira um Tema da materia
COMPETENCIAS_ENEM = [
    ("C1", "Domínio da modalidade escrita formal da língua portuguesa"),
    ("C2", "Compreensão da proposta e aplicação de conceitos no texto dissertativo-argumentativo"),
    ("C3", "Seleção, organização e interpretação de informações e argumentos"),
    ("C4", "Conhecimento dos mecanismos linguísticos da argumentação"),
    ("C5", "Proposta de intervenção respeitando os direitos humanos"),
]

TITULOS_ATIVIDADES = [
    "Redação 1 - desigualdade social no Brasil",
    "Redação 2 - meio ambiente e sustentabilidade",
    "Redação 3 - tecnologia e sociedade",
    "Redação 4 - educação e cidadania",
]

# cada aluno tem um ponto fraco diferente, pra evolucao/recomendacao fazer sentido e ser distinta.
# "aprovadas": atividades (indice em TITULOS_ATIVIDADES) com correcao aprovada, cada uma com as 5 notas.
# "pendente"/"disponivel": so o indice da atividade.
ALUNOS = [
    {
        "nome": "Ana Beatriz Lima", "email": "aluno@domina.com", "fraco": "C4",
        "aprovadas": {
            0: {"C1": 160, "C2": 160, "C3": 160, "C4": 80, "C5": 160},
            1: {"C1": 160, "C2": 160, "C3": 160, "C4": 40, "C5": 160},
        },
        "pendente": 2, "disponivel": 3,
    },
    {
        "nome": "Bruno Costa", "email": "aluno2@domina.com", "fraco": "C3",
        "aprovadas": {
            0: {"C1": 160, "C2": 160, "C3": 80, "C4": 160, "C5": 160},
            2: {"C1": 160, "C2": 160, "C3": 40, "C4": 160, "C5": 160},
        },
        "pendente": 1, "disponivel": 3,
    },
    {
        "nome": "Carla Duarte", "email": "aluno3@domina.com", "fraco": "C5",
        "aprovadas": {
            1: {"C1": 160, "C2": 160, "C3": 160, "C4": 160, "C5": 80},
            3: {"C1": 160, "C2": 160, "C3": 160, "C4": 160, "C5": 40},
        },
        "pendente": 0, "disponivel": 2,
    },
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
    u.nome = nome
    u.senha_hash = hash_password(SENHA)
    return u


def submeter(db, atividade, aluno, aguardando_correcao=True):
    texto = (
        f"Texto de redação de {aluno.nome} sobre '{atividade.titulo}'. "
        "A desigualdade social e o acesso desigual a oportunidades seguem como desafios "
        "centrais no Brasil contemporâneo, exigindo politicas publicas efetivas. "
    ) * 3
    return get_or_create(
        db, Submissao, atividade_id=atividade.id, aluno_id=aluno.id,
        defaults=dict(tipo_envio=TipoEnvioEnum.TEXTO, conteudo_bruto=texto, texto_confirmado=texto),
    )


def aprovar(db, professor, submissao, temas, notas: dict, fraco: str):
    if db.query(Correcao).filter_by(submissao_id=submissao.id).first():
        return  # ja aprovada numa execucao anterior do seed
    total = sum(notas.values())
    correcao = Correcao(
        submissao_id=submissao.id, nota_ia=total, nota_professor=total, confianca=0.92,
        status=StatusCorrecaoEnum.APROVADA, modelo_usado="seed", versao_prompt="seed",
        revisado_por=professor.id,
        feedback=f"Boa estrutura geral. O ponto a desenvolver agora e a competência {fraco}.",
    )
    db.add(correcao)
    db.flush()
    criterios = {}
    for codigo, nota in notas.items():
        c = CorrecaoCriterio(
            correcao_id=correcao.id, tema_id=temas[codigo].id, nota=nota, nota_professor=nota,
            justificativa=f"Nota de exemplo (seed) para {codigo}.",
        )
        db.add(c)
        criterios[codigo] = c
    db.flush()
    _atualizar_dominio(db, submissao.aluno_id, criterios)


def run_seed():
    db = SessionLocal()
    try:
        escola = get_or_create(db, Escola, nome="COLEGIO PREPARA ENEM", defaults=dict(cnpj="12345678000190"))

        professor = usuario(db, escola, "Beto Andrade", "professor@domina.com", PerfilEnum.PROFESSOR)

        turma = get_or_create(db, Turma, escola_id=escola.id, nome="3º Ano A", defaults=dict(ano=2026))
        get_or_create(db, UsuarioTurma, usuario_id=professor.id, turma_id=turma.id,
                      defaults=dict(papel=UsuarioTurmaPapelEnum.PROFESSOR))

        materia = get_or_create(db, Materia, escola_id=escola.id, tipo=TipoMateriaEnum.REDACAO_ENEM,
                                defaults=dict(nome="Redação ENEM"))
        temas = {}
        for codigo, nome in COMPETENCIAS_ENEM:
            temas[codigo] = get_or_create(db, Tema, materia_id=materia.id, habilidade_codigo=codigo,
                                           defaults=dict(nome=nome))

        atividades = [
            get_or_create(db, Atividade, materia_id=materia.id, turma_id=turma.id, titulo=titulo,
                          defaults=dict(tipo=TipoAtividadeEnum.REDACAO))
            for titulo in TITULOS_ATIVIDADES
        ]
        db.flush()

        print("\nseed ok")
        print(f"escola:    {escola.nome}")
        print(f"professor: professor@domina.com / {SENHA}")

        for info in ALUNOS:
            aluno = usuario(db, escola, info["nome"], info["email"], PerfilEnum.ALUNO)
            get_or_create(db, UsuarioTurma, usuario_id=aluno.id, turma_id=turma.id,
                          defaults=dict(papel=UsuarioTurmaPapelEnum.ALUNO))

            for indice, notas in info["aprovadas"].items():
                sub = submeter(db, atividades[indice], aluno)
                aprovar(db, professor, sub, temas, notas, info["fraco"])

            submeter(db, atividades[info["pendente"]], aluno)
            # "disponivel": de proposito nao envia nada nessa atividade

            print(f"aluno:     {info['email']} / {SENHA}  (ponto fraco de propósito: {info['fraco']})")

        db.commit()
        print(f"\nturma:     {turma.nome}  ({len(atividades)} atividades)\n")
    except Exception:
        db.rollback()
        raise  # deixa o erro aparecer inteiro em vez de engolir
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
