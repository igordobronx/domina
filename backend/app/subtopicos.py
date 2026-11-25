"""Subtopico de cada questao de uma atividade (ex.: "Equacao do 1o grau"): o professor escreve, e o que
ficar em branco a IA identifica pelo enunciado (um chamado so, no Haiku). Se a IA falhar, fica sem
subtopico e a questao so nao entra na lista por subtopico da evolucao do aluno."""
import logging

from pydantic import BaseModel

from app.config import settings
from app.ia import registro
from app.llm.claude import gerar_json

log = logging.getLogger(__name__)

PROMPT = """Você é professor de {materia}. A atividade "{titulo}" tem várias questões, e cada uma pode
ser de um assunto diferente. Para CADA questão, diga o SUBTOPICO: o assunto geral do conteúdo que ela
treina, como aparece no índice de um livro didático (1 a 4 palavras, em português). Não use a operação
ou o detalhe da questão: "união" e "interseção" são "Conjuntos"; "2x + 3 = 7" é "Equação do 1º grau";
"Dom Pedro I e a Independência" é "Independência do Brasil".
{existentes}Questões (enunciado e resposta esperada):
{questoes}

Questões do mesmo assunto devem ter exatamente o mesmo nome. Se ficar em dúvida entre dois assuntos,
escolha o que a resposta esperada mais exige.
Responda em JSON: {{"subtopicos": ["...", "..."]}} com exatamente {n} itens, na mesma ordem."""

EXISTENTES = """Subtópicos que esta matéria já usa (REUSE o nome exato quando a questão for desse assunto,
só crie um novo se não couber em nenhum): {lista}.
"""


class _Subtopicos(BaseModel):
    subtopicos: list[str]


def identificar(materia: str, enunciados: list[str], titulo: str = "", respostas: list[str] | None = None,
                existentes: list[str] | None = None) -> list[str | None]:
    """Um subtopico por enunciado; None onde nao deu."""
    vazio: list[str | None] = [None] * len(enunciados)
    if not enunciados or not settings.ANTHROPIC_API_KEY:
        return vazio
    try:
        respostas = respostas or [""] * len(enunciados)
        texto = "\n".join(f"{i}) {e[:600]}\n   Resposta esperada: {(r or '(não informada)')[:300]}"
                          for i, (e, r) in enumerate(zip(enunciados, respostas), start=1))
        with registro.tarefa("subtopico_da_questao"):
            r, _ = gerar_json(PROMPT.format(materia=materia, titulo=titulo or "sem título", questoes=texto, n=len(enunciados),
                                         existentes=EXISTENTES.format(lista=", ".join(existentes[:40])) if existentes else ""),
                              _Subtopicos, model=settings.ANTHROPIC_MODEL_HAIKU)
        if len(r.subtopicos) != len(enunciados):
            return vazio
        return [(s.strip()[:150] or None) for s in r.subtopicos]
    except Exception:  # a atividade nao pode deixar de ser criada por causa disso
        log.exception("nao deu para identificar os subtopicos")
        return vazio


def completar(materia: str, questoes, titulo: str = "", existentes: list[str] | None = None) -> None:
    """Preenche `subtopico` das QuestaoInput que vieram em branco."""
    faltam = [q for q in questoes if not (q.subtopico or "").strip()]
    novos = identificar(materia, [q.enunciado for q in faltam], titulo, [q.resposta_correta for q in faltam], existentes)
    for q, s in zip(faltam, novos):
        q.subtopico = s


def usados(db, materia_id) -> list[str]:
    """Subtopicos ja usados nesta materia (a IA reaproveita o nome, para somar certo na evolucao)."""
    from app.models.usuario import Tema
    return sorted({t for (t,) in db.query(Tema.subtopico).filter(Tema.materia_id == materia_id, Tema.subtopico.isnot(None))})
