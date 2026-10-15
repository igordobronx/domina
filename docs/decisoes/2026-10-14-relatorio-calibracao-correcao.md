# Relatório: teste de calibração da correção por IA (14/10/2026)

**Pergunta:** a IA está corrigindo com rigor demais? Testado **só com texto digitado**, sem OCR,
para isolar a correção.

## Como foi feito
- Base: `essays/base_redacoes_enem_domina_ai.xlsm` (2.327 redações, montada pelo Lucas).
- Amostra fixa (sorteio com semente 42), 50 redações:
  - **20 com nota 1000 oficial do INEP** (cartilhas "Redação a Mil"). Cada competência = 200.
  - **30 do Banco de Redações UOL**: 10 fracas (≤ 350), 10 médias (400 a 600), 10 boas (≥ 700).
- Modelo: `gemini-3.5-flash-lite`. O flash ficou indisponível (503) o dia todo.
- Três versões das instruções, todas na mesma amostra:
  - **v2:** a que está no app hoje (descritores oficiais do INEP por nível).
  - **v3a:** v2 + analisar antes de dar a nota + contar desvios na C1 + usar a escala inteira.
  - **v3b:** v3a + 3 redações já corrigidas como referência de escala.
- Scripts em `backend/calibracao/`. Resultados brutos em `docs/calibracao/2026-10-14/`.

## Score de Correção (0 a 100)
Média de três partes:

| Parte | O que mede | Como calcula |
|---|---|---|
| **Precisão** | Acerta o topo? (rigidez) | 100 − erro médio nas nota 1000 ÷ 10 |
| **Ordenação** | Separa fraca, média e boa? | Correlação de Spearman com o UOL × 100 |
| **Acerto** | A nota bate com a banca? | % das UOL com diferença de até 100 pontos |

| Versão | Precisão | Ordenação | Acerto | **SCORE** |
|---|---|---|---|---|
| v2 (atual) | 92,4 | 32,8 | 20,0 | **48,4** |
| v3a | 98,6 | 41,8 | 23,3 | **54,6** |
| v3b | 98,6 | 36,6 | 26,7 | **54,0** |

Meta sugerida para o piloto: **score ≥ 75**, com a ordenação acima de 70.

## O que os números mostram

### 1. A rigidez no topo foi resolvida
Nas 20 redações nota 1000, a v2 dava em média **924**, perdendo quase tudo na C1 (−38). Com a
v3a, a média foi **986**, e todas as 20 ficaram ≥ 920. A contagem de desvios na C1 ("até 2
desvios = 200") resolveu o excesso de rigor que o Igor percebeu.

**Atenção:** essas redações estão publicadas na internet, e o modelo pode já tê-las visto.
O resultado no topo pode estar otimista.

### 2. O problema real é compressão, não rigor
A IA puxa as notas para o meio e não diferencia bem os níveis:

| UOL | Real | v2 | v3a | v3b |
|---|---|---|---|---|
| Fracas | 255 | 544 | 604 | 580 |
| Médias | 535 | 592 | 628 | 676 |
| Boas | 845 | 620 | 772 | 728 |

- Redação fraca recebe nota alta demais (de +290 a +350).
- Na v2, redação boa recebia nota baixa demais. Na v3a melhorou bastante (620 → 772).
- A **C5 é o oposto**: a IA é sempre mais dura que o UOL (−27). Ela exige os 5 elementos.

Na redação do Igor (ENEM 2023, oficial 880), a v2 deu 680: o mesmo padrão das "boas".

### 3. A referência do UOL tem ruído
- As notas do UOL vêm de outra banca, numa escala de 0 a 2 convertida (passo 50), e de
  2008 a 2016.
- Há redações com **0 em tudo** (provavelmente anuladas, por fuga ao tema ou cópia). Sem
  saber o motivo, a IA corrige normalmente: a 1907 levou 0 no UOL e 520 na IA.
- Há casos de redação razoável com nota baixa no UOL: a 2100 levou 300 no UOL e 880 na IA.

Parte do "erro" medido é da referência, não da IA. Para medir de verdade, precisamos de
**redações reais com o boletim oficial do INEP por competência**, como a do Igor.

### 4. A confiança informada pela IA não serve
A confiança média ficou entre 0,93 e 0,96 em todas as versões, inclusive quando a IA errou
por 500 pontos. Ela não pode ser usada para ordenar a fila do professor (RF-17).

## Recomendações
1. **Adotar a v3a no app**: maior score, resolve o rigor no topo e é simples.
   Ainda não foi aplicada: o Igor pediu para não mexer no código antes de decidir.
2. **Repetir com o `gemini-3.5-flash`** assim que ele estiver disponível. O lite é o
   modelo reserva e pode subestimar o que o principal consegue.
3. **Montar uma base de 30 ou mais redações com o boletim oficial do INEP** por competência.
   É a referência certa para o score e para o pitch.
4. **Detectar anulação antes de corrigir**: fuga ao tema, cópia dos textos motivadores,
   texto muito curto. É uma etapa separada.
5. **Trocar a "confiança"** por uma medida real, por exemplo a diferença entre duas
   correções independentes da mesma redação.
6. Depois disso, decidir entre few-shot com mais exemplos, RAG ou fine-tuning
   (ver `2026-10-13-correcao-ia-calibracao.md`). A v3b, com só 3 exemplos, não superou a
   v3a. Exemplos só ajudam se forem bem escolhidos e estiverem na escala do INEP.

## Como repetir (inclusive em outro PC)
```sh
cd backend
pip install -r requirements-dev.txt         # inclui openpyxl
# GEMINI_API_KEY no backend/.env
python -m calibracao.calibra ../docs/calibracao/nova.jsonl gemini-3.5-flash 20 30 v3a
python calibracao/analisa.py ../docs/calibracao/nova.jsonl    # imprime o score
```
O script retoma de onde parou se a execução cair ou a cota acabar. O plano grátis do flash
permite 20 chamadas por dia; as 50 redações levam 3 dias, ou alguns minutos com faturamento.
