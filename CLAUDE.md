# CLAUDE.md: domina, correção de redação do ENEM por IA

Atualizado em 20/10/2026 à noite (v14 fica; v18 a v20 testados). Versão anterior: `docs/handoff_CLAUDE_2026-10-20b.md`. Responda sempre em português, de forma curta e simples, sem números difíceis.

## 0. Estado em 20/10/2026 à noite (leia primeiro)

> **REGRA PRINCIPAL DO USUÁRIO (20/10): NÃO mude o prompt "de jeito louco".** Não fique trocando
> a regra de uma competência só porque outra deu errado, nem encadeie versões uma atrás da outra.
> Antes de qualquer teste: (1) olhe os resultados e ache a CAUSA do erro (quais redações, em qual
> competência, para que lado, se se repete nas 2 rodadas); (2) explique ao usuário, em poucas
> frases, por que aquela mudança deve melhorar o prompt; (3) espere o ok dele; (4) teste UMA
> mudança. Se não houver uma causa clara, não mude nada: diga isso ao usuário.

**Onde estamos**
- O app corrige **1 vez** com o prompt **v14** (`VERSAO_PROMPT = "v14"` em `backend/app/correcao.py`; 12 testes passam). Texto: `docs/calibracao/2026-10-20/prompt_v14.txt`.
- v14 nas 53 do INEP (flash-lite), 2 rodadas: **erro total 48 e 48**, 46 e 45 de 53 a menos de 100 pontos. É o melhor até agora.
- O usuário decidiu ficar com o v14 na entrega de 20/10.

**Tudo o que foi testado em 20/10 (flash-lite, 53 redações; v14 = 48)**
| Versão | Mudança (em cima do v14) | Erro | |
|---|---|---|---|
| v13 | C4 mais branda (falha isolada = 160) | 53 | ❌ |
| v15 | C1: 200 = até 3 desvios | 57 | ❌ |
| v16 | C1: 2 desvios do mesmo tipo podem ser 200 | 62 | ❌ |
| v17 | C1: tabela do usuário (desvio grave tira 200; parágrafo de um período = 120) | 59 | ❌ |
| v18 | C4: para 200, frases ligadas DENTRO de cada parágrafo | 49 | empate |
| v19 | C3: regra explícita de quando é 120 | 60 | ❌ |
| v20 | C1: 120 só com 7+ desvios | parado em 27/53, sem ganho | ❌ |
| v21 | Nota do meio (20, 60, 100, 140, 180) permitida em todas as competências | 51 | ❌ (a IA usou nota do meio só 1 vez em 265; não muda nada) |
Arquivos: `docs/calibracao/2026-10-20/` (`prompt_vNN.txt`, `inep_lite_vNN.jsonl`).

**O que aprendemos (importante para não repetir)**
1. Comparando as 2 rodadas do v14, o erro NÃO tem direção: em C1, C2 e C3 a IA erra quase o mesmo tanto para cima e para baixo. Por isso endurecer ou afrouxar uma regra só troca um erro pelo outro (foi o que aconteceu do v15 ao v20).
2. Metade do erro grande vem de 5 redações que a IA erra igual nas duas rodadas: IDs 5 (real 740, IA 860), 9 (real 780, IA 920; INEP deu 20 na C3), 27 (real 900, IA 1000), 29 (real 880, IA 760) e 31 (real 720, IA 960). Mudar regra geral não conserta isso.
3. Ruído entre rodadas: 5 a 10 pontos no erro total. Só aceite ganho de 6 ou mais, e de preferência confirme com 2 rodadas.
4. Pedir para a IA ACHAR/COPIAR prova de autoria na C3 piora (v10, v11).

**Próximos passos sugeridos (combine com o usuário ANTES de testar; ele pediu isso)**
1. **Confirmar no modelo do app (`gemini-3.5-flash`)**: só 3 de 15 rodaram em 20/10 (503 e depois cota). Nas 3, ficou parecido com o flash-lite. Rodar as 15: `IDS=46,3,51,48,53,34,21,45,52,25,14,8,42,35,41 DATABASE_URL=sqlite:// JWT_SECRET=x PYTHONPATH=. python ../docs/calibracao/2026-10-20/roda_inep_ids.py ../docs/calibracao/2026-10-20/prompt_v14.txt <saida.jsonl> gemini-3.5-flash` (de `backend/`; a saída retoma de onde parou, então pode usar `flash_v14_parcial3.jsonl`). Cota do flash: ~20 por dia.
2. **Olhar as 5 redações que erram sempre** (IDs acima): ler a justificativa da IA e o texto, e ver se o problema é de transcrição, de tema ou de um critério que a IA não enxerga (ex.: ID 31, que a IA dá 200 em quase tudo). Só depois propor UMA regra.
3. Mais redações fracas com nota oficial (só 5 abaixo de 700).

**Como rodar (sozinho, sem o usuário)**
- A thread NÃO pode estar conectada ao Mac: com a conexão a rede bloqueia o Gemini (403). A chave `GEMINI_API_KEY` está no cloud environment.
- Copie a pasta para um scratch (`cp -r /mnt/project-files/domina/{backend,essays,docs} <scratch>/`), `pip install -r backend/requirements.txt`, e de `backend/`: `DATABASE_URL=sqlite:// JWT_SECRET=x PYTHONPATH=. python ../docs/calibracao/2026-10-19/roda_inep53.py <prompt.txt> <saida.jsonl> gemini-3.5-flash-lite`; depois `python ../docs/calibracao/2026-10-18/analisa_inep.py <saida.jsonl>`. Cada rodada leva uns 6 min. Rode em background e espere com until-loop. Não use `pkill -f roda_inep53` (mata o próprio shell).
- Cota: se o flash-lite acabar, use `gemini-3.1-flash-lite` ou `gemini-2.5-flash-lite`, mas rode o v14 de novo no mesmo modelo como base.

**Regras de trabalho:** português, curto e simples; sempre usar o graphify (`graphify update .` depois de editar código); nada de nomes/CPF; uma mudança por versão e **perguntar ao usuário antes de testar cada mudança**; mudanças na cópia compartilhada `/mnt/project-files/domina`; ao fim de cada versão testada, atualize este arquivo.

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

## 5. Próximos passos antigos (19/10; vale o que está na seção 0)

1. **C3:** ainda é a pior (erro 20, viés +8; o gabarito mais comum é 180 e a IA dá 200). O v10 mostrou que perguntar direto "há autoria?" piora. Próxima ideia: inverter o padrão, dizendo que 160 é o nível comum da C3 (como deu certo na C1 no v7) e 200 só quando a IA consegue citar um trecho de interpretação própria que NÃO está nos textos motivadores. O texto do usuário sobre a C3 (níveis + onde se perde ponto) está em `docs/calibracao/2026-10-19/prompt_v10.txt`; ele disse que não é verdade absoluta.
2. **Redações fracas e médias:** na base INEP só 4 abaixo de 700 (IA 540 contra 565). Conseguir mais redações com nota oficial baixa (espelho do INEP de conhecidos, com consentimento; para menor de idade, o do responsável). Os prints do usuário só ajudam se vierem com o texto da redação.
4. Opcional: detectar anulação (fuga ao tema, cópia, texto curto) antes de corrigir; trocar a "confiança" por duas correções independentes.
5. Confirmar a versão final no `gemini-3.5-flash` (20 chamadas por dia) e levar para a `main` só quando o usuário pedir. Push e PR só quando ele pedir.

Regras de trabalho: sempre usar o graphify; não dar push sem o usuário pedir; não chamar API paga sem confirmação; nada de nomes ou CPF nas planilhas ou arquivos; o usuário gosta de respostas curtas e simples. Mudanças de código vão na cópia compartilhada (`/mnt/project-files/domina`) e/ou na branch a pedido dele.

## 6. Prompt antigo (v9; o atual é o v14, ver seção 0)

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
git commit -m "Prompt v14 fica; testes v15 a v20 e flash na base INEP; novo CLAUDE.md"
git push
```
