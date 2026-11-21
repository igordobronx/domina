---
title: Espaço no card da turma (Turmas)
author: João
date: 2026-11-21
branch: domina-ciclo-3
cost: { minutes: 1, tokens: 52610 }
touches:
  - dev.sh
  - frontend/src/screens/Management.tsx
---

## Decided
O card da turma em Management.tsx usa `.class-summary` (styles.css); o respiro até o botão "Ver alunos da turma" é `margin-bottom` (20px desktop, 14px mobile).
## Tried and ruled out
Procurar outros cards parecidos: só esse usa `.class-summary`, nada mais a alinhar.
## Watch out
Só CSS: não precisa reiniciar o ./dev.sh. Sem commit/push até o usuário pedir.
