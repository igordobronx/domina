# XP e gamificação: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** XP por ações + metas, com nível, histórico, sequência e conquistas na "Minha evolução".

**Architecture:** função pura `montar_xp(eventos, hoje)` em `backend/app/gamificacao.py` faz todas as contas; `carregar_eventos(db, aluno_id)` lê os dados; `xp_do_aluno(db, aluno_id)` junta os dois. Rota nova `GET /gamificacao/minha`. `/metas/minhas` e `/metas/ranking` passam a usar XP. Frontend mostra.

**Tech Stack:** FastAPI + SQLAlchemy, pytest; React + TS, Vitest.

**Spec:** `docs/superpowers/specs/2026-11-18-xp-gamificacao-design.md`

## Global Constraints
- Sem migration. Valores de XP e conquistas exatamente como na spec. Faixas: 0, 80, 300, 550, 850, 1200, 1600.
- Nota da IA nunca conta; só `Correcao.status == APROVADA` com `nota_professor`.
- Envio só conta com `texto_confirmado` e uma vez por atividade (o primeiro envio confirmado).
- Ranking só para equipe; aluno nunca vê XP de outro.
- Sem commit até o usuário pedir.

## Review Focus
1. Aluno que respondeu 10 exercícios no mesmo dia: XP de exercício do dia para em 30. Teste na Task 1.
2. Dois envios da mesma atividade: só +10 uma vez. Teste na Task 1.
3. Sequência quebrada (estudou ontem não, anteontem sim): sequência atual 0. Teste na Task 1.
4. Aluno sem nada: nível 1, 0 XP, conquistas todas bloqueadas, sem erro. Teste na Task 2.
5. Professor/gestor chamando `/gamificacao/minha`: 403. Teste na Task 2.

---

### Task 1: contas de XP (função pura)
**Files:** Create `backend/app/gamificacao.py`, `backend/tests/test_gamificacao.py`; Modify `backend/app/metas.py` (NIVEIS).

**Interfaces — Produces:**
- `Envio(data: date, titulo: str, no_prazo: bool, redacao: bool)`, `Aprovacao(data, titulo, pct: float, redacao: bool, nota: float)`, `Resposta(data, correta: bool)`, `MetaFeita(data, titulo, pontos: int)` (dataclasses)
- `montar_xp(envios, aprovacoes, respostas, metas, hoje: date) -> dict` com `xp`, `historico` (lista `{data, xp, motivo}`, mais recente primeiro), `sequencia` (`atual`, `melhor`, `estudou_hoje`), `conquistas` (lista `{codigo, nome, descricao, alvo, progresso, conquistada_em}` na ordem da spec).

- [ ] Testes (pytest, sem banco): envio no prazo = 15; 2 envios da mesma atividade → loader dedupe (testado na Task 2); aprovação 85% = 15, 70% = 5; 10 respostas certas num dia = 30 (teto); meta de 50 = 50; 7 dias seguidos = +15 e conquista Constância; sequência atual 0 se faltou ontem e hoje; Primeiro passo com +20; nível com 80 XP = 2.
- [ ] Rodar → FAIL; implementar; rodar → PASS.

### Task 2: leitura do banco e rotas
**Files:** Modify `gamificacao.py` (`carregar_eventos`, `xp_do_aluno`), Create `backend/app/routers/gamificacao.py`, `backend/app/schemas/gamificacao.py`; Modify `backend/app/main.py`, `backend/app/routers/metas.py` (minhas e ranking por XP), `backend/tests/test_metas.py` (teste que dependia da faixa antiga de 20).
- [ ] Testes API: aluno novo → nível 1 e 0 XP; envio objetivo aprovado sobe XP; equipe → 403; ranking ordena por XP.
- [ ] `python -m pytest -q tests/test_gamificacao.py tests/test_metas.py` → PASS.

### Task 3: tela "Minha evolução"
**Files:** Modify `frontend/src/services/api.ts` (tipo + `minhaGamificacao()`), `frontend/src/screens/Learning.tsx` (`Evolution`), `frontend/src/styles.css`.
- [ ] Topo: cartão de nível com barra de XP; cartão de sequência (🔥 atual, melhor, "estudou hoje"); grade de conquistas (bloqueadas em cinza com progresso); histórico (últimos 15).
- [ ] `npx tsc --noEmit -p .`.

### Task 4: XP na Visão geral e em Metas
**Files:** Modify `frontend/src/screens/Dashboard.tsx` (cartão de nível), `frontend/src/screens/Metas.tsx` ("pontos" → "XP", "+30 pts" → "+30 XP", ranking).
- [ ] `npx tsc --noEmit -p .`, `npm test`.

### Task 5: fechar
- [ ] Atualizar `docs/decisoes/gamificacao-niveis-e-metas.md` e `CLAUDE.md`. Testar no site. Revisão final.
