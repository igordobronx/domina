# CLAUDE.md: domina, correção de redação do ENEM por IA

Atualizado em 19/10/2026 (noite, 3ª versão; as anteriores estão em docs/handoff_CLAUDE_2026-10-19.md e docs/handoff_CLAUDE_2026-10-19b.md). Responda sempre em português, de forma curta e simples, sem números difíceis.

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
  - `4b35e86` (18/10): prompt **v9** em `correcao.py` (`VERSAO_PROMPT = "v9"`) + testes em `docs/calibracao/2026-10-18/`.
  - commit de 19/10: teste do v9 nas 53 do INEP, prompt v10 (não adotado) e scripts em `docs/calibracao/2026-10-19/`.
  - commit de 19/10 (noite, 2): app aplicado com **v12 + 2 correções + média** (seção 5).
  - commit de 19/10 (noite): v11 (pior, não adotado) e v12 (melhor total, ainda NÃO aplicado em `correcao.py`), com prompts, resultados e scripts em `docs/calibracao/2026-10-19/`.
- **O prompt fica em** `backend/app/correcao.py` (constante `PROMPT`, chamada em `corrigir()`).
- **Rede (19/10):** quando a thread se conecta ao Mac (ferramentas de pasta), o container perde o acesso a `generativelanguage.googleapis.com` (403). Para o Claude rodar o Gemini sozinho, a thread NÃO deve se conectar ao Mac: as redações 51–53 já estão em `essays/novas_51_53.jsonl` e `docs/calibracao/2026-10-19/roda_inep53.py` junta elas às 50 da planilha (de `backend/`, com `DATABASE_URL=sqlite:// JWT_SECRET=x PYTHONPATH=.`). Se não der, o usuário roda `bash docs/calibracao/2026-10-19/roda_v12.sh` no terminal do Mac.
- **Rodar os testes (19/10):** o usuário quer que o Claude rode TUDO sozinho. Ele colocou `GEMINI_API_KEY` como variável do cloud environment do projeto, então no container: `pip install -r backend/requirements.txt` e rodar o `roda_inep.py` (de `backend/`, com `PYTHONPATH=.`). Atenção: a planilha em `/mnt/project-files/domina/essays/` tem só 50 redações; a do Mac tem 53 (IDs 51–53 novas). Se não conseguir copiar a do Mac (`device_stage_files` dá 401), monte as 3 novas lendo via `device_bash` e confira com hash. O VM do Mac não tem internet.
- **Scripts de teste:** `backend/calibracao/` (`calibra.py` para o Gemini, `calibra_groq.py` para a Groq, `analisa.py` para o score, `variantes.py` para as versões) `docs/calibracao/2026-10-16/analisa_externa.py` (base externa) e, para a base INEP, `docs/calibracao/2026-10-18/roda_inep.py` + `analisa_inep.py` (uso: de `backend/`, `PYTHONPATH=. python ../docs/calibracao/2026-10-18/roda_inep.py <prompt.txt> <saida.jsonl> gemini-3.5-flash-lite`).
- **Chaves:** `backend/.env` (`GEMINI_API_KEY`, `GROQ_API_KEY`). O arquivo fica fora do git. Nunca imprima nem commite as chaves.
- **Modelos:** o app usa `gemini-3.5-flash` (20 chamadas por dia no plano grátis). Para iterar, use `gemini-3.5-flash-lite` (cota separada, roda 50 redações em minutos) ou a Groq `openai/gpt-oss-120b` (grátis, cerca de 25 min para 50).
- **graphify:** use sempre. Depois de editar código, rode `graphify update .`, mas não commite o cache de `graphify-out/`.

## 3. Bases de teste (planilhas em `essays/`)

| Arquivo | O que tem | Nota |
|---|---|---|
| `base_redacoes_primeira.xlsm` (na branch se chama `base_redacoes_enem_domina_ai.xlsm`) | 2.328 redações: cerca de 239 nota 1000 (cartilhas e sites) + cerca de 2.100 do Banco UOL (2007–2016) | A nota UOL não é do INEP e tem ruído. A amostra antiga é de 50 redações (semente 42). |
| `base_redacoes_3_corretores.xlsm` (na branch se chama `base_teste_externa.xlsm`) | 80 redações: 50 AES-ENEM (USP, com 3 notas humanas) + 30 Essay-BR | Aba "Comparação corretores". É a melhor régua até agora. |
| `base_redacoes_inep.xlsm` (**a ÚNICA base usada desde 19/10**) | **53 redações** (IDs 51–53 de 2024/2025, uma delas fraca, 560) com **nota oficial do INEP**: 34 de 14 conhecidos (2020–2025, fotos com nome e CPF tarjados) + 10 nota 1000 de sites (IDs 35–44) + 6 de conhecidos (IDs 45–50, 4 abaixo de 700) | As Observações dizem só "Participante X - ano", sem nomes. Agora são 5 abaixo de 700. O usuário NÃO quer mais testar nas bases UOL nem de 3 corretores. Os prints da "Vista Pedagógica" do INEP trazem nome e CPF: nunca copiar. |

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
| v9 nas 53 (19/10) | mesma v9, base INEP com as 3 novas | **erro total 53, 45/53 a menos de 100**, C1 18, C2 15, C3 20 (viés +8), C4 11, C5 12. Fracas: IA 544 x real 564. ✅ |
| v10 | v9 + C3 com as 4 falhas do usuário (argumento não explicado, repete a coletânea, informação solta, conclusão contradiz) checadas sim/não + pergunta "há AUTORIA?"; qualquer falha impede 200 | **Piorou:** total 63, viés +11; a IA deu 200 na C3 em 28 de 53 (v9: 20). Perguntar "há autoria?" faz a IA dizer sim. ❌ |
| v11 | v9 + C3 pedindo para a IA copiar um trecho de interpretação própria; 160 padrão | **Piorou:** total 55, viés +26, C3 erro 25; deu 200 na C3 em 35/53. Pedir para a IA achar prova de autoria faz ela sempre achar. ❌ |
| **v12** | v9 + só a regra da C3: 160 é o nível mais comum, 200 raro (todos os parágrafos com explicação/exemplo próprio), na dúvida 160; sem pedir trecho | Base INEP (53): **erro total 46 (v9: 53), 46/53 a menos de 100, viés -5**; C3 erro 20 (igual), viés -2, mas a IA dá 160 em 40/53. Ganho no total perto do ruído (~5). Melhor total até agora. ⚠️ |
| **v9 (atual)** | v7 + C3 com os **descritores oficiais do INEP** (160 aceita previsível se organizado; 200 = autoria) | **Base INEP: erro médio 60 pts no total, 41/50 a menos de 100 (v6: 67 e 37/50).** C1 14, C2 15, C3 23 (viés +12), C4 16, C5 10. ✅ |

Lições:
- Não ajuste o prompt para acertar uma redação só: isso decora o caso e piora os outros. Use regras gerais e teste na base inteira.
- A base UOL serve só para ver ordenação. Para medir o acerto, use as bases com mais de um corretor ou com nota do INEP.
- A "confiança" que a IA informa não serve (fica entre 0,93 e 0,96 mesmo quando ela erra 500 pontos).
- Mesmo com temperatura 0, a mesma redação varia até 40 pontos entre rodadas; entre rodadas inteiras o erro médio varia uns 5 pontos, então diferença menor que isso não prova nada.
- **Como o INEP nota:** cada corretor dá notas de 40 em 40; a nota oficial é a média de 2 corretores (por isso 140, 180 etc., sempre múltiplo de 20). 3º corretor só se a diferença passar de 80 numa competência ou de 100 no total. A IA age como UM corretor: diferença de 20 por competência conta como acerto.
- A contagem da C1 (2 desvios para 200, 5 para 160) é o critério usado por corretores e cursinhos, não um número oficial do INEP.

## 5. Próximos passos

1. **FEITO no código (19/10 noite), FALTA MEDIR:** `backend/app/correcao.py` agora usa o prompt **v12** (`VERSAO_PROMPT = "v12-2x"`) e `corrigir()` faz 2 correções em paralelo (temperatura 0 e 0,5); nota final = média por competência (pode dar 140/180; o banco aceita, nota é Numeric e a API é float). Se a diferença passar de 80 numa competência ou 100 no total, faz uma 3ª e fica a média do par mais próximo, com confiança limitada a 0,5 (vai para o topo da fila do professor). A `confianca` agora vem da divergência entre as correções (100 pontos de diferença = 0,6; 250 = 0), não da autoavaliação do modelo. Se alguma chamada usou o modelo reserva, devolve o reserva (a rota marca "requer atenção"). Testes: 12 passam (`cd backend && python -m pytest`), com um novo para média e 3ª correção.
   - **Custo:** 2 chamadas por redação (3 se discrepar): no plano grátis (20/dia no flash) dá uns 10 redações por dia.
   - **MEDIR (pendente):** com o Mac conectado o container não alcança o Gemini (403). O usuário roda no terminal do Mac: `bash docs/calibracao/2026-10-19/roda_dupla.sh` (usa `roda_dupla53.py`, que chama o `corrigir()` do app nas 53 do INEP com flash-lite e imprime a análise). Comparar com v12 sozinho: total 46, 46/53 a menos de 100, C3 erro 20. Saída em `inep_lite_v12_dupla.jsonl` e `log_inep_v12_dupla.txt`. A temperatura 0,5 da 2ª chamada não foi testada; se a média não ajudar, tentar 0,3.
2. **C3:** NÃO mexer mais por enquanto. Tentativas: v8, v10, v11 pioraram; v12 corrigiu só o viés. Uma regra pós-prompt (limitar a C3 a 160 quando outra competência não é 200) foi simulada nos resultados do v9 e não ajudou (erro total 52–54). A IA dá 200 em 20 redações e o INEP deu menos em 11, mas as outras competências delas também eram 200: nada separa esses casos.
3. **Redações fracas e médias:** na base INEP só 5 abaixo de 700. Conseguir mais redações com nota oficial baixa (espelho do INEP de conhecidos, com consentimento; para menor de idade, o do responsável). Os prints da "Vista Pedagógica" trazem nome e CPF: nunca copiar.
4. Opcional: detectar anulação (fuga ao tema, cópia, texto curto) antes de corrigir.
5. Confirmar a versão final no `gemini-3.5-flash` (20 chamadas por dia) e levar para a `main` só quando o usuário pedir. Push e PR só quando ele pedir. O push não funciona do Mac-VM nem do container: pedir ao usuário rodar `git push -u origin correcao-prompt-analise` no terminal dele.

Regras de trabalho: sempre usar o graphify; não dar push sem o usuário pedir; não chamar API paga sem confirmação; nada de nomes ou CPF nas planilhas ou arquivos; o usuário gosta de respostas curtas e simples. Mudanças de código vão na cópia compartilhada (`/mnt/project-files/domina`) e/ou na branch a pedido dele.

## 6. Prompts

Em `backend/app/correcao.py` hoje está o **v12** (`docs/calibracao/2026-10-19/prompt_v12.txt`, `VERSAO_PROMPT = "v12-2x"`): igual ao v9, só com a regra da C3 mais dura (160 comum, 200 raro), usado em 2 correções com média. Texto do v9 em `docs/calibracao/2026-10-18/prompt_v9.txt`; da v6 em `docs/calibracao/2026-10-16/prompt_v6.txt`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
