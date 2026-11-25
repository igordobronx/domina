---
title: Professor corrige sem IA e listas recentes primeiro (20/11)
author: João
date: 2026-11-20
branch: domina-ciclo-3
cost: { minutes: 9, tokens: 126898 }
touches:
  - dev.sh
---

## Decided
Professor corrige direto: `aprovar` cria a Correcao com `modelo_usado="professor"` (`memoria.SEM_IA`) se não existir; `GET /submissoes/{id}/correcao-manual` dá a ficha em branco sem gravar. Sem migration para isso (nota_ia/nota são NOT NULL, ficam iguais à do professor). Memória (`_exemplo`, `concordancia`, erros, `aprendido`) ignora SEM_IA na comparação. Atividade ganhou `criado_em` (migration 0031, default Python `datetime.now`) para ordenar mais recentes primeiro.
## Tried and ruled out
Tornar nota_ia nullable (muitos consumidores); default `func.now()` no model (não vale após migration e SQLite tem precisão de segundos, empata nos testes).
## Watch out
Mudou o banco: parar e rodar `./dev.sh`. Lista do professor: atividades sem envio ficam no fim.
