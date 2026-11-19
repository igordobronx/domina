# CLAUDE.md: Domina

Atualizado em 18/11/2026 (enxugado; histórico detalhado em `docs/historico_domina.md`). Responda sempre em português, de forma curta e simples, sem números difíceis.
Versão anterior (só calibração do prompt da redação, 20/10): `docs/handoff_CLAUDE_2026-10-20c.md`.

Este arquivo diz **o que o projeto é e o que já foi feito**, para uma thread nova continuar de onde a
anterior parou. O que fazer a seguir o usuário diz por escrito em cada thread.

## 1. O que é o Domina

Plataforma de correção com IA para escolas: a IA corrige e **só o professor dá a nota final** (a da IA é
provisória). O aluno envia a resposta (texto ou foto) e pode pedir a correção da IA.

- **Visão:** um **modelo de IA próprio, treinado por matéria** (aba "Treinar IA": o professor sobe ~5 materiais e a IA aprende a corrigir aquela matéria). Domina vai abranger todas as matérias. Hoje as APIs de terceiros são o motor provisório; o README deixa isso claro.
- **MVP:** redação estilo ENEM (C1 a C5) e matemática (e outras exatas, por gabarito). O upload de materiais (`POST /materias/{id}/documentos`) só guarda os arquivos; o treino ainda não está ligado.
- **Perfis:** ALUNO, PROFESSOR, GESTOR (da escola), ADMIN (da plataforma, sem escola).
- **Objetivo original do projeto:** deixar o prompt da correção da redação o mais próximo possível de um corretor humano do ENEM (ver seção 5).

## 2. Onde as coisas estão

- **Repo:** `igordobronx/domina` (GitHub). **Pasta no Mac:** `/Users/joaopedro/Documentos/Faculdade/Projetos GitHub/projeto hackathon/domina` (mudou em 15/11; antes ficava em `Documentos/Coding/projeto hackathon/domina`). Pastas de dados: `essays/` (planilhas), fotos das redações em `.../projeto hackathon/fotos redacoes do enem`.
- **Branch de trabalho: `domina-ciclo-3`** (antes `domina-ciclo-2`). Só fazer merge na `main` quando o usuário mandar. A `main` tem a correção da redação pelo Claude Sonnet.
- **Backend:** `backend/` (FastAPI + SQLAlchemy + Alembic, Python). **Frontend:** `frontend/` (React + Vite + TypeScript, PWA, deploy no Vercel com Root Directory `frontend`). Docs do frontend: `frontend/docs/FRONTEND.md`.
- **Banco:** Postgres no docker (porta **5433**) por padrão; SQLite é o fallback (testes usam SQLite temporário). Migrations em `backend/migrations/versions/` (0001 a 0030).
- **Subir tudo:** `./dev.sh` na raiz (banco + API na 8000 + site na 5173; já roda `migrar.py`; `./dev.sh --seed` roda o seed antes). A API e o site recarregam sozinhos quando o código muda; **só mudança de banco exige parar (Ctrl+C) e rodar `./dev.sh` de novo** (ou `cd backend && ../venv/bin/python migrar.py` em outro terminal).
- **Logins do seed** (senha `senha123`): `professor@domina.com` (Beto Andrade, turma "3º Ano A"), `gestor@domina.com`, `admin@domina.com`, `gestor2@domina.com` (outra escola), alunos `aluno@domina.com` (Ana Beatriz), `aluno2@domina.com` (Bruno), `aluno3@domina.com` (Carla).
- **Chaves** em `backend/.env` (fora do git; nunca imprimir nem commitar): `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`. No cloud environment do projeto a `GEMINI_API_KEY` já existe.
- **Modelos:** redação e agente = Claude Sonnet (`claude-sonnet-5-5`); exercícios gerados pela IA = Claude Haiku (`claude-haiku-5-5`); OCR e correção de exatas = Gemini (`gemini-3.5-flash`, reserva `gemini-3.5-flash-lite`). Camada única em `backend/app/llm/` e `backend/app/ocr/`.
- **Testes:** `cd backend && python -m pytest -q tests/test_X.py` (todos passam; rodar por arquivo). Frontend: `npx tsc --noEmit -p .`, `npm test` (todos passam; o teste do gestor foi atualizado em 18/11: o gestor abre Revisões em modo leitura) e `npm run test:e2e` (Playwright).
- **graphify:** usar sempre (regra do projeto). Antes de explorar: `graphify query "<pergunta>"`. Depois de editar código: `graphify update .`. Não commitar o cache de `graphify-out/cache`.

## 3. Regras de trabalho (preferências do usuário)

- Português, respostas curtas e simples.
- **Mudar o código direto no Mac** (pasta acima), via `device_bash` / `device_commit_files`. **Não fazer commit nem push a cada mudança: só quando o usuário pedir.** Nada de merge na `main` sem ele mandar. O push do container e do VM do Mac costuma falhar; se pedir push, ele roda `git push` no terminal dele.
- **Não gerar prints/imagens da tela a cada mudança.**
- Ao gravar planilha no Mac, pedir que esteja fechada no Excel. `device_commit_files` pode gravar versão antiga logo após `cp` em `/mnt/project-files` (cache): copiar com nome novo e conferir o `md5sum` dos dois lados.
- Nunca copiar nome/CPF de redação (planilhas só têm "Participante X - ano").
- Não chamar API paga sem confirmar. Uma mudança por vez no prompt da redação, **combinando antes** com o usuário (seção 5).
- Ao avisar que algo mudou, dizer em uma frase se precisa parar e rodar o `./dev.sh` de novo (só quando o banco mudou).

## 4. O que já foi feito (resumo)

Detalhe, em ordem, de tudo: `docs/historico_domina.md`. Em uma linha por área:

- **Base e correção:** FastAPI + OCR com Gemini + correção por IA (redação pelo Claude, prompt v14; exatas por gabarito no Gemini); agente de correção (`app/agente.py`).
- **Backend:** cadastro, turmas, atividades (várias turmas, objetivas, várias fotos), domínio por competência, evolução, metas e níveis, calendário, RBAC com isolamento por escola, Alembic, logs com auditoria em cadeia de hash.
- **Frontend:** telas reais para aluno, professor, gestor e admin (login real, sem modo demonstração).
- **Exercícios (15/11):** professor cria (escrever ou pedir para a IA, por turma/aluno), aluno responde uma vez; prática, não vale nota.
- **IA própria (16 a 18/11):** memória do professor (RAG), tela Treinar IA, material de treino. Resumo abaixo.

**Status "Corrigida pela IA" do aluno (17/11, branch `student-status-gamification`):** o aluno vê 4 status: Para fazer, Enviada (amarelo, sem correção), **Corrigida pela IA** (azul, tem notas da IA e falta o professor) e Corrigida (verde). Só no site: `paraStatusAluno` em `frontend/src/services/atividades.ts` (status `corrigida_ia`); `paraStatus` continua para o professor, que segue vendo "Em revisão". Abas do aluno: Todas, Para fazer, Enviadas, Corrigidas pela IA, Corrigidas. Visão geral do aluno com 5 cartões (classe `stats-5`; no celular 2 por linha). Spec e plano em `docs/superpowers/`. Sem mudança de banco. Commit `69a9580`.

**XP e gamificação (18/11, mesma branch):** nível agora = **XP** (ações do aluno + metas), calculado na hora em `backend/app/gamificacao.py` (sem migration). Tabela de XP, teto de 30 XP/dia em exercícios, 9 conquistas, sequência de dias e faixas novas (80, 300, 550, 850, 1200, 1600) em `docs/decisoes/gamificacao-niveis-e-metas.md`. Rota `GET /gamificacao/minha` (só aluno). Tela "Minha evolução" com nível + barra de XP, sequência, conquistas, histórico e "Como ganhar XP" (`frontend/src/screens/Gamificacao.tsx`). Visão geral, "Metas e níveis" e ranking falam em XP. Testes: `backend/tests/test_gamificacao.py` (13). Sem mudança de banco.

## 5. Correção da redação: estado do prompt

> **Regra do usuário: não mude o prompt "de jeito louco".** Antes de testar: ache a CAUSA do erro (quais redações, qual competência, para que lado, se repete nas 2 rodadas), explique ao usuário em poucas frases por que a mudança deve ajudar, espere o ok e teste **uma** mudança. Sem causa clara, não mude nada.

- O app corrige **1 vez** com o prompt **v14** (`VERSAO_PROMPT = "v14"` em `backend/app/correcao.py`; texto em `docs/calibracao/2026-10-20/prompt_v14.txt`). Nas 53 redações do INEP (flash-lite), 2 rodadas: **erro total 48 e 48**, 45 a 46 de 53 a menos de 100 pontos. É o melhor; v13 e v15 a v21 não ganharam.
- Histórico completo (v1 a v21, o que funcionou e o que falhou): `docs/calibracao/historico_versoes_prompt.md` e a tabela em `docs/handoff_CLAUDE_2026-10-20c.md`.
- **O que aprendemos:** o erro não tem direção (endurecer ou afrouxar só troca um erro pelo outro); metade do erro grande vem de 5 redações que a IA erra igual nas duas rodadas (IDs 5, 9, 27, 29, 31); o ruído entre rodadas é de 5 a 10 pontos (só aceitar ganho de 6 ou mais, de preferência em 2 rodadas); pedir para a IA achar/copiar prova de autoria na C3 piora; a "confiança" que a IA informa não serve.
- **Como o INEP nota:** cada corretor dá notas de 40 em 40; a nota oficial é a média de 2 corretores (por isso 140, 180...); 3º corretor se a diferença passar de 80 numa competência ou de 100 no total. A IA age como um corretor: diferença de 20 por competência conta como acerto. Dois humanos divergem uns 104 pontos entre si.
- **Bases de teste** (`essays/`): `base_redacoes_final_inep.xlsm` (**a única usada desde 19/10**: 53 redações com nota oficial do INEP, fotos com nome/CPF tarjados, observações "Participante X - ano"), `base_redacoes_segunda.xlsm` (80, 50 com 3 notas humanas), `base_redacoes_primeira.xlsm` (UOL, só ordenação). O usuário não quer mais testar nas duas últimas.
- **Como rodar teste** (sozinho, sem o usuário): a thread **não pode estar conectada ao Mac** (a rede bloqueia o Gemini); copiar `backend`, `essays` e `docs` para um scratch e, de `backend/`: `DATABASE_URL=sqlite:// JWT_SECRET=x PYTHONPATH=. python ../docs/calibracao/2026-10-19/roda_inep53.py <prompt.txt> <saida.jsonl> gemini-3.5-flash-lite`; depois `python ../docs/calibracao/2026-10-18/analisa_inep.py <saida.jsonl>`. Cada rodada leva uns 6 min (rodar em background). Cota do `gemini-3.5-flash`: ~20 por dia. Em 20/10 só 3 de 15 redações rodaram no `gemini-3.5-flash` (parecido com o flash-lite).

## 6. Mapa rápido do código

| O quê | Onde |
|---|---|
| Rotas | `backend/app/routers/` (submissoes, correcoes, agente, atividades, questoes, turma, usuario, escolas, painel, calendario, metas, logs, documento, dominio, estudos, exercicios, evolucao, compliance, ocr, auth) |
| Modelos / enums | `backend/app/models/usuario.py`, `models/enum.py` |
| Schemas | `backend/app/schemas/` |
| Correção redação / exatas | `backend/app/correcao.py`, `backend/app/correcao_exatas.py` |
| IA de exercícios | `backend/app/estudos.py` (pelos pontos fracos), `backend/app/exercicios_ia.py` (professor) |
| Telas | `frontend/src/screens/` (Dashboard, EducatorDashboard, Activities, Learning, Exercicios, Management, Metas, Calendar, Logs, Admin, Settings) |
| Cliente da API | `frontend/src/services/api.ts` |
| Navegação por perfil | `frontend/src/App.tsx` (`navItems`) e `frontend/src/services/navigation.ts` (`allowedPages`) |
| Docs de decisão | `docs/decisoes/`, README (fluxo do agente), `frontend/docs/` |

## IA própria: resumo (detalhe da memória, tela e migrations 0024 a 0030 em `docs/historico_domina.md` e `docs/decisoes/ia-propria.md`)

- Sem material do professor a IA usa a inteligência do modelo; com material, segue o professor. Memória é **de cada professor** (material do gestor vale para todos). Código em `backend/app/ia/` (`memoria.py`, `extracao.py`, `embeddings.py`, `registro.py`), tabelas `ia_trecho` e `ia_chamada`.
- **Tela Treinar IA** (`frontend/src/screens/TreinarIA.tsx`, menu entre Exercícios e Calendário): tudo por matéria, com um seletor de matéria no topo (nada pré-marcado, clicar de novo desmarca; mesma regra para turma em Exercícios, com o aviso "Escolha..." acima dos botões).
- **Regras do usuário:** nada é apagado sem a IA ter aprendido; "esquecer"/"tirar de uso" só tira de uso e fora do treino (`ia_trecho.ignorado`, documento arquivado); o modelo do app NÃO é o Fable (só para construir); só existe o Mac como máquina de trabalho.
- **Migrations:** 0024 a 0030 são nossas (0019 a 0023 vieram da main). Banco antigo com numeração antiga: recriar (`./dev.sh --seed` num banco limpo). Mudou o banco? Avisar para parar e rodar `./dev.sh` de novo.

- **Plano para a nossa IA ficar treinada (18/11, combinado com o usuário; NADA disso foi feito ainda, ele mandou esperar):** Claude e Gemini seguem no app até a nossa ficar ótima. Termos de uso do Claude/Gemini: o usuário já autorizou, não é mais pendência.
  - **Fase 1, preparar (sem custo):** (1) tirar nome e CPF dos dados de treino; (2) camada de troca de modelo (`app/llm`, uma porta só: `gerar_json`), **pronta mas desligada**: o padrão continua Claude/Gemini, com reserva no Claude se o nosso falhar (uma tentativa minha de config `IA_PROVEDOR=aberto` com API compatível com a da OpenAI foi desfeita; os chamadores importam `gerar_json` de `app.llm.claude`, `app/agente.py` usa `_client` direto e o Gemini fica em `app/ocr/gemini.py`); (3) guardar também os passos do agente (`app/agente.py`) no material de treino; (4) montar o conjunto de treino inicial para a IA já chegar treinada (redações do INEP com nota oficial em `essays/`, exercícios e gabaritos de matemática, correções do Claude revisadas pelo professor).
  - **Fase 2, treinar (precisa dele e de dinheiro):** (5) escolher o modelo aberto (Qwen, Llama ou Gemma) e onde treinar: dá para começar **local no Mac com LoRA** (camada pequena por cima do modelo aberto, uma por matéria ou professor) num modelo de 1 a 4 bi só para provar o caminho; se faltar qualidade, GPU alugada para 7 a 14 bi (perguntar o modelo e a memória do Mac dele); (6) **rodar o treino** (ajuste fino) com o conjunto inicial; (7) medir a nossa contra o Claude nas correções já revisadas; só avança se a concordância for boa.
  - **Fase 3, ligar:** (8) comparação em paralelo ("testar a IA antes de valer"): a nossa também corrige e guarda a diferença, sem valer e sem travar o professor (como e quando roda: em aberto, ver abaixo; **não roda no `./dev.sh`**); (9) trocar de vez quando a concordância passar do limite, mantendo o Claude de reserva; (10) a cada ciclo, treinar de novo com o que os professores corrigiram.
  - **EM ABERTO, a decidir depois (18/11):** como o treino é disparado (comando manual `python treinar_ia.py`, agendado no Mac, servidor/GPU alugada) e o que roda junto com o app (comparação em paralelo em segundo plano, treino automático). Opções discutidas: manual primeiro; o treino pesado não roda a cada upload (o professor já vê a IA aprender na hora pela memória/RAG) e sim quando juntar dado novo (ex.: 100 correções aprovadas). Não implementar nada disso sem ele decidir.
  - Ainda pendente também: testar o embedding do Gemini com chave real e juntar correções reais para ajustar os limites do selo "Pronta".
- Pendente: testar o embedding do Gemini com chave real; partes 2 (camada única para trocar de modelo) e 3 (ajuste fino); atualizar o graphify (só roda no Mac).