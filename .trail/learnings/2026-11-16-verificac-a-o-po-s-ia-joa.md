---
title: "Verificação pós-IA própria: deps, testes, graphify"
author: João
date: 2026-11-16
branch: domina-ciclo-3
cost: { minutes: 2, tokens: 46800 }
touches:
  - backend/requirements.txt
---

## Decided
- Depois das mudanças da IA própria: `venv/bin/pip install -r backend/requirements.txt` (pypdf, pypdfium2), testes por arquivo em `backend/` (12 arquivos, todos passam) e `graphify update .` na raiz.

## Tried and ruled out
- Nada; não foi preciso consertar nada.

## Watch out
- `graphify-out/cache/` não está no .gitignore: aparece como `??` no git status. Não commitar o cache.
- `graphify label` usa LLM; não rodado.
