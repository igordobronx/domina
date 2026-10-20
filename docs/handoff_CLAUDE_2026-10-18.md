# CLAUDE.md: domina, correção de redação do ENEM por IA

Atualizado em 18/10/2026. Responda sempre em português, de forma curta e simples, sem números difíceis.

## 1. Objetivo do prompt

Fazer a IA corrigir redações do ENEM (C1 a C5, de 0 a 200 cada, total até 1000) **o mais perto possível de um corretor humano do INEP**.
A meta realista é a IA ficar a cerca de 100 pontos da média dos humanos, porque dois corretores humanos já divergem uns 104 pontos entre si.

## 2. Onde as coisas estão

- **Pasta no Mac:** `/Users/joaopedro/Documentos/Coding/projeto hackathon/domina` (foi movida em 16/10; antes ficava em `Documentos/Coding/domina`).
- **Branch de trabalho:** `correcao-prompt-analise`. A `main` está intocada e não há PR.
  - `05dd1b3`: campo `analise` antes da `nota` no schema da IA.
  - `8a90c5e`: `calibra_groq.py` passou a ler as competências no formato em lista.
  - `57c5dd1`: prompt v6 em `backend/app/correcao.py` (`VERSAO_PROMPT = "v6"`).
  - `db35f46`: planilha externa, prompts testados, resultados e scripts em `docs/calibracao/2026-10-16/`.
  - commit de 18/10: prompt **v9** em `correcao.py` (`VERSAO_PROMPT = "v9"`) + testes em `docs/calibracao/2026-10-18/` (sem push).
- **O prompt fica em** `backend/app/correcao.py` (constante `PROMPT`, chamada em `corrigir()`).
- **Scripts de teste:** `backend/calibracao/` (`calibra.py` para o Gemini, `calibra_groq.py` para a Groq, `analisa.py` para o score, `variantes.py` para as versões) `docs/calibracao/2026-10-16/analisa_externa.py` (base externa) e, para a base INEP, `docs/calibracao/2026-10-18/roda_inep.py` + `analisa_inep.py` (uso: de `backend/`, `PYTHONPATH=. python ../docs/calibracao/2026-10-18/roda_inep.py <prompt.txt> <saida.jsonl> gemini-3.5-flash-lite`).
- **Chaves:** `backend/.env` (`GEMINI_API_KEY`, `GROQ_API_KEY`). O arquivo fica fora do git. Nunca imprima nem commite as chaves.
- **Modelos:** o app usa `gemini-3.5-flash` (20 chamadas por dia no plano grátis). Para iterar, use `gemini-3.5-flash-lite` (cota separada, roda 50 redações em minutos) ou a Groq `openai/gpt-oss-120b` (grátis, cerca de 25 min para 50).
- **graphify:** use sempre. Depois de editar código, rode `graphify update .`, mas não commite o cache de `graphify-out/`.

## 3. Bases de teste (planilhas em `essays/`)

| Arquivo | O que tem | Nota |
|---|---|---|
| `base_redacoes_primeira.xlsm` (na branch se chama `base_redacoes_enem_domina_ai.xlsm`) | 2.328 redações: cerca de 239 nota 1000 (cartilhas e sites) + cerca de 2.100 do Banco UOL (2007–2016) | A nota UOL não é do INEP e tem ruído. A amostra antiga é de 50 redações (semente 42). |
| `base_redacoes_3_corretores.xlsm` (na branch se chama `base_teste_externa.xlsm`) | 80 redações: 50 AES-ENEM (USP, com 3 notas humanas) + 30 Essay-BR | Aba "Comparação corretores". É a melhor régua até agora. |
| `base_redacoes_inep.xlsm` | **50 redações** com **nota oficial do INEP**: 34 de 14 conhecidos (2020–2025, fotos com nome e CPF tarjados) + 10 nota 1000 de sites (IDs 35–44) + 6 de conhecidos (IDs 45–50, 4 abaixo de 700) | As Observações dizem só "Participante X - ano", sem nomes. Faltam ainda redações fracas (só 4 abaixo de 700). Os prints da "Vista Pedagógica" do INEP trazem nome e CPF: nunca copiar. |

Cuidado: antes de gravar uma planilha no Mac, peça para ela estar **fechada no Excel**. O Excel aberto já salvou a versão antiga por cima da nova.

## 4. Histórico: o que funcionou e o que falhou

| Versão | O que mudou | Resultado |
|---|---|---|
| v1 | Prompt simples | Todas as competências em 120 (redação do Igor, real 880, recebeu 600). ❌ |
| v2 | Descritores oficiais do INEP por nível | 680 no Igor; rígida demais na C1. Score UOL 48,4. ⚠️ |
| v3a | v2 + analisar antes da nota + contar desvios na C1 | Score 54,6; resolveu o rigor nas nota 1000 (média 924 → 986). ✅ |
| v3b | v3a + 3 redações de exemplo (few-shot) | 54,0, não superou a v3a. ❌ |
| "prompt novo" | Duas etapas (evidências → nota) | 54,9. **Bug:** o schema não tinha o campo `analise`, então a Etapa 1 não era gerada. Corrigido em `05dd1b3`. |
| v4 / v4b | C1 com contagem (200 = até 2 desvios, 160 = até 5...), só o que tem certeza, ignorar falha de OCR; C4 sem exigir "conectivo sofisticado"; C5 com 1 detalhamento basta; no 200 não sugerir melhoria | Score UOL 59,8; nota 1000 com média 980. Na base externa: 105 pontos da média humana, ordenação 0,71. ✅ |
| v5 | v4b + regras do usuário (C1 sem reincidência, C2 com os 3 requisitos do repertório, C4 com 2 conectivos, C5 com 5 elementos) + critérios de C3 | Não foi testada sozinha; virou a v6. |
| v6 | v5 + C2 pela tabela do INEP (sem repertório externo legítimo e pertinente, no máximo 120) + C4 com conectivo no início de cada parágrafo (do 2º ao último) | Base UOL: 52,4, pior (mas a UOL tem ruído). **Base externa (3 humanos): 97 pontos da média humana, ordenação 0,78; Essay-BR 133 pontos (v4b: 161).** ✅ |
| v7 | v6 + regra da C1: 160 é o nível comum, 120 só com 6+ desvios, "falha de estrutura sintática" = só período quebrado | Base INEP (flash-lite): C1 erro 21→16; total 67→63. ✅ |
| v8 | v7 + C3 com marcação "desenvolvido/apenas afirmado" por parágrafo e teto 160 | C3 piorou (23→28), total 71. ❌ (previsível NÃO é 120: no INEP o 160 aceita "ainda previsíveis") |
| **v9 (atual)** | v7 + C3 com os **descritores oficiais do INEP** (160 aceita previsível se organizado; 200 = autoria) | **Base INEP: erro médio 60 pts no total, 41/50 a menos de 100 (v6: 67 e 37/50).** C1 14, C2 15, C3 23 (viés +12), C4 16, C5 10. ✅ |

Lições:
- Não ajuste o prompt para acertar uma redação só: isso decora o caso e piora os outros. Use regras gerais e teste na base inteira.
- A base UOL serve só para ver ordenação. Para medir o acerto, use as bases com mais de um corretor ou com nota do INEP.
- A "confiança" que a IA informa não serve (fica entre 0,93 e 0,96 mesmo quando ela erra 500 pontos).
- Mesmo com temperatura 0, a mesma redação varia até 40 pontos entre rodadas; entre rodadas inteiras o erro médio varia uns 5 pontos, então diferença menor que isso não prova nada.
- **Como o INEP nota:** cada corretor dá notas de 40 em 40; a nota oficial é a média de 2 corretores (por isso 140, 180 etc., sempre múltiplo de 20). 3º corretor só se a diferença passar de 80 numa competência ou de 100 no total. A IA age como UM corretor: diferença de 20 por competência conta como acerto.
- A contagem da C1 (2 desvios para 200, 5 para 160) é o critério usado por corretores e cursinhos, não um número oficial do INEP.

## 5. Próximos passos

1. **C3:** ainda é a pior (erro 23, dá nota alta demais: o gabarito mais comum é 180 e a IA dá 200). Ideia pendente: pedir na análise só uma contagem simples de argumentos desenvolvidos, sem travar o nível por parágrafo. Perguntar ao usuário como ele escreveria a regra.
2. **Redações fracas e médias:** na base INEP só 4 abaixo de 700 (IA 540 contra 565). Conseguir mais redações com nota oficial baixa (espelho do INEP de conhecidos, com consentimento; para menor de idade, o do responsável). Os prints do usuário só ajudam se vierem com o texto da redação.
3. Rodar também o v9 na base externa de 80 (3 humanos) para confirmar que não piorou lá (o v6 estava em 97 pontos).
4. Opcional: detectar anulação (fuga ao tema, cópia, texto curto) antes de corrigir; trocar a "confiança" por duas correções independentes.
5. Confirmar a versão final no `gemini-3.5-flash` (20 chamadas por dia) e levar para a `main` só quando o usuário pedir. Push e PR só quando ele pedir.

Regras de trabalho: sempre usar o graphify; não dar push sem o usuário pedir; não chamar API paga sem confirmação; nada de nomes ou CPF nas planilhas ou arquivos; o usuário gosta de respostas curtas e simples. Mudanças de código vão na cópia compartilhada (`/mnt/project-files/domina`) e/ou na branch a pedido dele.

## 6. Prompt atual (v9)

O texto exato está em `backend/app/correcao.py` (constante `PROMPT`) e em `docs/calibracao/2026-10-18/prompt_v9.txt`. Mudanças em relação à v6 (que está em `docs/calibracao/2026-10-16/prompt_v6.txt`): regra de contagem da C1 (160 comum, 120 só com 6+ desvios, falha de estrutura = período quebrado) e C3 com os descritores oficiais.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
