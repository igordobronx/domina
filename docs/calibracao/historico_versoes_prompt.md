# Histórico das versões do prompt de correção (v1 a v21)

Este documento explica, para quem não acompanhou o trabalho, como o prompt que corrige as redações
evoluiu: o que mudou em cada versão, o resultado medido e por que provavelmente melhorou ou piorou.

**Versão em uso no app: v14** (`VERSAO_PROMPT = "v14"` em `backend/app/correcao.py`).
Texto completo: `docs/calibracao/2026-10-20/prompt_v14.txt`.

---

## 1. Como ler os números

**Objetivo.** A IA corrige a redação nas 5 competências do ENEM (C1 a C5, de 0 a 200 cada, total
até 1000). Queremos que ela dê a mesma nota que o INEP daria.

**Como o INEP corrige.** Dois corretores dão notas de 40 em 40 (0, 40, 80, 120, 160, 200) em cada
competência. A nota oficial é a média dos dois. Por isso aparecem notas como 140 e 180. A IA age como
um corretor só, então uma diferença de 20 numa competência já é praticamente um acerto. Dois humanos
divergem, em média, uns 100 pontos no total entre si.

**As medidas usadas.**
- **Erro médio total:** quanto, em média, a nota total da IA fica longe da nota oficial (sem sinal).
  Menor é melhor.
- **Erro por competência (C1 a C5):** a mesma conta, competência por competência.
- **Viés:** a média com sinal. Positivo = a IA dá nota alta demais; negativo = baixa demais.
- **A menos de 100:** quantas redações a IA acertou com menos de 100 pontos de diferença no total.

**Ruído.** Mesmo com o mesmo prompt, a IA não responde sempre igual. Rodando a mesma versão duas vezes,
o erro total muda de 5 a 10 pontos. Por isso só contamos como melhora real um ganho de **6 pontos ou
mais**, de preferência confirmado em duas rodadas.

**As bases de teste (mudaram ao longo do tempo).**
| Período | Base | Observação |
|---|---|---|
| v1 a v3b (13 e 14/10) | 1 redação real (oficial 880) e depois 50 redações: 20 nota 1000 + 30 do Banco UOL | A nota do UOL não é do INEP e tem ruído. Media-se um "score" de 0 a 100. |
| v4 a v6 (15 e 16/10) | UOL + base externa de 80 redações (50 com 3 corretores humanos + 30 Essay-BR) | Mede a distância até a média dos humanos. |
| v6 a v9 (18/10) | **Base INEP com 50 redações** e nota oficial | Primeira régua confiável. |
| v9 em diante (19/10) | **Base INEP com 53 redações** (3 novas) | Base usada em todos os testes desde então. |

Números de bases diferentes **não** se comparam diretamente. Todos os testes na base INEP usaram o
modelo `gemini-3.5-flash-lite` (o app usa o `gemini-3.5-flash`, com cota diária pequena).

---

## 2. Tabela resumo

Base INEP, `gemini-3.5-flash-lite`. "Erro" = erro médio total; C1 a C5 = erro médio por competência.

| Versão | Mudança principal | Base | Erro | C1 | C2 | C3 | C4 | C5 | Viés | <100 | Resultado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v1 | Prompt simples | 1 redação | 280 | | | | | | | | ❌ tudo 120 |
| v2 | Descritores oficiais do INEP | UOL | score 48 | | | | | | | | ⚠️ dura na C1 |
| v3a | Analisar antes da nota + contar desvios na C1 | UOL | score 55 | | | | | | | | ✅ |
| v3b | v3a + 3 exemplos corrigidos | UOL | score 54 | | | | | | | | ❌ não ganhou |
| v4/v4b | Regras de contagem C1, C4 e C5 mais justas | UOL/externa | score 60 | | | | | | | | ✅ |
| v5 | Regras do usuário (não testada sozinha) | | | | | | | | | | virou v6 |
| v6 | C2 pela tabela do INEP + conectivo por parágrafo na C4 | INEP 50 | 67 | 21 | 16 | 21 | 16 | 16 | -8 | 37/50 | ✅ base |
| v7 | C1: 160 é o nível comum, 120 só com 6+ desvios | INEP 50 | 63 | 16 | 15 | 23 | 12 | 11 | -4 | 37/50 | ✅ |
| v8 | C3 com teto 160 e marcação por parágrafo | INEP 50 | 71 | 16 | 17 | 28 | 12 | 12 | -2 | 33/50 | ❌ |
| v9 | C3 com os descritores oficiais do INEP | INEP 50 | 60 | 14 | 15 | 23 | 16 | 10 | +4 | 41/50 | ✅ |
| v9 | (mesma, nas 53) | INEP 53 | 53 | 18 | 15 | 20 | 11 | 12 | -8 | 45/53 | ✅ referência |
| v10 | C3 com 4 falhas checadas + "há autoria?" | INEP 53 | 63 | 21 | 14 | 21 | 14 | 10 | +11 | 43/53 | ❌ |
| v11 | C3: 200 só copiando trecho de autoria | INEP 53 | 55 | 16 | 14 | 25 | 12 | 11 | +26 | 42/53 | ❌ |
| v12 | C3: 160 comum, 200 raro, "na dúvida 160" | INEP 53 | 46 | 16 | 14 | 20 | 11 | 12 | -5 | 46/53 | ✅ |
| v12 dupla | v12 corrigindo 2 vezes e tirando a média | INEP 53 | 49 | 15 | 15 | 19 | 11 | 10 | -9 | 45/53 | ❌ revertida |
| v13 | v14 + C4 mais branda | INEP 53 | 53 | 18 | 12 | 21 | 13 | 11 | -11 | 42/53 | ❌ |
| **v14** | v12 + C2 com piso 160 | INEP 53 | **48** | 18 | 12 | 17 | 12 | 14 | -2 | 46/53 | ✅ **no app** |
| v14 (2ª rodada) | (mesma) | INEP 53 | **48** | 14 | 11 | 18 | 11 | 11 | +8 | 45/53 | ✅ confirmou |
| v15 | C1: 200 com até 3 desvios | INEP 53 | 57 | 15 | 9 | 23 | 15 | 14 | +31 | 44/53 | ❌ |
| v16 | C1: 2 desvios do mesmo tipo ainda são 200 | INEP 53 | 62 | 20 | 15 | 22 | 15 | 11 | -1 | 41/53 | ❌ |
| v17 | C1: tabela do usuário (desvio grave tira 200) | INEP 53 | 59 | 22 | 14 | 20 | 14 | 12 | -5 | 42/53 | ❌ |
| v18 | C4: ligação das frases dentro do parágrafo | INEP 53 | 49 | 20 | 13 | 20 | 12 | 9 | -4 | 47/53 | ⚖️ empate |
| v19 | C3: regra explícita de quando é 120 | INEP 53 | 60 | 18 | 14 | 23 | 14 | 14 | -11 | 43/53 | ❌ |
| v20 | C1: 120 só com 7+ desvios | 27 de 53 | 47* | | | | | | | | ❌ parado |
| v21 | Nota do meio (20, 60, 100, 140, 180) liberada | INEP 53 | 51 | 20 | 15 | 20 | 14 | 12 | -11 | 46/53 | ❌ |

\* Nas mesmas 27 redações o v14 fez 42 e 48: não houve ganho, e o teste foi interrompido.
Espaços vazios = número não registrado para aquela versão.

**Caminho que deu certo:** v2 → v3a → v4b → v6 → v7 → v9 → v12 → **v14**.
Tudo o que foi tentado depois do v14 empatou ou piorou.

---

## 3. Versão por versão

### Fase 1: primeiras versões (13 e 14/10)

**v1. Prompt simples.**
- *O que era:* pedia a nota das 5 competências sem critérios detalhados.
- *Resultado:* numa redação real com nota oficial 880, a IA deu **600**, com 120 em todas as
  competências.
- *Por quê:* sem saber o que separa um nível do outro, a IA escolhe o meio da escala para tudo.

**v2. Descritores oficiais do INEP.**
- *O que mudou:* entrou a descrição oficial de cada nível (0 a 200) de cada competência.
- *Resultado:* a mesma redação subiu para **680**. As competências deixaram de ficar todas iguais.
  Na amostra de 50 (20 nota 1000 + 30 UOL), score **48,4**; nas nota 1000 a média foi só 924, perdendo
  quase tudo na C1 (média 162 de 200).
- *Melhorou, mas pouco:* a IA ficou dura demais na C1 (contava como erro do aluno coisas que eram
  erro de leitura da foto) e "comprimia" as notas: redação fraca ganhava nota alta e redação boa
  ganhava nota baixa.

**v3a. Analisar antes de dar a nota + contar desvios na C1.**
- *O que mudou:* a IA passou a escrever a análise antes da nota e a contar os desvios gramaticais
  na C1 ("até 2 desvios = 200"). Também foi orientada a usar a escala inteira.
- *Resultado:* score **54,6** (v2: 48,4). Nas nota 1000 a média foi de 924 para **986**; todas
  ficaram com 920 ou mais. As redações boas do UOL subiram de 620 para 772.
- *Melhorou:* contar desvios dá à IA um critério objetivo, em vez de uma impressão. Pensar antes de
  dar a nota também ajuda.

**v3b. v3a + 3 redações de exemplo.**
- *O que mudou:* foram colocadas 3 redações já corrigidas no prompt, como referência.
- *Resultado:* score **54,0**, não superou a v3a.
- *Por quê:* com só 3 exemplos a IA tende a copiar o padrão deles; exemplos só ajudam se forem muitos
  e bem escolhidos. A ideia foi abandonada.

**"Prompt novo" (15/10). Duas etapas: evidências e depois nota.**
- *Resultado:* score **54,9**, praticamente igual à v3a.
- *Por quê:* havia um erro de programação: o formato de resposta não tinha o campo da análise, então a
  primeira etapa nem era gerada. Foi corrigido (o campo `analise` vem antes da `nota` no formato da
  resposta) e isso continua em todas as versões seguintes.

### Fase 2: regras mais justas e a base externa (15 e 16/10)

**v4 / v4b. Regras de contagem mais claras.**
- *O que mudou:* C1 com faixas de contagem (200 = até 2 desvios, 160 = até 5...), contar só o que
  tem certeza e ignorar o que parece falha de leitura da foto; C4 sem exigir "conectivo sofisticado";
  C5 com um detalhamento já basta; quando a nota é 200, não sugerir melhoria.
- *Resultado:* score UOL **59,8**; nota 1000 com média 980. Na base externa (3 corretores humanos):
  **105 pontos** da média dos humanos.
- *Melhorou:* tirou exigências que o INEP não faz e que derrubavam notas boas.

**v5. Regras do usuário.**
- *O que mudou:* C1 sem reincidência de erro, C2 com os 3 requisitos do repertório, C4 com 2
  conectivos por parágrafo, C5 com os 5 elementos da proposta, e critérios para a C3.
- *Resultado:* não foi testada sozinha; foi a base da v6.

**v6. C2 pela tabela do INEP + conectivo em cada parágrafo na C4.**
- *O que mudou:* na C2, sem repertório externo legítimo e pertinente a nota é no máximo 120. Na C4,
  exige conectivo no início de cada parágrafo, do 2º ao último.
- *Resultado:* na base UOL piorou (52,4), mas a UOL tem muito ruído. Na base externa, que é mais
  confiável, melhorou: **97 pontos** da média humana (v4b: 105) e ordenação melhor (0,78 contra 0,71).
  Nas 30 do Essay-BR, 133 pontos (v4b: 161).
- Quando chegou a **base INEP de 50**, a v6 foi a primeira medida nela: **erro 67**, C1 21 (viés -10,
  dura demais), C3 21 (viés +11, generosa demais). Isso definiu os próximos alvos: C1 e C3.

### Fase 3: base INEP de 50 redações (18/10)

**v7. C1: 160 é o nível comum.**
- *O que mudou (só na C1):* 160 passa a ser o nível padrão; 120 só com 6 ou mais desvios; "falha de
  estrutura" é só período realmente quebrado.
- *Resultado:* erro total **67 → 63**; C1 **21 → 16**, viés -10 → -7.
- *Melhorou:* a IA rebaixava para 120 redações com poucos erros. Dizer qual é o nível comum puxou a
  nota para onde o INEP costuma ficar.

**v8. C3 com teto de 160 e marcação por parágrafo.**
- *O que mudou:* a IA marcava cada parágrafo como "desenvolvido" ou "apenas afirmado", e a C3 tinha
  teto de 160 se algo fosse só afirmado.
- *Resultado:* **piorou**: erro **71**, C3 **23 → 28**.
- *Por quê:* a regra ficou mais dura que o INEP. No INEP, argumentos "ainda previsíveis" podem ter 160
  e até 200 se bem organizados; a IA passou a punir texto previsível como se fosse fraco.

**v9. C3 com os descritores oficiais do INEP.**
- *O que mudou:* a v8 foi descartada; em cima da v7 a C3 ganhou o texto oficial do INEP (160 aceita
  argumentos previsíveis se organizados; 200 exige autoria).
- *Resultado:* erro **60** (v7: 63), 41 de 50 a menos de 100 (v6: 37). C1 14, C5 10. A C3 seguiu a pior
  (23, viés +12).
- *Melhorou no geral* e virou a versão do app. A C3 continuou generosa: a IA dá 200 onde o INEP dá 160
  ou 180.

### Fase 4: base INEP de 53 redações, foco na C3 (19/10)

**v9 nas 53.** Com as 3 redações novas (uma fraca), o v9 fez **erro 53**, 45 de 53 a menos de 100;
C1 18, C2 15, C3 20 (viés +8), C4 11, C5 12. Esta virou a referência para as versões seguintes.

**v10. C3 com 4 falhas checadas e a pergunta "há autoria?".**
- *O que mudou:* a IA respondia sim/não para 4 falhas apontadas pelo usuário (argumento não explicado,
  repete a coletânea, informação solta, conclusão contradiz) e para "há autoria?". Qualquer falha
  impedia o 200.
- *Resultado:* **piorou**: erro **63**, viés +11; a IA deu 200 na C3 em 28 de 53 redações (v9: 20).
- *Por quê:* perguntar diretamente "há autoria?" faz a IA responder "sim" quase sempre. A pergunta
  empurrou a nota para cima, o contrário do que se queria.

**v11. C3: 200 só se a IA copiar um trecho de interpretação própria.**
- *O que mudou:* 160 como padrão da C3; para dar 200 a IA tinha de transcrever o trecho que prova autoria.
- *Resultado:* **piorou**: erro **55**, C3 25 (viés +22); 200 na C3 em 35 de 53.
- *Por quê:* a mesma lição do v10. Quando se pede à IA para achar uma prova, ela sempre acha uma.
  **Não pedir para a IA buscar ou copiar prova de autoria.**

**v12. C3: 160 comum, 200 raro, "na dúvida, 160".**
- *O que mudou:* a mesma ideia que funcionou na C1 (dizer qual é o nível comum), sem pedir trecho.
- *Resultado:* erro **46** (v9: 53), 46 de 53 a menos de 100, viés -5. C3 continuou em 20, mas o viés
  caiu de +8 para -2.
- *Melhorou:* tirou a tendência da IA de dar 200 na C3. O ganho no total ficou perto do limite do ruído,
  mas a direção estava certa.

**v12 com correção dupla.**
- *O que mudou:* cada redação era corrigida duas vezes e a nota final era a média (arredondada de 20 em
  20), imitando os 2 corretores do INEP.
- *Resultado:* erro **49**, contra 46 de uma correção só. Além disso, gasta o dobro de cota.
- *Revertida:* o app voltou a corrigir uma vez só.

### Fase 5: dia da entrega (20/10)

**v14. v12 + C2 com piso de 160.**
- *O que mudou (só na C2):* com pelo menos um repertório externo legítimo e pertinente, a C2 é no mínimo
  160; repertório usado de forma produtiva = 200; só citado = 160.
- *Resultado:* erro **48** e **48** em duas rodadas; 46 e 45 de 53 a menos de 100. C2 caiu de 14 para
  **12** e a C3 ficou em 17.
- *Por quê ficou:* empatou com o v12 no total, mas melhorou a C2 e repetiu o mesmo resultado na segunda
  rodada, o que dá mais segurança. O usuário escolheu o v14. **É a versão do app.**
- *O que ainda erra:* C1 com viés para baixo (a IA dá 160 onde o INEP deu 180 ou 200) e C4 com viés
  para cima (a IA dá 200 onde o INEP deu 160 ou 180).

**v13. v14 + C4 mais branda.**
- *O que mudou:* uma falha isolada de coesão passa a ser 160, e 120 só com várias falhas.
- *Resultado:* **piorou**: erro **53**, viés -11, C4 13.
- *Por quê:* a C4 já estava alta; afrouxar a regra mexeu nos casos errados. Não afrouxar a C4.

**v15. C1: 200 com até 3 desvios.**
- *Resultado:* **piorou**: erro **57**, viés **+31**. As redações fracas subiram para 664 (real 564).
- *Por quê:* a regra corrigiu as boas que perdiam ponto, mas também subiu as fracas. A IA ficou
  generosa em geral.

**v16. C1: 2 desvios do mesmo tipo ainda podem ser 200.**
- *Resultado:* **piorou**: erro **62**, C1 20.
- *Por quê:* a IA não conta "tipos" de desvio do mesmo jeito que o corretor, e a regra deixou a
  contagem mais confusa.

**v17. C1: tabela do usuário (1 desvio grave tira o 200; parágrafo de um período só = 120).**
- *Resultado:* **piorou**: erro **59**, C1 22 (viés -12).
- *Por quê:* a IA passou a achar "desvio grave" em textos bons e derrubou notas que estavam certas.

**Conclusão das tentativas na C1 (v15 a v17):** mudar o texto da regra da C1 não ajuda. O erro não está
na regra, e sim na forma como a IA conta os desvios, que é diferente do corretor. Endurecer ou afrouxar
só troca um erro por outro.

**v18. C4: as frases precisam se ligar dentro de cada parágrafo.**
- *O que mudou:* para dar 200 na C4, cada parágrafo de desenvolvimento precisa ligar as frases dentro
  dele; frases soltas ou palavra repetida sem retomada = 160.
- *Resultado:* erro **49**, 47 de 53 a menos de 100; C4 continuou em 12, mas o viés caiu de +6 para +2;
  C5 9.
- *Empate:* a diferença para o v14 (48) é menor que o ruído. Ficou o v14, com o acordo do usuário.

**v19. C3: regra explícita de quando é 120.**
- *O que mudou:* 120 quando há parágrafo repetido, argumento anunciado e não desenvolvido, ou parágrafo
  só afirmado.
- *Resultado:* **piorou**: erro **60**, C3 23, viés -11.
- *Por quê:* a IA passou a enxergar esses defeitos em redações que o INEP aceitou como 160 ou 180.
  Parecido com o que aconteceu no v8.

**v20. C1: 120 só com 7 ou mais desvios.**
- *Resultado:* interrompido pelo usuário em 27 de 53. Nessas 27, erro 47, contra 42 e 48 do v14 nas
  mesmas 27. **Sem ganho.**

**v21. Nota do meio liberada (20, 60, 100, 140, 180).**
- *Ideia:* como a nota oficial é média de 2 corretores, cerca de 29% das notas reais são "do meio"
  (140, 180...), que a IA nunca acerta. A IA poderia dar a nota do meio quando a redação ficasse entre
  dois níveis.
- *Resultado:* erro **51** (v14: 48). A IA usou nota do meio **só 1 vez em 265** notas.
- *Por quê:* a IA prefere os níveis do descritor oficial (de 40 em 40) e ignora a opção nova. A mudança
  praticamente não teve efeito. Também se testou converter a nota da IA depois da correção (por
  exemplo, 120 na C1 vira 140), mas isso não funcionou em redações novas.

---

## 4. O que aprendemos

1. **Dizer qual é o nível comum funciona** (v7 na C1, v12 na C3). Regras que dizem "puna isto" tendem a
   fazer a IA punir demais (v8, v17, v19).
2. **Não pedir para a IA procurar ou copiar prova** de algo (v10, v11). Ela sempre encontra.
3. **O erro que sobra não tem direção.** Comparando as duas rodadas do v14, em C1, C2 e C3 a IA erra quase
   o mesmo tanto para cima e para baixo. Por isso endurecer ou afrouxar uma regra só troca um erro pelo
   outro (foi o que aconteceu do v15 ao v20).
4. **Metade do erro grande vem de 5 redações** que a IA erra igual nas duas rodadas (IDs 5, 9, 27, 29 e
   31; por exemplo, a 31 tem nota real 720 e a IA dá 960). Regra geral não conserta esses casos; é
   preciso olhar cada um.
5. **Ruído de 5 a 10 pontos** entre rodadas. Um ganho menor que 6 não prova nada.
6. **Poucos exemplos (v3b), correção dupla e nota do meio** não ajudaram.
7. **A "confiança" que a IA informa não serve:** fica sempre entre 0,93 e 0,96, mesmo quando ela erra
   500 pontos.

## 5. Conclusão

O app usa o **prompt v14**. Na base de 53 redações com nota oficial do INEP, ele erra em média **48
pontos** no total (duas rodadas, 48 e 48), e 46 de 53 redações ficam a menos de 100 pontos da nota
oficial. Para comparar: dois corretores humanos divergem, em média, uns 100 pontos entre si. Desde o
primeiro teste na base INEP (v6, erro 67) o erro caiu cerca de 30%.

Próximos passos sugeridos:
- Confirmar o v14 no modelo do app (`gemini-3.5-flash`); só 3 de 15 redações rodaram até agora, com
  resultado parecido com o flash-lite.
- Estudar uma a uma as 5 redações que a IA erra sempre, antes de propor qualquer regra nova.
- Conseguir mais redações fracas com nota oficial (hoje só 5 abaixo de 700).

## Onde estão os arquivos

- Prompts: `docs/calibracao/<data>/prompt_vNN.txt` (v7 a v9 em `2026-10-18/`, v11 e v12 em `2026-10-19/`,
  v13 a v21 em `2026-10-20/`).
- Resultados por redação: `docs/calibracao/<data>/inep_lite_vNN.jsonl`.
- Para recalcular os números: `python docs/calibracao/2026-10-18/analisa_inep.py <arquivo.jsonl>`.
- Relatórios antigos: `docs/decisoes/2026-10-13-correcao-ia-calibracao.md` e
  `docs/decisoes/2026-10-14-relatorio-calibracao-correcao.md`.
