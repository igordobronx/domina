# CLAUDE.md: Domina

Atualizado em 15/11/2026 (fim da tarde). Responda sempre em português, de forma curta e simples, sem números difíceis.
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
- **Branch de trabalho: `domina-ciclo-2`.** Só fazer merge na `main` quando o usuário mandar. A `main` tem a correção da redação pelo Claude Sonnet.
- **Backend:** `backend/` (FastAPI + SQLAlchemy + Alembic, Python). **Frontend:** `frontend/` (React + Vite + TypeScript, PWA, deploy no Vercel com Root Directory `frontend`). Docs do frontend: `frontend/docs/FRONTEND.md`.
- **Banco:** Postgres no docker (porta **5433**) por padrão; SQLite é o fallback (testes usam SQLite temporário). Migrations em `backend/migrations/versions/` (0001 a 0018).
- **Subir tudo:** `./dev.sh` na raiz (banco + API na 8000 + site na 5173; já roda `migrar.py`; `./dev.sh --seed` roda o seed antes). A API e o site recarregam sozinhos quando o código muda; **só mudança de banco exige parar (Ctrl+C) e rodar `./dev.sh` de novo** (ou `cd backend && ../venv/bin/python migrar.py` em outro terminal).
- **Logins do seed** (senha `senha123`): `professor@domina.com` (Beto Andrade, turma "3º Ano A"), `gestor@domina.com`, `admin@domina.com`, `gestor2@domina.com` (outra escola), alunos `aluno@domina.com` (Ana Beatriz), `aluno2@domina.com` (Bruno), `aluno3@domina.com` (Carla).
- **Chaves** em `backend/.env` (fora do git; nunca imprimir nem commitar): `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`. No cloud environment do projeto a `GEMINI_API_KEY` já existe.
- **Modelos:** redação e agente = Claude Sonnet (`claude-sonnet-5-5`); exercícios gerados pela IA = Claude Haiku (`claude-haiku-5-5`); OCR e correção de exatas = Gemini (`gemini-3.5-flash`, reserva `gemini-3.5-flash-lite`). Camada única em `backend/app/llm/` e `backend/app/ocr/`.
- **Testes:** `cd backend && python -m pytest -q tests/test_X.py` (todos passam; rodar por arquivo). Frontend: `npx tsc --noEmit -p .`, `npm test` (1 teste já falhava antes: "não abre a revisão por um link do gestor") e `npm run test:e2e` (Playwright).
- **graphify:** usar sempre (regra do projeto). Antes de explorar: `graphify query "<pergunta>"`. Depois de editar código: `graphify update .`. Não commitar o cache de `graphify-out/cache`.

## 3. Regras de trabalho (preferências do usuário)

- Português, respostas curtas e simples.
- **Mudar o código direto no Mac** (pasta acima), via `device_bash` / `device_commit_files`. **Não fazer commit nem push a cada mudança: só quando o usuário pedir.** Nada de merge na `main` sem ele mandar. O push do container e do VM do Mac costuma falhar; se pedir push, ele roda `git push` no terminal dele.
- **Não gerar prints/imagens da tela a cada mudança.**
- Ao gravar planilha no Mac, pedir que esteja fechada no Excel. `device_commit_files` pode gravar versão antiga logo após `cp` em `/mnt/project-files` (cache): copiar com nome novo e conferir o `md5sum` dos dois lados.
- Nunca copiar nome/CPF de redação (planilhas só têm "Participante X - ano").
- Não chamar API paga sem confirmar. Uma mudança por vez no prompt da redação, **combinando antes** com o usuário (seção 5).
- Ao avisar que algo mudou, dizer em uma frase se precisa parar e rodar o `./dev.sh` de novo (só quando o banco mudou).

## 4. O que já foi feito (em ordem)

**Set a início de out/2026 (base):** esqueleto FastAPI; OCR de foto com Gemini (pula rasuras, não corrige o aluno, o aluno confere e confirma o texto); laboratório de testes (`/laboratorio/`); correção por IA; graphify; frontend inicial; docker-compose + seed.

**Calibração do prompt da redação (13 a 21/10):** v1 a v21, bases de teste e histórico em `docs/calibracao/` (resumo na seção 5).

**Backend (19 a 24/10):** cadastro de usuário, turmas e matrícula; atividade + upload de material (`DocumentoBase`); diagnóstico de **domínio por competência** (`dominio_aluno`); consentimento LGPD, custo de uso por escola e audit log; `GET /usuarios/me`; Postgres como padrão; evolução do aluno por matéria; recomendação de estudo; fila de revisão do professor; **correção de exatas** (matemática/física/química) por gabarito, com valor total da atividade dividido entre as questões, aceita foto; IA cita o trecho exato e vários acertos/erros por competência/questão; aluno gera e vê a própria correção da IA antes da aprovação do professor; correção da redação migrou para **Claude Sonnet**.

**Agente de correção (24/10, PR #2):** o Claude decide os passos (`ler_envio`, `pedir_nova_foto`, corretor certo, `consultar_historico_aluno`, `gerar_exercicios_reforco`, `sinalizar_professor`, `finalizar`), máx. 10 passos, grava log de auditoria e custo, e se cair no meio a correção direta ainda sai. Detalhes no README (`backend/app/agente.py`, `routers/agente.py`, tabela `agente_execucao`). README final em 24/10 ("protótipo final hackathon").

**Frontend (19 a 20/10):** login real (sem modo demonstração), telas com dados reais: Minhas atividades, Revisões (fila do professor, cria atividade), Evolução, Turmas (gestor cria turma, vê/matricula alunos), Plano de estudo real, backend ligado a toda UI.

**RBAC, calendário, logs (9 a 11/11):** admin x gestor com isolamento por escola no backend; **Alembic**; calendário por escola (prazos das atividades aparecem sozinhos); correção de exatas por foto; **logs do sistema** (access log, eventos de segurança, auditoria com cadeia de hash, tela, retenção; ver `docs/decisoes/logs-do-sistema.md`); reautenticação para ações sensíveis; agente com cache de prompt e `correcoes.py` separado de `submissoes.py`.

**Atividades (11/11 a 13/11):** lançar a mesma atividade em várias turmas, editar e excluir/arquivar (com envios, só arquiva); revisão do professor por turma; questões **objetivas** (alternativas A–E, correção na hora, sem IA); **várias fotos** por envio; barra de **símbolos** (química/matemática) nos campos; **metas e níveis** (gamificação: nível = soma de pontos das metas concluídas, sem nota; `docs/decisoes/gamificacao-niveis-e-metas.md`).

**Exercícios do professor (15/11):**
- Menu **Exercícios** para professor e aluno (ícone de caderno com lápis; a IA usa estrelinhas). Exercício é **prática, não vale nota** (prova continua em Atividades).
- **Aluno:** abas **"Para você (IA)"** (gerados na hora pelos pontos fracos, `/estudos/meu`) e **"Do professor"** (`/exercicios/turma`). Regra de separação: **quem publicou**; se o professor usou a IA, continua "do professor" e ganha o selo "Com ajuda da IA". O gabarito só aparece depois de responder.
- **Professor** (`frontend/src/screens/Exercicios.tsx`, `backend/app/routers/exercicios.py`, `exercicios_ia.py`, `schemas/exercicio.py`, tabelas `exercicio` e `exercicio_resposta`):
  - Criar: nome, matéria, tema, **turmas** (pode marcar várias: cada turma recebe a sua cópia; o formulário não mostra esse aviso) e "Para quem" (todos ou **alunos escolhidos**, inclusive de turmas diferentes; turma sem aluno marcado não recebe). Abas "Escrever eu mesmo" e "Pedir para a IA" (rascunhos que o professor revisa e salva; nada chega ao aluno sem salvar). Os seletores são botões com borda. **Nada vem pré-marcado**: turma e "Para quem" começam sem seleção (ao editar, vêm os valores salvos). **Objetivo só salva com a alternativa correta marcada** (botão desabilitado + aviso; o backend também recusa).
  - Objetivo: 2 a 6 alternativas, botão "Marcar esta como correta" e "Remover alternativa" em cada uma. Discursivo: **uma ou mais respostas de exemplo** (até 5; pelo menos uma), botão "IA sugere uma resposta".
  - Lista **separada por turma**; resumo por aluno (fez / acertou / parcial); "Ver respostas" por exercício com filtros Todos, Fizeram, Não fizeram. Objetivo: acerto automático. Discursivo: o professor marca **Certo / Parcial / Errado**; **parcial e errado exigem comentário** (backend recusa sem). O aluno vê o resultado, o comentário e as respostas de exemplo. Refazer apaga a correção antiga.
  - Migrations 0014 (campos do exercício), 0015 (`alunos`), 0016 (comentário), 0017 (`resultado`), 0018 (`respostas_exemplo`). Testes: `backend/tests/test_exercicios.py` (7).
- **Ajustes do aluno (15/11, noite):** só **uma resposta** por exercício (backend recusa a segunda com 409; sem "Tentar de novo"); texto de resultado só "Você acertou." / "Você errou."; alternativa marcada errada fica **vermelha** e a certa continua verde (professor e IA); selo **"Feito"** verde se acertou, vermelho se errou (amarelo se o professor marcou parcial); na aba IA o botão verde é sempre o primeiro exercício ainda não feito (a resposta fica guardada no navegador, por aluno, em `domina-ia-respostas:<id>`); botão "Carregar exercícios (usar pouco)"; menu lateral com "Exercícios" logo depois de "Visão geral" (igual ao do professor); discursiva do aluno com caixa "Responder" alinhada e botão "Enviar"; professor: só um botão Certo/Parcial/Errado fica marcado, e o cursor não fica "carregando" nos botões desabilitados. Sem mudança de banco.
- **Ajustes 2 (15/11, noite):** menu lateral voltou à ordem do aluno (Visão geral, Minhas atividades, Minha evolução, Exercícios, Calendário, Metas) e o professor segue a mesma ordem (Visão geral, Revisões, Turmas, Exercícios, Calendário, Metas, Materiais); selo "Feito" agora é neutro e o resultado aparece numa linha discreta com bolinha colorida (`ResultadoMini` em `Learning.tsx`); professor: Certo/Parcial/Errado e comentário **não salvam sozinhos**, há botão "Salvar" (e "Cancelar") que só aparece quando algo mudou; botão "Errado" sem vermelho no hover; "Como criar" ganhou mini título no formulário.
- **Ajustes 3 (15/11, noite):** professor, criar exercício: "Como criar" e "Tipo do exercício" (um só, vale para escrever e para IA) começam sem nada marcado e o resto do formulário só aparece depois de escolher os dois; botão "Salvar" da correção ficou verde-claro com borda verde e separado por uma linha (não confunde com "Certo"); aluno, aba "Do professor": o botão do cartão fica sempre no fim do cartão (classe `ex-prof`). Sem mudança de banco.
- **Estado no git:** o commit `0677bb6` (na `domina-ciclo-2`, enviado ao GitHub) tem só a primeira versão dos exercícios. **Tudo depois (migrations 0015 a 0018, "para quem", parcial, comentário, várias respostas de exemplo, lista por turma, ícone novo) está só na pasta do Mac, sem commit.**

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
