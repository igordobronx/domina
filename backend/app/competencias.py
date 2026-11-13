"""As 5 competencias da redacao do ENEM (INEP). Cada uma vira um Tema da materia de redacao: sem elas
a correcao nao tem o que avaliar. Toda materia de redacao precisa ter as 5, nao importa por onde nasceu."""
from sqlalchemy.orm import Session

from app.models.usuario import Materia, Tema

COMPETENCIAS_ENEM = [
    ("C1", "Domínio da modalidade escrita formal da língua portuguesa"),
    ("C2", "Compreensão da proposta e aplicação de conceitos no texto dissertativo-argumentativo"),
    ("C3", "Seleção, organização e interpretação de informações e argumentos"),
    ("C4", "Conhecimento dos mecanismos linguísticos da argumentação"),
    ("C5", "Proposta de intervenção respeitando os direitos humanos"),
]


def garantir_competencias(db: Session, materia: Materia) -> None:
    """Cria (sem commit) as competencias que faltam na materia. Repetir nao duplica."""
    tem = {c for (c,) in db.query(Tema.habilidade_codigo).filter_by(materia_id=materia.id, atividade_id=None)}
    for codigo, nome in COMPETENCIAS_ENEM:
        if codigo not in tem:
            db.add(Tema(materia_id=materia.id, habilidade_codigo=codigo, nome=nome))
    db.flush()
