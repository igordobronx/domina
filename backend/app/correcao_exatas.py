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
from app.ocr.gemini import LADO_EXATAS, gerar, reduzir

VERSAO_PROMPT = "exatas-v3"  # v3: leitura do desenho antes da nota; substrato diferente do enunciado = parcial
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

{instrucao_figuras}{instrucao_foto}Respostas do aluno, transcritas do que ele entregou (podem estar fora de ordem ou sem
numeração clara — associe cada trecho à questão correspondente pelo conteúdo):
\"\"\"
{respostas}
\"\"\"

Antes da nota, escreva em "leitura" o que o aluno entregou naquela questão, sem julgar: se
for desenho, o composto/estrutura (nome, nº de carbonos, grupos funcionais, posição da
ligação múltipla) ou os passos do mecanismo; se for texto/número, a resposta final. Só depois
dê a nota com base na leitura. Se a leitura mostra que o aluno partiu de um composto ou dado
DIFERENTE do enunciado mas raciocinou de forma coerente a partir dele, NÃO dê 0: dê nota
parcial (40 a 80), diga isso na justificativa e baixe a "confianca", para o professor decidir.

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
    {{"codigo": "Q1", "leitura": "...", "nota": 200, "justificativa": "...", "pontos": [
      {{"trecho": "...", "tipo": "acerto", "comentario": "..."{exemplo_caixa}}}
    ]}}
  ],
  "confianca": 0.0
}}"""

INSTRUCAO_FIGURAS = """As figuras das questões (estruturas, gráficos, esquemas) vêm ANTES deste texto, cada uma
identificada pelo código da questão. Elas fazem parte do enunciado: use-as para entender o que
a questão pede e conferir a resposta do aluno.

"""

INSTRUCAO_FOTO = """A foto da prova do aluno acompanha este pedido e é a FONTE PRINCIPAL. A transcrição abaixo
pode ter ficado sem os desenhos (estruturas químicas, mecanismos com setas, gráficos, esquemas,
tabelas) e até sem colunas inteiras da folha. Leia a foto inteira, todas as colunas, e avalie
também o que o aluno DESENHOU: uma estrutura ou um mecanismo desenhado É resposta.
Nunca diga que uma resposta está em branco só porque a transcrição não a traz: olhe a foto antes.
Só dê 0 por falta de resposta se a foto realmente não mostrar nada para aquela questão (e diga
isso na justificativa). Se o desenho estiver pouco legível para avaliar, diga isso e baixe
a "confianca" em vez de dar 0 por omissão.

"""

INSTRUCAO_FOLHAS = """A prova do aluno tem {n} fotos (folhas do mesmo trabalho), na ordem em que ele as enviou:
"folha 1", "folha 2"... Trate-as como uma prova só: a resposta de uma questão pode estar em
qualquer folha. Em cada "caixa" inclua também "pagina": a folha em que o trecho está, contando
de 0 (folha 1 = 0, folha 2 = 1...); x, y, largura e altura valem para essa folha.
"""

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
    leitura: str = ""  # antes da nota: o schema respeita a ordem, entao o modelo le primeiro
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
    imagem: tuple[bytes, str] | list[tuple[bytes, str]] | None = None,
    figuras: dict[str, tuple[bytes, str]] | None = None,
) -> tuple[ResultadoExatasIA, str]:
    # questoes: lista de (codigo, enunciado, resposta_correta), na ordem em que serao exibidas
    # imagem: (bytes, mime_type) da foto original, so quando a resposta foi enviada por foto --
    # nesse caso a IA tambem devolve "caixa" (onde na foto esta cada resposta)
    # figuras: {codigo da questao: (bytes, mime_type)} anexadas pelo professor ao enunciado
    imagens = [imagem] if isinstance(imagem, tuple) else list(imagem or [])
    texto_questoes = "\n".join(
        f"{codigo}) {enunciado}\n   Gabarito: {resposta}" for codigo, enunciado, resposta in questoes
    )
    prompt = PROMPT.format(
        materia=materia_nome,
        questoes=texto_questoes,
        respostas=respostas_aluno,
        instrucao_figuras=INSTRUCAO_FIGURAS if figuras else "",
        instrucao_foto=(INSTRUCAO_FOLHAS.format(n=len(imagens)) if len(imagens) > 1 else "") + (INSTRUCAO_FOTO if imagens else ""),
        instrucao_caixa=INSTRUCAO_CAIXA if imagens else "",
        exemplo_caixa=EXEMPLO_CAIXA if imagens else "",
    )
    partes = []
    for codigo, figura in (figuras or {}).items():
        figura_bytes, figura_mime = reduzir(*figura)
        partes += [f"Figura da questão {codigo}:", types.Part.from_bytes(data=figura_bytes, mime_type=figura_mime)]
    for n, foto in enumerate(imagens, start=1):
        imagem_bytes, mime_type = reduzir(*foto, LADO_EXATAS)
        partes += [f"Prova do aluno (folha {n}):" if len(imagens) > 1 else "Prova do aluno (foto):",
                   types.Part.from_bytes(data=imagem_bytes, mime_type=mime_type)]
    contents = [*partes, prompt] if partes else prompt
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
    for q in resultado.questoes:
        if q.leitura:
            q.justificativa = f"Leitura da IA: {q.leitura}\n{q.justificativa}"
    return resultado, modelo
