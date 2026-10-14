"""Correcao da redacao ENEM pelo Gemini nas 5 competencias do INEP.

A nota NAO vai para o aluno aqui: fica PENDENTE ate o professor aprovar (RN-01).
"""
from typing import Literal

from google.genai import types
from pydantic import BaseModel, Field, field_validator

from app.ocr.gemini import gerar

VERSAO_PROMPT = "v1"
NOTAS_VALIDAS = {0, 40, 80, 120, 160, 200}  # o ENEM so usa esses niveis por competencia

PROMPT = """Você é um corretor experiente da redação do ENEM. Corrija a redação abaixo
segundo a matriz de referência do INEP, nas 5 competências:

C1 - Domínio da modalidade escrita formal da língua portuguesa.
C2 - Compreensão da proposta e desenvolvimento do tema dentro do texto dissertativo-argumentativo,
     com repertório sociocultural.
C3 - Seleção, relação, organização e interpretação de informações e argumentos em defesa de um ponto de vista.
C4 - Conhecimento dos mecanismos linguísticos necessários para a construção da argumentação (coesão).
C5 - Proposta de intervenção para o problema abordado, respeitando os direitos humanos
     (agente, ação, meio/modo, finalidade e detalhamento).

Regras:
- Cada competência recebe exatamente um destes valores: 0, 40, 80, 120, 160 ou 200.
- Na justificativa de cada competência, cite trechos da redação e diga o que faltou para o nível acima.
- A redação foi transcrita de uma foto; "[ilegível]" é falha da leitura, não erro do aluno.
- "confianca" (0 a 1) é o quanto você está seguro da nota total. Use valores baixos se o texto
  estiver incompleto, muito ilegível, fugir do tema ou se a correção for ambígua.
- "feedback_geral": 2 a 4 frases para o aluno sobre o que mais vale a pena melhorar.

Tema proposto: {tema}

Redação:
\"\"\"
{texto}
\"\"\""""


class CompetenciaIA(BaseModel):
    codigo: Literal["C1", "C2", "C3", "C4", "C5"]
    nota: int
    justificativa: str

    @field_validator("nota")
    @classmethod
    def nivel_do_enem(cls, v):
        # arredonda para o nivel valido mais proximo em vez de rejeitar a correcao inteira;
        # no empate (ex.: 60) fica com o menor, para nao inflar a nota
        return min(NOTAS_VALIDAS, key=lambda n: (abs(n - v), n))


class ResultadoIA(BaseModel):
    competencias: list[CompetenciaIA] = Field(min_length=5, max_length=5)
    feedback_geral: str
    confianca: float = Field(ge=0, le=1)

    @field_validator("competencias")
    @classmethod
    def uma_de_cada(cls, v):
        if sorted(c.codigo for c in v) != ["C1", "C2", "C3", "C4", "C5"]:
            raise ValueError("a correcao precisa ter C1..C5, uma vez cada")
        return sorted(v, key=lambda c: c.codigo)


def corrigir(texto: str, tema: str) -> tuple[ResultadoIA, str]:
    # devolve (resultado, modelo_usado). Levanta excecao se o modelo nao devolver JSON valido.
    # ponytail: "confianca" e autoavaliacao do modelo; trocar por medida real
    # (ex.: divergencia entre 2 correcoes) quando houver dados de concordancia com professor
    response, modelo = gerar(
        PROMPT.format(tema=tema, texto=texto),
        types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=ResultadoIA,
        ),
    )
    return ResultadoIA.model_validate_json(response.text), modelo
