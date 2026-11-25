---
title: "Nova matéria: onde está e conflito (21/11)"
author: João
date: 2026-11-21
branch: domina-ciclo-3
cost: { minutes: 1, tokens: 60143 }
touches:
  - frontend/src/screens/Activities.tsx
---

## Decided
"Nova matéria" fica em NovaAtividade (frontend/src/screens/Activities.tsx): botão abaixo de Turma/Matéria/Tipo abre Modal (nome + tipo). Novo lugar ainda NÃO decidido pelo usuário; não mexer até ele escolher.
## Tried and ruled out
Mover o botão ao lado do rótulo "Matéria" antes da decisão: desfeito (usuário não quer mudança ainda).
## Watch out
Branch origin/student-status-gamification (GustaRibeiror) remove esse botão do mesmo formulário: combinar antes para evitar conflito.
