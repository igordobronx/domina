---
title: Agente sempre corrige e texto longo quebra linha (20/11)
author: João
date: 2026-11-21
branch: domina-ciclo-3
cost: { minutes: 1, tokens: 63712 }
touches:
  - backend/app/agente.py
---

## Decided
Agente (`backend/app/agente.py`, `routers/agente.py`) sempre corrige qualquer envio, nota 0 se couber; ferramenta `pedir_nova_foto` removida. Texto do aluno usa `overflow-wrap: anywhere` (`.essay`, `.texto-resposta` etc. em styles.css).
## Tried and ruled out
Manter `pedir_nova_foto` só para imagem ilegível: o usuário quer corrigir sempre. Prompt v14 da redação não foi tocado.
## Watch out
Rótulo `pedir_nova_foto` ainda existe em Activities.tsx para execuções antigas. Rodar `python` do repo via `venv/bin/python`.
