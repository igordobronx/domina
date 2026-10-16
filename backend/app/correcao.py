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
Você vai corrigir a redação abaixo em DUAS ETAPAS. Não pule direto para a nota.

=== ETAPA 1 — EXTRAÇÃO DE EVIDÊNCIAS (faça isso antes de pontuar) ===
Para cada competência, liste objetivamente o que você observa no texto, com trecho citado e
número da linha quando possível. Não avalie ainda, só levante os fatos:
- C1: erros gramaticais/de convenção que encontrou (liste cada um, com trecho). Separe:
  (a) palavras ou trechos RISCADOS pelo próprio candidato com um traço e substituídos por
      outra palavra/frase — isso é uma AUTOCORREÇÃO EXPLICITAMENTE PERMITIDA pelas instruções
      oficiais da folha de redação do ENEM ("No caso de erro, risque... e escreva o respectivo
      substitutivo"). NÃO conte isso como erro de C1. Avalie apenas a versão final, já corrigida,
      do texto.
  (b) erros reais que permanecem no texto final (concordância, regência, ortografia, pontuação).
- C2: qual repertório sociocultural o texto usa (filme, livro, dado histórico, citação, lei,
  evento) e se ele é usado de forma PRODUTIVA (articulado ao argumento) ou apenas DECORATIVA
  (citado e abandonado).
- C3: qual é a tese, quais são os argumentos de cada parágrafo de desenvolvimento, e se a
  progressão entre eles é lógica ou se os parágrafos se repetem/contradizem.
- C4: liste os conectivos usados entre parágrafos e entre frases-chave. Avalie a coesão
  SOMENTE pelos conectivos e pela retomada referencial (pronomes, sinônimos). NÃO avalie
  caligrafia, rasuras ou organização visual aqui — isso não é C4.
- C5: identifique explicitamente, com citação: agente, ação, meio/modo, finalidade, e se há
  detalhamento de algum desses elementos. Diga quais dos 5 estão presentes e quais faltam.

=== ETAPA 2 — CLASSIFICAÇÃO POR NÍVEL ===
Só agora, com base na extração acima, escolha o nível de cada competência.

C1 - Domínio da modalidade escrita formal da língua portuguesa
  200: excelente domínio; desvios só como excepcionalidade e sem reincidência do mesmo tipo de erro.
  160: bom domínio, com poucos desvios gramaticais e de convenções da escrita.
  120: domínio mediano, com alguns desvios gramaticais e de convenções da escrita.
   80: domínio insuficiente, com muitos desvios gramaticais, de registro e de convenções.
   40: domínio precário, sistemático, com desvios diversificados e frequentes.
    0: desconhecimento da modalidade escrita formal.
  REGRA DE CALIBRAÇÃO: 2-3 ocorrências do MESMO tipo de erro (ex: concordância de gênero) em
  um texto de 30 linhas, sem outros problemas de registro/estrutura, normalmente ainda fica em
  160 — não desça para 120 só por reincidência de um único tipo de erro se o resto do domínio
  (sintaxe, registro formal, pontuação) for sólido. Reserve 120 ou menos para quando há VÁRIOS
  TIPOS diferentes de desvio (gramática + registro + pontuação + ortografia) coexistindo.

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
  LEMBRETE: avalie só os conectivos e a retomada referencial listados na Etapa 1. Rasura e
  caligrafia são questões de legibilidade da transcrição, não de coesão textual.

C5 - Proposta de intervenção respeitando os direitos humanos
  Conte os 5 elementos listados na Etapa 1: agente, ação, meio/modo, finalidade e detalhamento
  (de qualquer um dos outros quatro).
  200: proposta muito bem elaborada, com os 5 elementos, relacionada ao tema e articulada ao texto.
  160: 4 elementos.  120: 3 elementos.  80: 2 elementos.  40: 1 elemento ou proposta vaga.
    0: sem proposta, ou proposta que desrespeita os direitos humanos.

=== REGRAS GERAIS ===
- Cada competência é INDEPENDENTE. Não puxe todas para o meio por insegurança — é normal e
  esperado que um texto tenha, por exemplo, 200 em C2 e 160 em C1 na mesma correção.
  Competências diferentes avaliam coisas diferentes; não deixe a impressão geral do texto
  "vazar" para competências que ela não mede.
- Só desça de nível quando o PROBLEMA ESPECÍFICO descrito no nível de baixo realmente aparece
  no texto, com evidência citada na Etapa 1. Nunca desça "por precaução" ou "para ficar seguro".
  Se a evidência coletada na Etapa 1 só sustenta um problema leve, mantenha o nível alto mesmo
  que o texto não seja perfeito.
- A redação pode ter sido transcrita de uma foto: "[ilegível]" e palavras estranhas isoladas
  podem ser falha da leitura/OCR, não do aluno. Na C1, não conte esses casos como desvio.
- Trechos riscados pelo próprio candidato (ver regra de C1 acima) nunca contam contra nenhuma
  competência — são a versão final sendo construída, não um erro mantido.
- Na justificativa de cada competência, cite pelo menos um trecho da redação e diga
  explicitamente o que faltaria para alcançar o nível imediatamente acima.
- "confianca" (0 a 1): o quanto você está seguro da nota total. Use valores baixos se o texto
  estiver incompleto, muito ilegível, perto de fugir do tema, ou se alguma competência ficou
  genuinamente no limiar entre dois níveis.
- "feedback_geral": 2 a 4 frases para o aluno sobre o que mais vale a pena melhorar.

Responda em JSON com esta estrutura:
{{
  "competencias": [
    {{"codigo": "C1", "analise": "...", "nota": 0, "justificativa": "..."}},
    {{"codigo": "C2", "analise": "...", "nota": 0, "justificativa": "..."}},
    {{"codigo": "C3", "analise": "...", "nota": 0, "justificativa": "..."}},
    {{"codigo": "C4", "analise": "...", "nota": 0, "justificativa": "..."}},
    {{"codigo": "C5", "analise": "...", "nota": 0, "justificativa": "..."}}
  ],
  "confianca": 0.0,
  "feedback_geral": "..."
}}

Tema proposto: {tema}

Redação:
\"\"\"
{texto}
\"\"\""""

class CompetenciaIA(BaseModel):
    codigo: Literal["C1", "C2", "C3", "C4", "C5"]
    analise: str  # evidencias/raciocinio da Etapa 1, ANTES da nota -- forca pensar antes de decidir
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
