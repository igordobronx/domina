"""IA ajudando o PROFESSOR a criar exercicios de pratica: rascunhos sobre um tema e resposta de
exemplo para um discursivo. Nada e salvo aqui -- o professor revisa, edita e so entao publica
(RN-13: exercicio feito pela IA so chega ao aluno depois que o professor aprova).
Mesmo padrao do app/estudos.py: prompt -> JSON tipado, no Haiku (pratica, nao avaliacao).
"""
from typing import Literal

from pydantic import BaseModel, Field

from app.config import settings
from app.llm.claude import gerar_json

PROMPT_SUGERIR = """Você é um professor experiente de {materia}. Crie {quantidade} exercício(s) de prática
para alunos do ensino médio sobre o tema: "{assunto}".
Tipo: {tipo_texto}
{instrucoes}
Regras:
- Seja concreto: apresente uma situação, um trecho, um problema ou um dado, e peça algo sobre ele.
  Evite pergunta teórica genérica.
- Varie os exercícios entre si (não repita a mesma ideia).
- Escreva em português do Brasil, com linguagem clara para o aluno.
{regras_tipo}
Responda em JSON com esta estrutura:
{{
  "exercicios": [
    {{
      "titulo": "título curto",
      "enunciado": "a pergunta completa, com o contexto necessário",
      "alternativas": [{exemplo_alternativas}],
      "resposta_correta": {exemplo_correta},
      "resposta_exemplo": {exemplo_resposta},
      "explicacao": "por que a resposta certa está certa (e, no objetivo, por que as outras não)"
    }}
  ]
}}"""

REGRAS_OBJETIVO = """- Exatamente 4 alternativas, só UMA correta, todas plausíveis.
- "resposta_correta" é o índice (0 a 3) da alternativa certa; varie a posição entre os exercícios.
- "resposta_exemplo" deve ser null."""
REGRAS_DISCURSIVO = """- "alternativas" deve ser uma lista vazia e "resposta_correta" null.
- "resposta_exemplo" é uma resposta modelo, completa e curta, que o aluno usará para comparar com a dele."""

PROMPT_RESPOSTA = """Você é um professor experiente de {materia}. Escreva uma resposta modelo, completa e
curta, para o exercício discursivo abaixo (tema: "{assunto}"). O aluno vai comparar a resposta dele
com esta, então seja claro e mostre o raciocínio. Português do Brasil.

Enunciado:
{enunciado}

Responda em JSON: {{"resposta_exemplo": "..."}}"""


class SugestaoExercicio(BaseModel):
    titulo: str
    enunciado: str
    alternativas: list[str] = []
    resposta_correta: int | None = None
    resposta_exemplo: str | None = None
    explicacao: str = ""


class _RespostaSugestao(BaseModel):
    exercicios: list[SugestaoExercicio]


class _RespostaExemplo(BaseModel):
    resposta_exemplo: str = Field(min_length=1)


def sugerir_exercicios(materia: str, assunto: str, tipo: Literal["OBJETIVO", "DISCURSIVO"],
                       quantidade: int, instrucoes: str | None = None) -> list[SugestaoExercicio]:
    objetivo = tipo == "OBJETIVO"
    prompt = PROMPT_SUGERIR.format(
        materia=materia, quantidade=quantidade, assunto=assunto,
        tipo_texto="objetivo (múltipla escolha)" if objetivo else "discursivo (o aluno escreve a resposta)",
        instrucoes=f"Pedido do professor: {instrucoes}\n" if instrucoes else "",
        regras_tipo=REGRAS_OBJETIVO if objetivo else REGRAS_DISCURSIVO,
        exemplo_alternativas='"A", "B", "C", "D"' if objetivo else "",
        exemplo_correta="0" if objetivo else "null",
        exemplo_resposta="null" if objetivo else '"resposta modelo"',
    )
    resultado, _ = gerar_json(prompt, _RespostaSugestao, model=settings.ANTHROPIC_MODEL_HAIKU)
    exercicios = []
    for e in resultado.exercicios[:quantidade]:
        if objetivo:  # normaliza: o professor ainda revisa, mas o rascunho ja vem num formato valido
            e.alternativas = [a for a in e.alternativas if a.strip()][:6]
            if e.resposta_correta is None or not 0 <= e.resposta_correta < len(e.alternativas):
                e.resposta_correta = 0
            e.resposta_exemplo = None
        else:
            e.alternativas, e.resposta_correta = [], None
        exercicios.append(e)
    return exercicios


def sugerir_resposta_exemplo(materia: str, assunto: str, enunciado: str) -> str:
    resultado, _ = gerar_json(
        PROMPT_RESPOSTA.format(materia=materia, assunto=assunto or "livre", enunciado=enunciado),
        _RespostaExemplo, model=settings.ANTHROPIC_MODEL_HAIKU,
    )
    return resultado.resposta_exemplo
