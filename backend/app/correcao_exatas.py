"""Correcao de exercicios de materias exatas (matematica, fisica, quimica) pelo Gemini.

Diferente da redacao (app/correcao.py): aqui nao ha rubrica subjetiva nem "pensamento
critico". E so conferir, questao por questao, se a resposta do aluno bate com o gabarito
dado pelo professor -- aceitando formas equivalentes (1/2 = 0,5, x=3 = 3 etc.) -- e explicar
o motivo em 1-2 frases objetivas.
"""
from google.genai import types
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.correcao import NOTAS_VALIDAS, PontoIA
from app.ocr.gemini import gerar, reduzir

VERSAO_PROMPT = "exatas-v1"
MODELO_PRINCIPAL = settings.GEMINI_MODEL

PROMPT = """Você é um corretor de exercícios de {materia}. Confira se as respostas do aluno batem
com o gabarito, questão por questão. Isto NÃO é uma avaliação subjetiva: é uma conferência
lógica e objetiva, sem julgamento de estilo ou argumentação.

Considere a resposta do aluno correta mesmo se estiver em formato diferente do gabarito
(ex.: "1/2" e "0,5" são a mesma resposta; "x = 3" e "3" são a mesma resposta; unidades
equivalentes contam). Considere errada se o valor final for diferente do gabarito, mesmo que
o método usado pareça certo.

Questões e gabarito (código da questão, enunciado, resposta correta):
{questoes}

Respostas do aluno, transcritas do que ele entregou (podem estar fora de ordem ou sem
numeração clara — associe cada trecho à questão correspondente pelo conteúdo):
\"\"\"
{respostas}
\"\"\"

Para cada questão, dê uma nota de 0 a 200: 200 se a resposta final do aluno bate com o
gabarito, 0 se não bate. Só use valores intermediários (40, 80, 120, 160) se a questão tiver
múltiplas partes e o aluno acertou só parte delas. Na justificativa, cite objetivamente a
resposta que o aluno deu e a resposta do gabarito, em 1-2 frases.

"pontos": 1 ou mais pontos concretos para esta questão (um por parte, se a questão tiver
várias partes com resultado diferente), cada um com:
- "trecho": copie literalmente, da transcrição das respostas do aluno acima, o pedaço a que
  esse ponto se refere. Deixe "" se não achar nada que corresponda.
- "tipo": "acerto" se esse pedaço bate com o gabarito, "erro" se não bate.
- "comentario": 1 frase objetiva (o que o aluno respondeu vs. o gabarito, nesse ponto).
{instrucao_caixa}
"confianca" (0 a 1): o quanto você está seguro de ter identificado corretamente a resposta do
aluno para CADA questão (baixa se a letra/transcrição estiver ambígua, incompleta, ou se
alguma questão não foi respondida).

Responda em JSON com esta estrutura, uma entrada por questão, na mesma ordem recebida:
{{
  "questoes": [
    {{"codigo": "Q1", "nota": 200, "justificativa": "...", "pontos": [
      {{"trecho": "...", "tipo": "acerto", "comentario": "..."{exemplo_caixa}}}
    ]}}
  ],
  "confianca": 0.0
}}"""

INSTRUCAO_CAIXA = """
Além disso, a imagem enviada é a prova original do aluno: em CADA ponto, diga também ONDE na
imagem está aquele trecho, com "caixa": {"x": 0.0, "y": 0.0, "largura": 0.0, "altura": 0.0},
todos os valores entre 0 e 1 (frações da largura/altura da imagem inteira; x/y é o canto
superior-esquerdo da caixa). Se não conseguir localizar com confiança, omita "caixa" ou deixe
null -- não invente uma posição.
"""
EXEMPLO_CAIXA = ', "caixa": {"x": 0.1, "y": 0.2, "largura": 0.3, "altura": 0.1}'


class QuestaoCorrigida(BaseModel):
    codigo: str
    nota: float
    justificativa: str
    pontos: list[PontoIA] = Field(default_factory=list)

    @field_validator("nota")
    @classmethod
    def nivel_valido(cls, v):
        # mesma escala discreta da redacao (0..200): arredonda para o nivel mais proximo
        # em vez de rejeitar a correcao inteira por causa de um valor fora da escala
        return min(NOTAS_VALIDAS, key=lambda n: (abs(n - v), n))


class ResultadoExatasIA(BaseModel):
    questoes: list[QuestaoCorrigida]
    confianca: float = Field(ge=0, le=1)


def corrigir(
    respostas_aluno: str,
    materia_nome: str,
    questoes: list[tuple[str, str, str]],
    imagem: tuple[bytes, str] | None = None,
) -> tuple[ResultadoExatasIA, str]:
    # questoes: lista de (codigo, enunciado, resposta_correta), na ordem em que serao exibidas
    # imagem: (bytes, mime_type) da foto original, so quando a resposta foi enviada por foto --
    # nesse caso a IA tambem devolve "caixa" (onde na foto esta cada resposta)
    texto_questoes = "\n".join(
        f"{codigo}) {enunciado}\n   Gabarito: {resposta}" for codigo, enunciado, resposta in questoes
    )
    prompt = PROMPT.format(
        materia=materia_nome,
        questoes=texto_questoes,
        respostas=respostas_aluno,
        instrucao_caixa=INSTRUCAO_CAIXA if imagem else "",
        exemplo_caixa=EXEMPLO_CAIXA if imagem else "",
    )
    if imagem:
        imagem_bytes, mime_type = reduzir(*imagem)
        contents = [types.Part.from_bytes(data=imagem_bytes, mime_type=mime_type), prompt]
    else:
        contents = prompt
    response, modelo = gerar(
        contents,
        types.GenerateContentConfig(
            temperature=0, response_mime_type="application/json", response_schema=ResultadoExatasIA,
        ),
    )
    resultado = ResultadoExatasIA.model_validate_json(response.text)
    esperado = sorted(codigo for codigo, _, _ in questoes)
    if sorted(q.codigo for q in resultado.questoes) != esperado:
        raise ValueError("a IA nao respondeu exatamente as questoes esperadas")
    return resultado, modelo
