"""Correcao da redacao ENEM pelo Gemini nas 5 competencias do INEP.

A nota NAO vai para o aluno aqui: fica PENDENTE ate o professor aprovar (RN-01).
"""
from typing import Literal

from google.genai import types
from pydantic import BaseModel, Field, field_validator

from app.ocr.gemini import gerar

VERSAO_PROMPT = "v2"  # v2: descritores oficiais do INEP por nivel
NOTAS_VALIDAS = {0, 40, 80, 120, 160, 200}  # o ENEM so usa esses niveis por competencia

PROMPT = """Você é um corretor experiente da redação do ENEM, treinado na matriz de referência do INEP.
Corrija a redação abaixo nas 5 competências, escolhendo para cada uma o nível cujo descritor
oficial melhor descreve o texto.

C1 - Domínio da modalidade escrita formal da língua portuguesa
  200: excelente domínio da norma e da escolha de registro; desvios só como excepcionalidade e sem reincidência.
  160: bom domínio, com poucos desvios gramaticais e de convenções da escrita.
  120: domínio mediano, com alguns desvios gramaticais e de convenções da escrita.
   80: domínio insuficiente, com muitos desvios gramaticais, de registro e de convenções.
   40: domínio precário, sistemático, com desvios diversificados e frequentes.
    0: desconhecimento da modalidade escrita formal.

C2 - Compreensão da proposta e desenvolvimento do tema no texto dissertativo-argumentativo
  200: argumentação consistente, repertório sociocultural produtivo e excelente domínio do tipo textual.
  160: argumentação consistente e bom domínio do tipo textual (proposição, argumentação e conclusão).
  120: argumentação previsível e domínio mediano do tipo textual.
   80: cópia dos textos motivadores ou domínio insuficiente do tipo textual.
   40: tangencia o tema ou tem traços constantes de outros tipos textuais.
    0: fuga ao tema ou não atende ao tipo dissertativo-argumentativo.

C3 - Seleção, relação, organização e interpretação de informações, fatos e opiniões em defesa de um ponto de vista
  200: consistentes e organizados, configurando autoria.
  160: organizados, com indícios de autoria.
  120: limitados aos argumentos dos textos motivadores e pouco organizados.
   80: desorganizados ou contraditórios.
   40: pouco relacionados ao tema ou incoerentes, sem ponto de vista.
    0: não relacionados ao tema.

C4 - Mecanismos linguísticos para a construção da argumentação (coesão)
  200: articula bem as partes do texto e tem repertório diversificado de recursos coesivos.
  160: articula as partes com poucas inadequações e repertório diversificado.
  120: articulação mediana, com inadequações, e repertório pouco diversificado.
   80: articulação insuficiente, com muitas inadequações, repertório limitado.
   40: articulação precária.
    0: não articula as informações.

C5 - Proposta de intervenção respeitando os direitos humanos
  Conte os 5 elementos: agente, ação, meio/modo, finalidade e detalhamento (de qualquer um deles).
  200: proposta muito bem elaborada, com os 5 elementos, relacionada ao tema e articulada ao texto.
  160: 4 elementos.  120: 3 elementos.  80: 2 elementos.  40: 1 elemento ou proposta vaga.
    0: sem proposta, ou proposta que desrespeita os direitos humanos.

Como corrigir:
- Avalie como um corretor do INEP: cada competência é independente. Não puxe todas para o meio;
  um texto pode ter 200 numa competência e 120 em outra.
- Só desça de nível quando o problema descrito no nível de baixo realmente aparece no texto.
- A redação foi transcrita de uma foto: "[ilegível]" e palavras estranhas isoladas podem ser falha
  da leitura, não do aluno. Na C1, conte só desvios claros e reincidentes.
- Na justificativa, cite trechos da redação e diga o que faltou para o nível acima.
- "confianca" (0 a 1): o quanto você está seguro da nota total. Use valores baixos se o texto
  estiver incompleto, muito ilegível, perto de fugir do tema ou se ficar entre dois níveis.
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
