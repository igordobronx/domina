"""Onde o aluno erra em exatas. Le as correcoes APROVADAS e guarda cada questao em que ele ficou
abaixo de 80% do valor dela. Idempotente (uma linha por questao); chamado na aprovacao e antes de
montar o plano de estudo (assim tambem pega correcoes antigas e as objetivas, aprovadas na hora)."""
from sqlalchemy.orm import Session

from app.models.enum import StatusCorrecaoEnum
from app.models.usuario import Atividade, Correcao, CorrecaoCriterio, ErroAluno, Materia, Submissao, Tema
from app.routers.submissoes import MATERIAS_EXATAS

LIMITE_ERRO = 80  # % da questao: abaixo disso conta como erro


def _detalhe(c: CorrecaoCriterio) -> str:
    erros = [p.get("comentario", "") for p in (c.pontos or []) if p.get("tipo") == "erro" and p.get("comentario")]
    return " ".join([c.justificativa.strip(), *erros]).strip()


def registrar_erros(db: Session, aluno_id) -> int:
    """Grava (sem commit) os erros novos do aluno. Devolve quantos criou."""
    ja = {r[0] for r in db.query(ErroAluno.criterio_id).filter_by(aluno_id=aluno_id)}
    linhas = (
        db.query(CorrecaoCriterio, Correcao, Atividade, Materia, Tema)
        .join(Correcao, Correcao.id == CorrecaoCriterio.correcao_id)
        .join(Submissao, Submissao.id == Correcao.submissao_id)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .join(Materia, Materia.id == Atividade.materia_id)
        .join(Tema, Tema.id == CorrecaoCriterio.tema_id)
        .filter(Submissao.aluno_id == aluno_id, Correcao.status == StatusCorrecaoEnum.APROVADA,
                Materia.tipo.in_(MATERIAS_EXATAS))
        .all()
    )
    por_correcao: dict = {}
    for c, cor, *_ in linhas:
        por_correcao[cor.id] = por_correcao.get(cor.id, 0) + 1
    novos = 0
    for c, cor, ativ, mat, tema in linhas:
        if c.id in ja:
            continue
        valor = float(ativ.valor_total or 1000) / por_correcao[cor.id]
        nota = float(c.nota_professor if c.nota_professor is not None else c.nota)
        pct = nota / valor * 100 if valor else 0
        if pct >= LIMITE_ERRO:
            continue
        db.add(ErroAluno(
            aluno_id=aluno_id, materia_id=mat.id, atividade_id=ativ.id, correcao_id=cor.id, criterio_id=c.id,
            enunciado=tema.nome, gabarito=tema.resposta_correta, nota=round(nota, 2), valor=round(valor, 2),
            percentual=round(pct, 2), detalhe=_detalhe(c),
        ))
        novos += 1
    db.flush()
    return novos
