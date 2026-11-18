---
title: Treinar IA por matéria (18/11)
author: João
date: 2026-11-18
branch: domina-ciclo-3
cost: { minutes: 2, tokens: 78170 }
---

## Decided
TreinarIA.tsx usa um só estado `materiaId` (seletor de botões no topo); tudo abaixo filtra por ele. "Seu jeito" virou uma frase só (vies + diferenca_media só se acrescentar). Textos de `falta` no backend ficam em minúscula; o frontend põe "Falta:" e acrescenta "envie rubrica/gabarito" sozinho.
## Tried and ruled out
Nada.
## Watch out
Use `venv/bin/python` (não há `python` no PATH). `sed` do BSD falhou com acentos: use python para editar. Não abri a tela rodando, só tsc e testes.
