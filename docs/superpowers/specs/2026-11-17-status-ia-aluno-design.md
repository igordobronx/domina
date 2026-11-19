# Status "Corrigida pela IA" nas atividades do aluno (task 1)

## Por quê
Hoje, para o aluno, uma atividade enviada fica "Em revisão" antes e depois de ele pedir a correção da IA.
Ele não acha com facilidade quais já têm a nota provisória da IA. Um status a mais resolve isso.

## O que muda (aprovado pelo usuário em 17/11)
Status que o aluno vê:

| Status | Quando | Cor |
|---|---|---|
| Para fazer | ainda não enviou | cinza |
| Enviada | enviou e não pediu a IA (backend: `AGUARDANDO_CORRECAO`) | amarelo |
| Corrigida pela IA | tem correção da IA, falta o professor (backend: `PENDENTE` ou `REQUER_ATENCAO`) | azul |
| Corrigida | o professor aprovou (backend: `APROVADA`) | verde |

- Nova aba de filtro em "Minhas atividades": "Corrigida pela IA".
- O status novo aparece na lista, na Visão geral do aluno e no contador.
- Provas objetivas continuam indo direto para "Corrigida".

## Fora do escopo
- Tela de Revisões do professor e do gestor: fica como está ("Em revisão" junta as duas fases).
- Backend e banco: não mudam. O backend já manda os status separados.

## Abordagens
1. **Só no site, com um valor novo de status (escolhida).** O site passa a separar o que o backend já manda. É pequena e não mexe no banco.
2. Status novo no backend: desnecessária, porque o backend já distingue as fases.
3. Calcular na tela pela existência de nota (`scores`): espalharia a regra por vários lugares.

## Decisões minhas (para o usuário conferir)
- Nome interno: `ActivityStatus` ganha só `"corrigida_ia"`. `"pendente"` passa a ser "Enviada" para o aluno e continua "Em revisão" para o professor. Assim a tela de detalhe (botão "Gerar minha correção com IA") não muda.
- Visão geral do aluno (decidido pelo usuário): 4 cartões. Novo cartão "Corrigidas pela IA" (azul);
  "Aguardando revisão" vira "Enviadas" e conta só as sem IA. Cada cartão abre a aba certa.
  Com "Domínio médio" ficam 5 cartões: no computador, os 5 numa linha; no celular, 2 por linha (decidido pelo usuário).
- Abas do aluno: Todas, Para fazer, Enviadas, Corrigidas pela IA, Corrigidas. A aba "Em revisão" do professor não muda.
- Ordem dos cartões: Domínio médio, Atividades corrigidas, Corrigidas pela IA, Enviadas, Para fazer.
- A IA só conta como "Corrigida pela IA" se a correção tiver notas (`criterios`). Sem notas, fica "Enviada".
- A nota provisória não aparece na linha da lista (só na "Corrigida", como hoje).
