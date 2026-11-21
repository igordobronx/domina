---
title: Evolução do aluno e exceção dos botões (21/11)
author: João
date: 2026-11-21
branch: domina-ciclo-3
cost: { minutes: 1, tokens: 66233 }
touches:
  - dev.sh
---

## Decided
Poucas opções (2 ou 3) ficam em botões lado a lado, não em Seletor (ex.: Exercícios do aluno, Para você/Do professor). Minha evolução (Learning.tsx, Evolution) usa SeletorMultiplo com prop nova `todos` (linha "Todas as matérias"); nada marcado = todas; só 3 cards de matéria com "Ver mais".
## Tried and ruled out
Carrossel/rolagem interna: mais código que o "Ver mais".
## Watch out
Button do ui.tsx usa `onPress`, não `onClick`. `sed -i` do BSD precisa de `''`. Só front: sem ./dev.sh. Sem commit/push até o usuário pedir.
