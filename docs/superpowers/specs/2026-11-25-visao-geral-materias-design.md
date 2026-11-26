# Visão geral do aluno: matérias em % e subtópicos separados (design)

Task: "Níveis e metas: Arrumar visão geral - mostrar só a matéria (matemática/física/redação em %) e depois separado com subtópicos das matérias."
Formato escolhido: **dois cartões**. Só no site; usa rotas que já existem (`/evolucao/minha` e `/dominio/meu`); sem mudança no banco.

## Cartão 1: "Seu mapa de conhecimento" (onde está hoje)
- Uma linha por matéria: nome, barra e % (a mesma média da tela *Minha evolução*), e "N atividades corrigidas".
- Ordem: maior % primeiro.
- Sem nada corrigido ainda: o aviso de hoje ("Ainda não há correções aprovadas...").

## Cartão 2: "Subtópicos" (novo, logo abaixo)
- Botões com as matérias; abre na matéria de **menor %** (onde o aluno mais precisa).
- Exatas: os subtópicos das questões. Redação: as competências C1 a C5 com nome curto (ex.: "C4 Coesão textual").
- Subtópicos do menor % para o maior.
- Matéria sem subtópicos: "Ainda não há subtópicos nesta matéria."

## Código
- `services/mapaConhecimento.ts` (novo, com testes): função pura que junta evolução + domínio em matérias e subtópicos.
- `HABILIDADE_NOME` vai para esse serviço (as telas que usam continuam funcionando).
- `screens/Dashboard.tsx`: os dois cartões no lugar da lista de competências (só para o aluno real; o professor não muda).

## Alinhado com a Minha evolução (pedido do João, 25/11)
- As duas telas usam a mesma função (`montarMapa`): mesma conta, mesmos nomes curtos (C1 Norma culta...) e mesma ordem (subtópicos do menor % para o maior).
- Mesmos textos: "Competências (C1 a C5)" na redação, "Subtópicos" nas outras; "1 atividade corrigida" / "2 atividades corrigidas".
- O formato continua diferente de propósito: Visão geral = resumo; Minha evolução = detalhe (gráfico, filtro, cartão por matéria).
