# Status "Corrigida pela IA" (aluno): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** o aluno ver 4 status nas atividades: Para fazer, Enviada, Corrigida pela IA, Corrigida.

**Architecture:** só frontend. O backend já manda `AGUARDANDO_CORRECAO`, `PENDENTE`, `REQUER_ATENCAO`, `APROVADA`.
Uma função nova traduz isso para o aluno. O tipo `ActivityStatus` ganha `"corrigida_ia"`. `"pendente"` = "Enviada" para o aluno e "Em revisão" para o professor.

**Tech Stack:** React + Vite + TypeScript, Vitest.

**Spec:** `docs/superpowers/specs/2026-11-17-status-ia-aluno-design.md`

## Global Constraints

- Sem mudança no backend nem no banco.
- Tela de Revisões do professor/gestor e `paraStatus` (usado em `services/revisoes.ts`) não mudam.
- Textos: "Para fazer", "Enviada", "Corrigida pela IA", "Corrigida". Abas do aluno: "Todas", "Para fazer", "Enviadas", "Corrigidas pela IA", "Corrigidas".
- Cores: Enviada amarelo (`amber`), Corrigida pela IA azul (`blue`, nova), Corrigida verde.
- Sem commit: o usuário pede quando quiser (regra do CLAUDE.md).

## Review Focus

1. Envio com status `REQUER_ATENCAO` e sem `criterios` (agente pediu nova foto): tem que ficar "Enviada" e mostrar o botão "Gerar minha correção com IA". Teste na Task 1.
2. Aluno gera a correção na tela de detalhe: ao voltar, a linha mostra "Corrigida pela IA" (a lista recarrega). Conferir à mão na Task 3.
3. Celular: 5 cartões da Visão geral ficam 2 por linha (a regra nova de 5 colunas não pode vencer as `@media` do fim do `styles.css`). Conferir na Task 4.
4. Professor: a linha de uma submissão `pendente` continua "Em revisão" na lista de Revisões e no EducatorDashboard. Conferir na Task 2.
5. Prova objetiva (vai direto para `APROVADA`): continua "Corrigida". Teste na Task 1.

---

### Task 1: função de status do aluno

**Files:**
- Modify: `frontend/src/types.ts:18`
- Modify: `frontend/src/services/atividades.ts`
- Create: `frontend/src/services/atividades.test.ts`

**Interfaces:**
- Produces: `ActivityStatus = "disponivel" | "pendente" | "corrigida_ia" | "aprovada"`;
  `paraStatusAluno(statusBackend: string, temCorrecao: boolean): ActivityStatus` em `services/atividades.ts`.

- [ ] **Step 1: teste que falha** (`atividades.test.ts`, describe "Status do aluno"):
  - `paraStatusAluno("AGUARDANDO_CORRECAO", false)` → `"pendente"`
  - `paraStatusAluno("PENDENTE", true)` → `"corrigida_ia"`
  - `paraStatusAluno("REQUER_ATENCAO", true)` → `"corrigida_ia"`
  - `paraStatusAluno("REQUER_ATENCAO", false)` → `"pendente"`
  - `paraStatusAluno("APROVADA", true)` → `"aprovada"`
  - `paraStatus("PENDENTE")` → `"pendente"` (professor não muda)
- [ ] **Step 2:** `cd frontend && npx vitest run src/services/atividades.test.ts` → FAIL (função não existe).
- [ ] **Step 3:** adicionar `"corrigida_ia"` ao tipo; criar `paraStatusAluno` (APROVADA → aprovada; senão, com correção → corrigida_ia; senão → pendente). Em `carregarAtividadesDoAluno`, trocar `paraStatus(submissao.status)` por `paraStatusAluno(submissao.status, !!submissao.criterios?.length)`. Atualizar o comentário de `paraStatus` (agora é só do professor).
- [ ] **Step 4:** mesmo comando → PASS; `npx tsc --noEmit -p .` sem erro novo.

### Task 2: selo azul e linha da lista

**Files:**
- Modify: `frontend/src/components/ui.tsx:122-128` (Badge)
- Modify: `frontend/src/styles.css` (perto de `.badge-neutral`, linha ~924)
- Modify: `frontend/src/screens/Dashboard.tsx:475-516` (`ActivityRow`)
- Modify: `frontend/src/screens/Activities.tsx:360`, `frontend/src/screens/Dashboard.tsx:418`

**Interfaces:**
- Produces: `Badge` aceita `tone="blue"`; `ActivityRow` ganha `aluno?: boolean` (padrão `false`).

- [ ] **Step 1:** `tone` do Badge aceita `"blue"`; CSS `.badge-blue { background: #dde8f5; color: #22558c; }`.
- [ ] **Step 2:** `ActivityRow`: `corrigida_ia` → selo azul "Corrigida pela IA"; `pendente` → "Enviada" se `aluno`, senão "Em revisão" (amarelo nos dois). Nota só em `aprovada` (como hoje).
- [ ] **Step 3:** passar `aluno={!reviewOnly}` em `Activities.tsx:360` e `aluno={student}` em `Dashboard.tsx:418`. EducatorDashboard fica sem a prop.
- [ ] **Step 4:** `npx tsc --noEmit -p .` e `npm test` → só a falha antiga ("não abre a revisão por um link do gestor").

### Task 3: abas de filtro do aluno

**Files:**
- Modify: `frontend/src/screens/Activities.tsx:175` (comentário de `initialFilter`) e `:319-326` (abas)

- [ ] **Step 1:** aluno (`!reviewOnly`): abas `todas` "Todas", `disponivel` "Para fazer", `pendente` "Enviadas", `corrigida_ia` "Corrigidas pela IA", `aprovada` "Corrigidas". Professor: igual a hoje.
- [ ] **Step 2:** `npx tsc --noEmit -p .`; no site (`./dev.sh`, `aluno@domina.com`): gerar a correção de uma atividade enviada e ver que ela sai de "Enviadas" e vai para "Corrigidas pela IA".

### Task 4: cartões da Visão geral

**Files:**
- Modify: `frontend/src/screens/Dashboard.tsx:50-52` (contagens), `:246-275` (cartões), `:442-467` (`Stat`)
- Modify: `frontend/src/styles.css` (logo depois de `.stats-grid`, linha ~710, e de `.stat-amber`, ~745)

**Interfaces:**
- Consumes: `"corrigida_ia"` (Task 1).
- Produces: `Stat` ganha `blue?: boolean`.

- [ ] **Step 1:** contagem nova `corrigidasIA = atividades.filter(a => a.status === "corrigida_ia")`.
- [ ] **Step 2:** cartões na ordem: Domínio médio, Atividades corrigidas, **Corrigidas pela IA** (azul, ícone `Sparkles`, foot "Nota provisória, falta o professor", abre `corrigida_ia`), **Enviadas** (amarelo, era "Aguardando revisão", foot "Você pode pedir a correção da IA", abre `pendente`), Para fazer.
- [ ] **Step 3:** CSS `.stat-blue { background: #dde8f5; color: #22558c; }` e `.stats-5 { grid-template-columns: repeat(5, minmax(0, 1fr)); }` com **uma classe só**, antes das `@media` (assim no celular continua 2 por linha). Usar `className="stats-grid stats-5"` só na Visão geral do aluno.
- [ ] **Step 4:** `npx tsc --noEmit -p .`, `npm test`; no site, conferir os 5 cartões no computador e em tela de celular (375px), e que cada cartão abre a aba certa.

### Task 5: fechar

- [ ] `graphify update .`
- [ ] Atualizar `CLAUDE.md` seção 4 com uma linha da task 1 (sem mudança de banco).
- [ ] Revisão final da branch (um revisor).
