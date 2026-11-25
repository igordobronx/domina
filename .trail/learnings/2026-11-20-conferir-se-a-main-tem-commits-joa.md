---
title: Conferir se a main tem commits de outros autores
author: João
date: 2026-11-20
branch: domina-ciclo-3
cost: { minutes: 1, tokens: 47983 }
---

## Decided
Comparar main com a branch: git fetch, depois git log domina-ciclo-3..origin/main e merge-base --is-ancestor. Em 20/11 a origin/main (4af68de) ja estava dentro da domina-ciclo-3: 0 commits de outros autores.

## Tried and ruled out
Nada alem disso; sem diferenca nao precisou de graphify.

## Watch out
So leitura: nada de merge, commit ou push. Saida vazia do git log significa 0 commits, confirmar com rev-list --count.
