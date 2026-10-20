# CLAUDE.md: domina, correção de redação do ENEM por IA

Atualizado em 20/10/2026 (thread nova: 1 correção + prompt v14). Responda sempre em português, de forma curta e simples, sem números difíceis.

## 0. Estado em 20/10/2026 (leia primeiro) — ENTREGA DO PROJETO É HOJE

O usuário precisa entregar hoje. Seja rápido: mexa em UMA coisa por versão, rode as 53, fique com a melhor, e pare quando o tempo apertar. Sempre deixe o app funcionando com a melhor versão já testada.

**Onde estamos**
- App corrige **1 vez** com o prompt **v14** (`VERSAO_PROMPT = "v14"` em `backend/app/correcao.py`; 12 testes passam). Correção dupla foi revertida (49 contra 46 de uma só).
- v14 = v12 + C2 com piso 160 (com pelo menos 1 repertório externo legítimo e pertinente a C2 é no mínimo 160; produtivo = 200; só citado = 160). Texto: `docs/calibracao/2026-10-20/prompt_v14.txt`.
- v14 nas 53 do INEP (flash-lite): **erro total 48**, 46/53 a menos de 100, viés -2. Erro por competência: C1 18 (viés **-10**), C2 12, C3 17, C4 12 (viés **+6**), C5 14. Faixas: <=700 IA 528 x real 564; nota 1000 IA 972. v12 (19/10): 46, 46/53, C2 15, C3 20. Empate no total dentro do ruído (~5); o usuário escolheu o v14. Resultados: `docs/calibracao/2026-10-20/inep_lite_v14.jsonl`.
- v13 (v14 + C4 mais branda, falha isolada = 160): 53, C4 piorou. Não repetir.
- Nada foi commitado nem enviado (a pasta compartilhada não é repo git). O usuário faz `git add/commit/push` no Mac no fim (ver seção 5).

**Onde ainda dá para ganhar (ideias para as próximas versões, uma por vez)**
1. **C1 (maior erro, viés -10):** a IA dá 160 onde o INEP deu 180/200 (10 casos 200→160). Afrouxar a regra do 200: o corretor tolera até 2–3 desvios, mesmo do mesmo tipo, se o texto flui. Ver quais regras de reincidência (a do "mesmo desvio repetido tira o 200") estão derrubando.
2. **C4 (viés +6):** a IA dá 200 onde real é 160/180. NÃO afrouxar (v13 piorou). Se mexer, só endurecer algo específico (ex.: conectivo repetido).
3. **Redações fracas (<=700, só 5 na base):** IA dá 528 contra 564; olhar C1/C3 delas.
4. **Nota 1000 (IA 972):** ver quais competências derrubam (provavelmente C1).
5. Lições: pedir para a IA ACHAR/COPIAR prova de autoria na C3 piora (v10, v11); regra pós-prompt de teto na C3 não ajudou; ruído entre rodadas ~5 pontos, então só aceite ganho claro (>=6) ou ganho em várias competências ao mesmo tempo.

**Como rodar (sozinho, sem o usuário)**
- Esta thread (ou a nova) NÃO pode se conectar ao Mac: a rede bloqueia o Gemini. A chave `GEMINI_API_KEY` está no cloud environment.
- Copie a pasta para um scratch (`cp -r /mnt/project-files/domina/{backend,essays,docs} <scratch>/`), `pip install -r backend/requirements.txt`, e de `backend/`: `DATABASE_URL=sqlite:// JWT_SECRET=x PYTHONPATH=. python ../docs/calibracao/2026-10-19/roda_inep53.py <prompt.txt> <saida.jsonl> gemini-3.5-flash-lite`; depois `python ../docs/calibracao/2026-10-18/analisa_inep.py <saida.jsonl>`. Cada rodada leva uns 4 min (roda em background; use until-loop, nada de `sleep` longo; não use `pkill -f roda_inep53`, ele mata o próprio shell).
- **Cota:** o flash-lite no plano grátis acabou depois de umas 3 a 4 rodadas de 53 (190 chamadas) no dia 19. Se acabar de novo, troque o modelo no último argumento (`gemini-3.1-flash-lite`, `gemini-2.5-flash-lite`), mas aí compare as versões SEMPRE no mesmo modelo (rode o v14 de novo nele como base).
- O app usa `gemini-3.5-flash`; o teste usa flash-lite (só 20 chamadas/dia no flash). Se der cota, rode a versão final em umas 10–20 redações no flash só para ver se o comportamento é parecido.

**Regras de trabalho:** responder em português, curto e simples; sempre usar o graphify (`graphify update .` depois de editar código); nada de nomes/CPF; push só pelo usuário; mudanças de código na cópia compartilhada `/mnt/project-files/domina`; ao fim de cada versão testada, atualize este arquivo (tabela do histórico + estado).

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
- **O prompt fica em** `backend/app/correcao.py` (constante `PROMPT`, chamada em `corrigir()`).
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
| v9 | v7 + C3 com os **descritores oficiais do INEP** (160 aceita previsível se organizado; 200 = autoria) | **Base INEP: erro médio 60 pts no total, 41/50 a menos de 100 (v6: 67 e 37/50).** C1 14, C2 15, C3 23 (viés +12), C4 16, C5 10. ✅ |

Lições:
- Não ajuste o prompt para acertar uma redação só: isso decora o caso e piora os outros. Use regras gerais e teste na base inteira.
- A base UOL serve só para ver ordenação. Para medir o acerto, use as bases com mais de um corretor ou com nota do INEP.
- A "confiança" que a IA informa não serve (fica entre 0,93 e 0,96 mesmo quando ela erra 500 pontos).
- Mesmo com temperatura 0, a mesma redação varia até 40 pontos entre rodadas; entre rodadas inteiras o erro médio varia uns 5 pontos, então diferença menor que isso não prova nada.
- **Como o INEP nota:** cada corretor dá notas de 40 em 40; a nota oficial é a média de 2 corretores (por isso 140, 180 etc., sempre múltiplo de 20). 3º corretor só se a diferença passar de 80 numa competência ou de 100 no total. A IA age como UM corretor: diferença de 20 por competência conta como acerto.
- A contagem da C1 (2 desvios para 200, 5 para 160) é o critério usado por corretores e cursinhos, não um número oficial do INEP.

## 5. Próximos passos (versão de 19/10; vale o que está na seção 0)

1. **C3:** ainda é a pior (erro 20, viés +8; o gabarito mais comum é 180 e a IA dá 200). O v10 mostrou que perguntar direto "há autoria?" piora. Próxima ideia: inverter o padrão, dizendo que 160 é o nível comum da C3 (como deu certo na C1 no v7) e 200 só quando a IA consegue citar um trecho de interpretação própria que NÃO está nos textos motivadores. O texto do usuário sobre a C3 (níveis + onde se perde ponto) está em `docs/calibracao/2026-10-19/prompt_v10.txt`; ele disse que não é verdade absoluta.
2. **Redações fracas e médias:** na base INEP só 4 abaixo de 700 (IA 540 contra 565). Conseguir mais redações com nota oficial baixa (espelho do INEP de conhecidos, com consentimento; para menor de idade, o do responsável). Os prints do usuário só ajudam se vierem com o texto da redação.
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


## 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto)

Antes, copie da pasta compartilhada `backend/app/correcao.py`, `backend/tests/test_fluxo_envio.py` e `docs/` para a pasta do Mac (planilha fechada no Excel). Depois:

```
git add backend/app/correcao.py backend/tests/test_fluxo_envio.py docs
git commit -m "Volta a 1 correcao por redacao com prompt v14; testes v13 e v14 na base INEP"
git push
```
