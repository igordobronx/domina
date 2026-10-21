"""Correcao da redacao ENEM pelo Gemini nas 5 competencias do INEP.

A nota fica PENDENTE ate o professor aprovar; o STATUS "APROVADA" (nao a visibilidade pro
aluno) e o que muda aqui -- o aluno pode ver a nota da IA antes disso, mas so como provisoria
(ver _pode_ver_correcao em app/routers/submissoes.py).
"""
from typing import Literal

from google.genai import types
from pydantic import BaseModel, Field, field_validator

from app.ocr.gemini import gerar

VERSAO_PROMPT = "v14"  # v12 + C2 com piso 160 (repertorio externo legitimo e pertinente); uma correcao so
NOTAS_VALIDAS = {0, 40, 80, 120, 160, 200}  # cada corretor do ENEM so usa esses niveis por competencia

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
  (b) erros reais que permanecem no texto final (concordância, regência, ortografia, acentuação,
      pontuação, estrutura sintática). LISTE CADA UM com o trecho exato e no fim escreva a contagem:
      "desvios gramaticais/convenção: N; falhas de estrutura sintática: M". Não conte como erro
      escolhas estilísticas aceitas na norma culta nem variações de pontuação opcionais.
      Só liste o que você tem CERTEZA que é erro: se ao analisar você concluir que a forma está
      correta ou é aceitável, NÃO liste e NÃO conte. Caracteres estranhos dentro de uma palavra
      (ex.: "inüuência" por "influência", "ﬁ", "�") são falha de digitalização do texto, não do
      candidato: ignore. Erro de conteúdo (citação ou autor duvidoso) não é C1.
- C2: qual repertório sociocultural EXTERNO o texto usa (filme, livro, dado histórico, citação, lei,
  evento; informações tiradas só dos textos motivadores não contam como repertório externo) e, para CADA um, verifique os 3 requisitos, dizendo sim/não com o motivo:
  (1) LEGITIMADO: tem respaldo numa área do conhecimento reconhecida (ciência, filosofia,
      literatura, história, sociologia, artes etc.) e fonte/autoria identificável; não é inventado
      nem genérico ("estudos mostram", "especialistas dizem").
  (2) PERTINENTE: tem relação direta com o TEMA proposto, não só com o assunto geral.
  (3) PRODUTIVO: o texto explica o que o repertório tem a ver com o argumento; não é citado e
      abandonado (decorativo).
- C3: qual é a tese, quais são os argumentos de cada parágrafo de desenvolvimento, e se a
  progressão entre eles é lógica ou se os parágrafos se repetem/contradizem.
- C4: liste os conectivos usados entre parágrafos e entre frases-chave. Avalie a coesão
  SOMENTE pelos conectivos e pela retomada referencial (pronomes, sinônimos). Para cada
  conectivo, diga o sentido que ele tem no trecho (adição, oposição, conclusão, causa...) e se
  está correto, aponte os que se repetem e diga com que palavra começa cada parágrafo. NÃO avalie
  caligrafia, rasuras ou organização visual aqui — isso não é C4.
- C5: identifique explicitamente, com citação: agente, ação, meio/modo, finalidade, e se há
  detalhamento de algum desses elementos. Marque cada um dos 5 como PRESENTE (com o trecho) ou
  AUSENTE, e diga se a proposta respeita os direitos humanos.

=== ETAPA 2 — CLASSIFICAÇÃO POR NÍVEL ===
Só agora, com base na extração acima, escolha o nível de cada competência.

C1 - Domínio da modalidade escrita formal da língua portuguesa
  200: excelente domínio; desvios só como excepcionalidade e sem reincidência do mesmo tipo de erro.
  160: bom domínio, com poucos desvios gramaticais e de convenções da escrita.
  120: domínio mediano, com alguns desvios gramaticais e de convenções da escrita.
   80: domínio insuficiente, com muitos desvios gramaticais, de registro e de convenções.
   40: domínio precário, sistemático, com desvios diversificados e frequentes.
    0: desconhecimento da modalidade escrita formal.
  REGRA DE CONTAGEM (como o corretor humano faz), usando a contagem da Etapa 1:
    200: no máximo 1 falha de estrutura sintática e no máximo 2 desvios, que precisam ser de
         TIPOS DIFERENTES: o mesmo desvio repetido (ex.: 2 erros de crase) já é reincidência e
         tira o 200 (nota máxima 160). Na Etapa 1, registre o TIPO de cada desvio. 200 NÃO exige texto
         perfeito: redações nota 1000 reais costumam ter 1 ou 2 desvios pontuais.
    160: até 3 falhas de estrutura sintática e até 5 desvios. Este é o nível MAIS COMUM em redações
         boas: texto com alguns deslizes de concordância, crase, pontuação ou acentuação, mas
         que se lê sem dificuldade, é 160, não 120.
    120: só quando há 6 a 9 desvios, ou estrutura sintática claramente irregular em vários
         períodos, ou desvios de registro. Poucos deslizes pontuais NÃO justificam 120.
     80: estrutura sintática deficiente OU muitos desvios (10 ou mais) e problemas de registro.
     40: estrutura sintática deficitária, com desvios diversificados e frequentes em quase todo o texto.
  FALHA DE ESTRUTURA SINTÁTICA é só período realmente quebrado: frase incompleta, sem verbo ou
  sem sentido, fragmento solto, junção de orações sem ligação. Vírgula mal colocada, regência ou
  concordância NÃO são falha de estrutura: contam como desvio comum.
  Antes de dar a nota, some os desvios da Etapa 1 e escolha o nível pela faixa da contagem.
  A nota da C1 tem que bater com a contagem: não dê 120 para um texto com 3 desvios, e não dê
  200 para um texto com 8. Na dúvida entre 120 e 160, e a contagem for 5 ou menos, dê 160.

C2 - Compreensão da proposta e desenvolvimento do tema no texto dissertativo-argumentativo
  200: argumentação consistente, a partir de um repertório sociocultural LEGÍTIMO, PERTINENTE e
       PRODUTIVO (os 3 requisitos da Etapa 1), com excelente domínio do tipo textual.
  160: argumentação consistente, a partir de um repertório LEGÍTIMO e PERTINENTE, mas que pode não ser
       totalmente produtivo, com bom domínio do tipo textual (proposição, argumentação e conclusão).
  120: desenvolve o tema limitando-se aos textos motivadores, OU apresenta repertório legítimo mas sem
       produtividade ou sem pertinência, com domínio previsível da estrutura do texto.
   80: cópia de trechos dos textos motivadores ou domínio insuficiente do tipo textual.
   40: tangencia o tema ou tem apenas traços do texto dissertativo-argumentativo.
    0: fuga total ao tema ou não atende ao tipo dissertativo-argumentativo.
  LIMITE: sem pelo menos UM repertório EXTERNO (que não venha dos textos motivadores) que seja
  legítimo e pertinente ao tema, a C2 NÃO passa de 120. Usar só informações dos textos motivadores
  conta como sem repertório. PISO: se há pelo menos UM repertório externo legítimo e pertinente ao
  tema, a C2 é no mínimo 160, mesmo que ele seja pouco aprofundado; 120 fica só para quem não
  tem repertório externo pertinente. A produtividade separa o 160 do 200: repertório ligado ao
  argumento (o texto explica o que ele prova) em pelo menos um parágrafo de desenvolvimento = 200;
  repertório só citado e abandonado = 160.

C3 - Seleção, relação, organização e interpretação de informações, fatos e opiniões em defesa de um ponto de vista
  (descritores oficiais do INEP)
  200: informações, fatos e opiniões relacionados ao tema, de forma consistente e organizada,
       configurando AUTORIA: os argumentos estão organizados e relacionados de forma consistente
       com o ponto de vista e com o tema, mostrando independência de pensamento.
  160: informações, fatos e opiniões relacionados ao tema, de forma organizada, com INDÍCIOS de
       autoria: os argumentos, embora ainda possam ser previsíveis, estão organizados e
       relacionados de forma consistente ao ponto de vista e ao tema.
  120: informações, fatos e opiniões relacionados ao tema, mas limitados aos argumentos dos textos
       motivadores e pouco organizados, ou seja, em defesa de um ponto de vista, mas sem projeto claro.
   80: relacionados ao tema, mas desorganizados ou contraditórios e limitados aos argumentos dos
       textos motivadores.
   40: pouco relacionados ao tema ou incoerentes, sem defesa de um ponto de vista.
    0: não relacionados ao tema.
  COMO DIFERENCIAR 160 DE 200: 160 é o nível MAIS COMUM da C3, inclusive em redações boas, bem
  organizadas e com repertório. Argumento previsível, mas organizado e ligado à tese, é 160.
  200 é raro: só quando os argumentos vão além do previsível, com explicação própria, causa e
  consequência ou exemplo que mostrem posicionamento do autor, em TODOS os parágrafos de
  desenvolvimento, sem trecho apenas afirmado. Organização boa, repertório legítimo ou tese clara,
  sozinhos, são 160. Argumentos que só repetem os textos motivadores são 120 ou menos.
  Na dúvida entre 160 e 200, dê 160.

C4 - Mecanismos linguísticos para a construção da argumentação (coesão)
  200: articula bem as partes do texto e tem repertório diversificado de recursos coesivos.
  160: articula as partes com poucas inadequações e repertório diversificado.
  120: articulação mediana, com inadequações, e repertório pouco diversificado.
   80: articulação insuficiente, com muitas inadequações, repertório limitado.
   40: articulação precária.
    0: não articula as informações.
  200 = PELO MENOS 2 conectivos DIFERENTES (sem repetir o mesmo conectivo), todos usados com o
  SENTIDO CORRETO (ex.: "portanto" só para conclusão, "contudo" só para oposição), e com um
  conectivo no INÍCIO de cada parágrafo (do segundo ao último), ligando-o ao anterior. Parágrafo
  que começa sem conectivo, repetição do mesmo conectivo ou conectivo com sentido errado
  impede o 200. Não exija conectivos "mais complexos" ou "mais
  sofisticados": isso não é critério do INEP.
  LEMBRETE: avalie só os conectivos e a retomada referencial listados na Etapa 1. Rasura e
  caligrafia são questões de legibilidade da transcrição, não de coesão textual.

C5 - Proposta de intervenção respeitando os direitos humanos
  Conte os 5 elementos listados na Etapa 1: agente, ação, meio/modo, finalidade e detalhamento
  (de qualquer um dos outros quatro). DETALHAMENTO = uma informação a mais sobre UM dos quatro
  (ex.: explicar quem é o agente, exemplificar a ação, dizer como o meio funciona). Basta UM
  detalhamento para contar o 5º elemento; não exija mais detalhes, órgãos novos, prazos ou
  avaliação de resultados.
  200: SOMENTE com uma proposta de intervenção que tenha os 5 elementos (agente, ação, modo/meio,
       efeito/finalidade e detalhamento), todos respeitando os direitos humanos, relacionada ao
       tema e articulada ao texto. Faltou qualquer elemento = não é 200.
  160: 4 elementos.  120: 3 elementos.  80: 2 elementos.  40: 1 elemento ou proposta vaga.
  A nota segue a CONTAGEM: proposta incompleta perde só os elementos que faltam. Uma proposta
  com 2 ou 3 elementos vale 80 ou 120, nunca 0. Zero só sem proposta ou com desrespeito aos
  direitos humanos.
    0: sem proposta, ou proposta que desrespeita os direitos humanos.

=== REGRAS GERAIS ===
- Cada competência é INDEPENDENTE. Não puxe todas para o meio por insegurança — é normal e
  esperado que um texto tenha, por exemplo, 200 em C2 e 160 em C1 na mesma correção.
  Competências diferentes avaliam coisas diferentes; não deixe a impressão geral do texto
  "vazar" para competências que ela não mede.
- Só desça de nível quando o PROBLEMA ESPECÍFICO descrito no nível de baixo realmente aparece
  no texto, com evidência citada na Etapa 1. Nunca desça "por precaução" ou "para ficar seguro".
  Se a evidência coletada na Etapa 1 só sustenta um problema leve, mantenha o nível alto mesmo
  que o texto não seja perfeito. Vale o mesmo no sentido contrário: só dê 160 ou 200 quando a
  evidência da Etapa 1 mostrar o que o nível descreve. Texto curto, argumento genérico,
  repertório decorativo ou proposta incompleta NÃO ganham nota alta por boa impressão geral.
- A redação pode ter sido transcrita de uma foto: "[ilegível]" e palavras estranhas isoladas
  podem ser falha da leitura/OCR, não do aluno. Na C1, não conte esses casos como desvio.
- Trechos riscados pelo próprio candidato (ver regra de C1 acima) nunca contam contra nenhuma
  competência — são a versão final sendo construída, não um erro mantido.
- Na justificativa de cada competência, cite pelo menos um trecho da redação. Se a nota for
  menor que 200, diga o problema concreto (com trecho) que impediu o nível acima. Se a nota for
  200, diga por que atinge o máximo e NÃO sugira melhorias: no 200 não falta nada.
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
\"\"\"
"""

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
    # A IA age como UM corretor; a correcao dupla (media de 2) foi testada e nao melhorou o erro.
    response, modelo = gerar(
        PROMPT.format(tema=tema, texto=texto),
        types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=ResultadoIA,
        ),
    )
    return ResultadoIA.model_validate_json(response.text), modelo
