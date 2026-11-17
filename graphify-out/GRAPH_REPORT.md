# Graph Report - domina  (2026-11-16)

## Corpus Check
- 181 files · ~178,893 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 55 file(s) not represented in the graph (top: .jsonl 37, (none) 6, .xlsm 3)

## Summary
- 1865 nodes · 4947 edges · 159 communities (92 shown, 67 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 652 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef737353`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- ref_child_process
- Escopo do Protótipo
- E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita
- 0004_calendario.py
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- api
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Correcao
- app/logs.py
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- test_fluxo_envio.py
- Custo Variável de IA/OCR
- Dependência: Hash de Senha
- Dependência: Pydantic
- Cautela sobre Estimativas
- gemini.py
- Dependência: FastAPI
- Dependência: Google Cloud Vision
- Dependência: psycopg2
- Dependência: PyJWT
- Dependência: python-multipart
- Dependência: SQLAlchemy
- Dependência: Uvicorn
- Ponto em Aberto: Índices
- Login Social
- Integração com AVAs
- Transparência sobre IA
- Peso de Evidências Recentes
- Priorização de Recomendações
- Sem Ranking Público
- Gamificação Não Bloqueia
- Transparência de Classificação
- Amostra Mínima de Tendência
- Direitos sobre Material Didático
- Descontos para Pilotos
- RNF: Tempo de Correção
- RNF: Carregamento de Telas
- RNF: Tempo de OCR
- RNF: Consistência da IA
- RNF: Explicabilidade da Nota
- RNF: Criptografia
- RNF: Gestão de Segredos
- RNF: Disponibilidade
- RNF: Backup Diário
- RNF: Fila Assíncrona
- RNF: Usabilidade
- RNF: Acessibilidade
- RNF: Observabilidade
- Domina
- PerfilEnum
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- correcao.py
- uuid
- rodar_agente
- test_exatas.py
- dominio.ts
- Admin.tsx
- routers/calendario.py
- Documentação do frontend Domina
- App.tsx
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- questoes.py
- api.ts
- compilerOptions
- seguranca.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- Calendar.tsx
- token
- E10 Privacidade e operação — LGPD, auditoria e custo
- main.py
- vercel.json
- registrar
- atividades.ts
- main.tsx
- test_agente.py
- E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA
- pydantic
- vite-env.d.ts
- pathlib
- routers/metas.py
- CLAUDE.md: domina, correção de redação do ENEM por IA
- frontend/README.md
- LGPD (Lei Geral de Proteção de Dados)
- exercicios.py
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- Histórico das versões do prompt de correção (v1 a v21)
- Turma
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh
- routers/estudos.py
- Domina · Frontend
- devDependencies
- analisa_externa.py
- 5. Mapa de telas e funcionalidades
- Usuario
- test_exercicios.py
- json
- variantes.py
- DocumentoBase
- dev.sh
- test_atividades.py
- Logs.tsx
- monta_base_externa.py
- models/usuario.py
- Logs do sistema
- Metas.tsx
- 0010_submissao_pagina.py
- dependencies
- test_estudos.py
- scripts
- test_metas.py
- test_logs.py
- @playwright/test
- _gemini_falso
- usePwa.ts
- App
- alembic
- sqlalchemy
- typing
- test_agente_que_parou_sem_correcao_tenta_de_novo_ao_clicar
- test_calendario.py
- CampoComSimbolos.tsx
- 3. Versão por versão
- analisa.py
- 6. Fluxos e estados
- Validação do frontend
- ref_fs
- ref_os
- ref_path
- ref_url

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 163 edges
2. `PerfilEnum` - 74 edges
3. `request()` - 74 edges
4. `token()` - 49 edges
5. `Atividade` - 45 edges
6. `Materia` - 41 edges
7. `Tema` - 39 edges
8. `Turma` - 34 edges
9. `registrar()` - 33 edges
10. `Submissao` - 32 edges

## Surprising Connections (you probably didn't know these)
- `2.1 Redação: o prompt (versão v14)` --references--> `ResultadoIA`  [INFERRED]
  README.md → backend/app/correcao.py
- `Visão geral do fluxo` --references--> `TipoMateriaEnum`  [INFERRED]
  README.md → backend/app/models/enum.py
- `2.4 Nota total e status` --references--> `corrigir_submissao()`  [INFERRED]
  README.md → backend/app/routers/correcoes.py
- `3.2 O que a API devolve` --references--> `CorrecaoResponse`  [INFERRED]
  README.md → backend/app/schemas/submissao.py
- `3.1 O que a IA devolve` --references--> `ResultadoExatasIA`  [INFERRED]
  README.md → backend/app/correcao_exatas.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **domina backend dependencies** — backend_requirements_fastapi, backend_requirements_uvicorn, backend_requirements_sqlalchemy, backend_requirements_psycopg2_binary, backend_requirements_pydantic_settings, backend_requirements_pydantic, backend_requirements_pyjwt, backend_requirements_passlib, backend_requirements_bcrypt, backend_requirements_google_cloud_vision, backend_requirements_python_multipart [EXTRACTED 1.00]
- **Ciclo central do produto Domina (corrigir-diagnosticar-recomendar-evoluir)** — docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_produto_domina, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_corrigir, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_diagnosticar, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_recomendar, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_mostrar_evolucao [EXTRACTED 1.00]
- **Pipeline de arquitetura de alto nível do Domina (9 componentes + base comum)** — docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_material_base, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_base_da_materia, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_envio, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_ocr, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_correcao_por_ia, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_professor_revisa, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_paineis, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_recomendacao, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_motor_de_dominio [EXTRACTED 1.00]
- **Equipe do Protótipo (Hackathon, 4 pessoas / 24 dias)** — docs_plano_prototipo_igor, docs_plano_prototipo_gustavo, docs_plano_prototipo_joao_pedro, docs_plano_prototipo_lucas, docs_plano_prototipo_divisao_por_pessoa [EXTRACTED 1.00]
- **Caminho para melhorar a correção por IA (medir → few-shot → RAG → fine-tuning)** — docs_decisoes_2026_10_13_correcao_ia_calibracao_calibracao_30_50_redacoes, docs_decisoes_2026_10_13_correcao_ia_calibracao_few_shot, docs_decisoes_2026_10_13_correcao_ia_calibracao_rag, docs_decisoes_2026_10_13_correcao_ia_calibracao_fine_tuning [EXTRACTED 1.00]
- **Conformidade LGPD e privacidade de dados de menores no Domina** — docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_19, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_20, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_21, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_22, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rnf_10, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rnf_11, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_risco_dados_menores [INFERRED 0.85]
- **Fluxo de Correção, Revisão e Diagnóstico de Domínio** — docs_plano_prototipo_motor_de_correcao, docs_plano_prototipo_revisao_do_professor, docs_plano_prototipo_motor_de_diagnostico_de_dominio, docs_plano_prototipo_painel_de_dominio_do_aluno [INFERRED 0.85]

## Communities (159 total, 67 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.08
Nodes (31): AuditLog, CustoUso, Escola, Exercicio, ExercicioResposta, Ponto em aberto: particionamento de AuditLog e CustoUso, Turma, Usuario (+23 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.06
Nodes (47): initialActivities, ActivityDetail(), alternativasDe(), BarraAtividade(), compoeEnunciado(), destacarTrechos(), EditarAtividade(), FiguraQuestao() (+39 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (25): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Últimos 2–3 Dias — Buffer, Chamadas de IA Síncronas (sem fila), Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Escopo do Protótipo, Fila Assíncrona (Celery) — fora de escopo (+17 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.13
Nodes (16): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), Ponto em aberto: segunda matéria do MVP restrita às matérias do segundo dia do ENEM, RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP) (+8 more)

### Community 7 - "Relatório: teste de calibração da correção (14/10/2026)"
Cohesion: 0.14
Nodes (18): Calibração com 30–50 redações de nota conhecida (erro médio e viés por competência), Decisão em aberto: prompt × RAG × fine-tuning (conversar com o Igor), Correção por IA: calibração e decisão RAG/fine-tuning (13/10/2026), Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir), Opção 1: prompt com exemplos corrigidos (few-shot), Laboratório /laboratorio/ (foto → texto → nota), Opção 2: RAG com redações corrigidas parecidas, Teste: redação ENEM 2023 do Igor (oficial 880; IA 600 → 680) (+10 more)

### Community 8 - "api"
Cohesion: 0.07
Nodes (27): build, depends_on, env_file, environment, ports, volumes, condition, environment (+19 more)

### Community 9 - "E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios"
Cohesion: 0.17
Nodes (13): E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios, RF-28 (Recomendação): Indicar ao aluno os temas prioritários de estudo com base nas lacunas, RF-29 (Recomendação): Sugerir exercícios direcionados a cada lacuna, a partir de um banco etiquetado por tema e habilidade, RF-30 (Recomendação): Gerar exercícios novos com IA para a turma, sujeitos à aprovação do professor antes de circular, RF-46 (Recomendação): Aluno gera exercício de prática individual sob demanda, ancorado na base aprovada da matéria, sem aprovação prévia do professor, RF-47 (Recomendação): Gerar material de estudo (resumo ou mapa mental) a partir do conteúdo da matéria, para download, RN-13 (Recomendação): Exercícios gerados por IA para a turma só chegam ao aluno depois de aprovados por um professor; exercícios gerados sob demanda pelo próprio aluno seguem a RN-28, RN-28 (Recomendação): O aluno pode gerar exercício de prática individual sem aprovação prévia do professor, desde que ancorado na base aprovada da matéria; o exercício é identificado como gerado por IA, sem revisão (+5 more)

### Community 10 - "Diagnóstico de Domínio"
Cohesion: 0.20
Nodes (10): E6 Diagnóstico de domínio — Estimar o domínio por tema e mostrar a evolução, RF-24 (Domínio): Cada correção aprovada atualiza a estimativa de domínio do aluno nos temas e habilidades avaliados, RF-25 (Domínio): Exibir domínio em percentual por tema, com o número de evidências que o sustenta, RF-26 (Domínio): Histórico de evolução do domínio por tema ao longo do tempo, RF-27 (Domínio): Agregar domínio por turma e por escola, RN-08 (Domínio): O domínio por tema só aparece em percentual quando há um mínimo de evidências (número a definir); abaixo disso, "poucos dados", RN-09 (Domínio): Só correções aprovadas pelo professor entram no cálculo do domínio, US-20 (MVP): Como aluno, quero ver meu domínio por tema em percentual com o número de evidências, para não confiar em número com pouco dado (+2 more)

### Community 11 - "Tendências do ENEM"
Cohesion: 0.20
Nodes (10): E9 Tendências — Recorrência histórica de assuntos do ENEM, Ponto em aberto: conferir licença e formato dos dados públicos do ENEM e de outros vestibulares, RF-31 (Recomendação): Cruzar a lacuna do aluno com a recorrência do tema em provas passadas para priorizar, RF-36 (Tendências): Ingerir provas públicas do ENEM e de outros vestibulares (UFG, UFU, FUVEST, UEG) e classificar as questões por assunto e gênero textual, RF-37 (Tendências): Calcular o índice de recorrência (frequência, nº de provas, recência, consistência) e classificar em 4 categorias, RF-38 (Tendências): Exibir por assunto o nível de atenção, as evidências históricas e o grau de confiança, nunca como probabilidade de cair, RF-39 (Tendências): Indicar alta ou queda de frequência só com amostra suficiente; senão, avisar que não há tendência confiável, US-30 (Piloto): Como estudante, quero ver os assuntos do ENEM classificados por recorrência histórica, para priorizar meu tempo (+2 more)

### Community 12 - "Correcao"
Cohesion: 0.16
Nodes (19): Atividade, Correcao, CorrecaoCriterio, DocumentoBase, DominioAluno, Materia, Submissao, Tema (+11 more)

### Community 13 - "app/logs.py"
Cohesion: 0.12
Nodes (17): configurar_logging(), ip_do_cliente(), JsonFormatter, novo_request_id(), Request, Logging do sistema: JSON em stdout (uma linha por evento) + contexto da…, IP real. Atras do proxy (Railway, Nginx) o IP do socket e o do proxy; o real…, access_log() (+9 more)

### Community 14 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (6): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos, Risco: capacidade de execução (equipe de quatro, ainda validando divisão de papéis), Risco: dependência de poucos pilotos

### Community 15 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 16 - "Modelo de Cobrança"
Cohesion: 0.67
Nodes (3): Ponto em aberto: definição de "aluno ativo" para cobrança, Ponto em aberto: preço (rascunho R$1.000 fixos + R$8/aluno, sem validação), RN-24 (Comercial): Cobrança proposta: mensalidade fixa por escola mais valor por aluno ativo por mês. Rascunho: R$ 1.000 fixos + R$ 8 por aluno; ainda não validado

### Community 17 - "test_fluxo_envio.py"
Cohesion: 0.19
Nodes (17): Exception, TextoPublicado, atividade_id(), Fluxo do aluno: login -> envia foto -> OCR (falso) -> confirma texto. cd…, test_aluno_gera_propria_correcao_e_professor_aprova_depois(), test_falha_do_gemini_nao_vaza_detalhe(), test_fluxo_completo(), test_imagem_sem_texto_responde_422() (+9 more)

### Community 18 - "Custo Variável de IA/OCR"
Cohesion: 0.67
Nodes (3): Risco: custo variável de LLM e OCR por correção acima do previsto, RN-26 (Comercial): O valor por aluno deve superar o custo variável de IA e OCR por aluno; o preço só fecha depois de medir o custo real, RNF-17 (Custo): Custo variável por correção monitorado e abaixo do valor cobrado por aluno

### Community 23 - "gemini.py"
Cohesion: 0.12
Nodes (18): corrigir(), BaseModel, field_validator, QuestaoCorrigida, Correcao de exercicios de materias exatas (matematica, fisica, quimica) pelo…, ResultadoExatasIA, _client(), extract_text() (+10 more)

### Community 58 - "Domina"
Cohesion: 0.07
Nodes (30): finalizar(), ler_envio(), AgenteRequest, AgenteResponse, ExercicioResumo, BaseModel, CorrecaoResponse, 1. O que é o Domina (+22 more)

### Community 59 - "PerfilEnum"
Cohesion: 0.12
Nodes (33): escola_do_escopo(), exigir_perfil(), UUID, Dependencia: so deixa passar quem tem um dos perfis., Escola sobre a qual a consulta vale. E AQUI que o RBAC acontece, no backend. -…, Session, registrar_uso(), PerfilEnum (+25 more)

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.12
Nodes (17): Achado: confiança da IA não serve (0,93–0,96 mesmo errando 500 pontos), E4 Correção por IA — Nota estimada, feedback e nível de confiança, Ponto em aberto: correção por gabarito (RF-18) — resolvido, tornou-se obrigatório no MVP, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção (+9 more)

### Community 61 - "correcao.py"
Cohesion: 0.16
Nodes (14): CaixaIA, CompetenciaIA, corrigir(), PontoIA, BaseModel, field_validator, Correcao da redacao ENEM pelo Gemini nas 5 competencias do INEP. A nota fica…, ResultadoIA (+6 more)

### Community 62 - "uuid"
Cohesion: 0.17
Nodes (15): criar_usuario(), listar_usuarios(), meu_usuario(), get, post, Session, UUID, _resposta() (+7 more)

### Community 63 - "rodar_agente"
Cohesion: 0.43
Nodes (8): AgenteExecucao, get, post, Session, UUID, _resposta(), rodar_agente(), ver_agente()

### Community 64 - "test_exatas.py"
Cohesion: 0.26
Nodes (17): criar_atividade_com_gabarito(), criar_turma_e_materia(), _gemini_falso(), Correcao de exercicios de materias exatas (matematica/fisica/quimica): gabarito…, test_aluno_gera_propria_correcao_exatas_e_professor_aprova_depois(), test_aprovar_exige_todos_os_criterios(), test_atividade_de_exatas_exige_gabarito(), test_enunciado_longo_nao_quebra_a_criacao() (+9 more)

### Community 65 - "dominio.ts"
Cohesion: 0.38
Nodes (6): Evolution(), dominioMeu(), evolucaoMinha(), carregarDominioReal(), Recomendacao, recomendar()

### Community 66 - "Admin.tsx"
Cohesion: 0.11
Nodes (27): BlocosResumo(), brl(), EditarEscola(), Equipe(), Escolas(), ListaContas(), mb(), mesAtual() (+19 more)

### Community 67 - "routers/calendario.py"
Cohesion: 0.15
Nodes (29): feriados(), _pascoa(), date, Feriados nacionais do Brasil de um ano, calculados (nao precisam de manutencao…, Evento, Calendario da escola: uma tabela so, todo mundo le dela (por isso fica…, apagar_evento(), criar_evento() (+21 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.22
Nodes (9): 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual, 7. Persistência e contratos, 9. Usabilidade e acessibilidade (+1 more)

### Community 69 - "App.tsx"
Cohesion: 0.11
Nodes (39): navItems, EvolutionChart(), RealSparkline(), InstallBanner(), Badge(), Button(), Card(), Empty() (+31 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (13): Banco compartilhado + escola_id + RLS (estratégia escolhida), Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados (+5 more)

### Community 71 - "package.json"
Cohesion: 0.15
Nodes (13): name, private, type, version, prettier, react-native-web, @types/react, @types/react-dom (+5 more)

### Community 72 - "questoes.py"
Cohesion: 0.18
Nodes (20): extract_text_from_image(), ler_imagem(), post, Session, UploadFile, anexar_figura(), _apagar_arquivo(), _pode_editar() (+12 more)

### Community 73 - "api.ts"
Cohesion: 0.05
Nodes (76): erroDe(), ExerciciosProfessor(), FormExercicio(), LinhaResposta(), Rascunho, RespostasExercicio(), ResumoTurma(), vazio (+68 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "seguranca.py"
Cohesion: 0.18
Nodes (19): hash_de(), proximo_elo(), Session, Cadeia de hash compartilhada pelos logs append-only (evento_seguranca e…, (seq, hash_anterior) da proxima linha. Chamar DEPOIS de ter definido os campos…, Confere a cadeia inteira; devolve (integra, mensagem com a primeira quebra)., verificar(), EventoSeguranca (+11 more)

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 77 - "Calendar.tsx"
Cohesion: 0.14
Nodes (21): Modal(), iso(), useCalendario(), br(), Calendar(), apagar(), cobre(), MESES (+13 more)

### Community 78 - "token"
Cohesion: 0.29
Nodes (16): test_admin_precisa_da_escola_e_feriados_calculados(), test_telas_de_log_so_para_quem_pode_e_gestor_so_ve_a_propria_escola(), escola_id(), novo(), Administrador x Gestor: o isolamento por escola e garantido no backend (RBAC),…, test_admin_cria_escola_gestor_e_professor(), test_admin_lista_turmas_da_escola_e_cria_conta_nela(), test_admin_ve_cada_escola_e_o_total() (+8 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (13): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+5 more)

### Community 80 - "main.py"
Cohesion: 0.11
Nodes (30): confirmar_senha(), escola_inativa(), get_current_user(), Session, Reautenticacao em acao sensivel: o JWT roubado/esquecido aberto nao basta, pede…, create_access_token(), decode_access_token(), verify_password() (+22 more)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "registrar"
Cohesion: 0.11
Nodes (29): _campos(), Session, Log de auditoria (quem fez o que sobre quais dados), append-only e com cadeia…, registrar(), verificar_auditoria(), AuditLog, editar_atividade(), excluir_atividade() (+21 more)

### Community 83 - "atividades.ts"
Cohesion: 0.27
Nodes (12): Activities(), Dashboard(), listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData() (+4 more)

### Community 84 - "main.tsx"
Cohesion: 0.33
Nodes (5): frontend_src_styles, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, react-dom

### Community 85 - "test_agente.py"
Cohesion: 0.24
Nodes (8): Roda o agente de verdade (Claude + Gemini, GASTA API) num banco temporario e…, atividade_id(), Agente de correcao: o Claude (falso aqui) escolhe as ferramentas e o passo a…, test_agente_decide_os_passos_e_grava_o_passo_a_passo(), Evolucao real por materia: historico de correcoes aprovadas, agrupado por…, fastapi_testclient, os, tempfile

### Community 86 - "E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA"
Cohesion: 0.15
Nodes (14): Opção 3: fine-tuning com pares nota_ia × nota_professor, E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA, Ponto em aberto: LLM própria — resolvido (não treinar modelo do zero), RF-20 (Revisão): Nenhuma correção é liberada ao aluno sem aprovação do professor, RF-21 (Revisão): Professor edita nota e feedback e aceita ou rejeita a sugestão por critério, RF-22 (Revisão): Guardar a nota da IA e a nota final do professor, para medir concordância, Risco: correção de IA errada ou inconsistente, RN-01 (Revisão humana): Nenhuma nota ou feedback gerado pela IA é exibido ao aluno sem aprovação do professor responsável (+6 more)

### Community 87 - "pydantic"
Cohesion: 0.09
Nodes (28): integridade(), logs_auditoria(), logs_seguranca(), _periodo(), date, get, Session, UUID (+20 more)

### Community 89 - "pathlib"
Cohesion: 0.30
Nodes (7): Roda calibra.py com prompt de arquivo na planilha externa. uso (de backend/):…, Roda calibra.py com prompt de arquivo na base INEP (nota oficial). uso (de…, Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da…, Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da…, openpyxl, pathlib, runpy

### Community 90 - "routers/metas.py"
Cohesion: 0.08
Nodes (57): avaliar_metas(), metas_do_aluno(), nivel_de(), pontos_do_aluno(), progresso(), Session, Metas ativas que valem para o aluno: da escola toda, das turmas dele ou so dele., Quanto o aluno ja fez, na mesma unidade de meta.alvo (quantidade ou percentual). (+49 more)

### Community 91 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (8): Ponto em aberto: retenção de conteudo_bruto, LGPD (Lei Geral de Proteção de Dados), Ponto em aberto: RN-21 (dados não usados para treinar modelos de terceiros) mantida, pendente confirmação do usuário, Risco: dados de menores de idade (legal e reputacional), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

### Community 94 - "exercicios.py"
Cohesion: 0.09
Nodes (67): BaseModel, IA ajudando o PROFESSOR a criar exercicios de pratica: rascunhos sobre um tema…, _RespostaExemplo, _RespostaSugestao, sugerir_exercicios(), sugerir_resposta_exemplo(), SugestaoExercicio, Exercicio (+59 more)

### Community 95 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 (leia primeiro) — ENTREGA DO PROJETO É HOJE, 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos (versão de 19/10; vale o que está na seção 0), 6. Prompt atual (v9), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 96 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 (leia primeiro) — ENTREGA DO PROJETO É HOJE, 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos (versão de 19/10; vale o que está na seção 0), 6. Prompt atual (v9), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 97 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.22
Nodes (8): 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos, 6. Prompt atual (v9), CLAUDE.md: domina, correção de redação do ENEM por IA, graphify

### Community 98 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.22
Nodes (8): 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos, 6. Prompt atual (v9), CLAUDE.md: domina, correção de redação do ENEM por IA, graphify

### Community 99 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.22
Nodes (8): 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos, 6. Prompts, CLAUDE.md: domina, correção de redação do ENEM por IA, graphify

### Community 100 - "Histórico das versões do prompt de correção (v1 a v21)"
Cohesion: 0.33
Nodes (6): 1. Como ler os números, 2. Tabela resumo, 4. O que aprendemos, 5. Conclusão, Histórico das versões do prompt de correção (v1 a v21), Onde estão os arquivos

### Community 101 - "Turma"
Cohesion: 0.41
Nodes (12): UsuarioTurmaPapelEnum, Turma, UsuarioTurma, criar_turma(), matricular(), membros_turma(), minhas_turmas(), get (+4 more)

### Community 109 - "routers/estudos.py"
Cohesion: 0.06
Nodes (69): Anthropic, ErroFerramenta, Ferramenta, Exception, Agente de correcao: o Claude recebe um objetivo e decide sozinho quais…, Erro esperado de uma ferramenta: volta para o agente como resultado com…, Roda o loop ate o agente chamar a ferramenta de fim (terminou() vira True) ou…, _resumo() (+61 more)

### Community 110 - "Domina · Frontend"
Cohesion: 0.18
Nodes (11): Comandos, Conexão com o backend, Documentação, Domina · Frontend, Executar, Experimente o fluxo, O agente de correção na tela, O que o frontend faz (+3 more)

### Community 111 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, @playwright/test, prettier, @types/react, @types/react-dom, @types/react-native-web, typescript, vite (+3 more)

### Community 112 - "analisa_externa.py"
Cohesion: 0.38
Nodes (5): csv, pearson(), ranks(), Compara a IA com as notas humanas da base externa (AES-ENEM com 3 humanos,…, spearman()

### Community 113 - "5. Mapa de telas e funcionalidades"
Cohesion: 0.33
Nodes (6): 5. Mapa de telas e funcionalidades, Acesso demonstrativo, Aluno, Compartilhadas, Gestor, Professor

### Community 114 - "Usuario"
Cohesion: 0.09
Nodes (59): avaliar_seguro(), Chamada depois de um envio/aprovacao: sessao propria e nunca derruba a…, Folhas de um envio por foto, em ordem (ordem 0 = primeira). Envio antigo, de…, SubmissaoPagina, Usuario, ocr(), _atividade_response(), caminhos_da_submissao() (+51 more)

### Community 115 - "test_exercicios.py"
Cohesion: 0.36
Nodes (10): _objetivo(), Exercicios do professor: criar (objetivo/discursivo), IA sugere rascunhos,…, _setup(), test_aluno_ve_so_da_turma_e_gabarito_depois_de_responder(), test_criar_validacoes_e_permissoes(), test_discursivo_com_varias_respostas_de_exemplo(), test_editar_e_excluir_somem_para_o_aluno(), test_exercicio_so_para_alguns_alunos() (+2 more)

### Community 116 - "json"
Cohesion: 0.15
Nodes (10): Mede a correcao da IA contra notas conhecidas, via Groq (gratis). Nao altera o…, Mede a correcao da IA contra notas conhecidas (so texto, sem OCR). Nao altera o…, Confere a cadeia de hash dos dois logs. python verificar_logs.py (sai com…, Compara a IA com a nota oficial do INEP. uso: python analisa_inep.py <ia.jsonl>…, Roda corrigir() do app (v12, 2 correcoes + media) nas 53 do INEP. uso (de…, google_genai, httpx, json (+2 more)

### Community 117 - "variantes.py"
Cohesion: 0.27
Nodes (8): CompetenciaV3, para_v2(), pegar(), BaseModel, Variantes de prompt para o teste de calibracao (nao fazem parte do projeto)., ResultadoV3, _v3b(), random

### Community 118 - "DocumentoBase"
Cohesion: 0.23
Nodes (12): StatusProcessamentoEnum, TipoDocumentoEnum, DocumentoBase, enviar_documento(), listar_documentos(), get, post, Session (+4 more)

### Community 120 - "test_atividades.py"
Cohesion: 0.24
Nodes (19): _lote(), _objetiva(), Professor com varias turmas: lancar em lote, editar e excluir/arquivar…, Um professor PROPRIO deste teste (nao mexe no do seed, que os outros testes…, _setup(), test_atividade_sem_autor_nao_aparece_para_professor_so_para_gestor(), test_depois_do_primeiro_envio_so_titulo_e_prazo_mudam(), test_editar_titulo_prazo_e_gabarito_enquanto_ninguem_enviou() (+11 more)

### Community 121 - "Logs.tsx"
Cohesion: 0.22
Nodes (13): Aba, hora(), Logs(), verificar(), TIPOS, TOM(), AuditoriaAPI, consulta() (+5 more)

### Community 122 - "monta_base_externa.py"
Cohesion: 0.12
Nodes (15): ast, gerar(), collections, copy, norm(), notas(), palavras(), Monta essays/base_redacoes_segunda.xlsm a partir da original (molde) com… (+7 more)

### Community 123 - "models/usuario.py"
Cohesion: 0.12
Nodes (53): hash_password(), garantir_competencias(), Session, As 5 competencias da redacao do ENEM (INEP). Cada uma vira um Tema da materia…, Cria (sem commit) as competencias que faltam na materia. Repetir nao duplica., _detalhe(), Session, Onde o aluno erra em exatas. Le as correcoes APROVADAS e guarda cada questao em… (+45 more)

### Community 124 - "Logs do sistema"
Cohesion: 0.29
Nodes (6): Acesso, Integridade, Logs do sistema, O que existe e onde fica, Railway (testes), VPS (depois)

### Community 125 - "Metas.tsx"
Cohesion: 0.13
Nodes (23): br(), EditarMeta(), MetaLinha(), Metas(), MetasAluno(), MetasEquipe(), NovaMeta(), Ranking() (+15 more)

### Community 127 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, lucide-react, react, react-dom, react-native-web

### Community 128 - "test_estudos.py"
Cohesion: 0.25
Nodes (14): _claude_falso(), _com_claude_falso(), gerar_contado(), _limpar_pratica(), Plano de estudo: POST /estudos/meu/gerar gera exercicios (GET /estudos/meu so…, Apaga exercicios/respostas do aluno (outros testes do mesmo banco, como o do…, test_gera_salva_e_nao_regera_enquanto_ha_pendentes_sem_vazar_gabarito(), test_meta_de_pratica_conclui_ao_responder() (+6 more)

### Community 129 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, format, preview, test, test:e2e

### Community 130 - "test_metas.py"
Cohesion: 0.36
Nodes (11): _entregar_objetiva(), _meta(), Niveis e metas: escopo (escola/turma/aluno), conclusao automatica, nivel por…, Turma, professor e dois alunos PROPRIOS deste teste (nao mexe nos do seed)., Cria uma prova objetiva de 1 questao na turma e o aluno acerta (correcao nasce…, _setup(), test_editar_arquivar_e_pontos_ficam(), test_escopo_e_permissoes_de_criacao() (+3 more)

### Community 131 - "test_logs.py"
Cohesion: 0.27
Nodes (10): _eventos(), Access log em JSON, eventos de seguranca no banco e IP atras de proxy., test_403_vira_acesso_negado_com_usuario_e_request_id(), test_acao_sensivel_pede_a_senha_de_novo(), test_access_log_json_sem_query_string_nem_token(), test_auditoria_guarda_escola_ip_e_entra_na_cadeia(), test_ip_so_vem_do_proxy_quando_configurado(), ip_da_falha() (+2 more)

### Community 133 - "_gemini_falso"
Cohesion: 0.40
Nodes (5): _gemini_falso(), gerar(), test_evolucao_agrupa_por_materia_sem_tocar_dominio(), test_evolucao_so_para_aluno(), token()

### Community 134 - "usePwa.ts"
Cohesion: 0.36
Nodes (6): 8. PWA, Instalação, InstallEvent, isStandalone(), usePwa(), wasDismissed()

### Community 135 - "App"
Cohesion: 0.22
Nodes (11): App(), iniciais(), clearToken(), login(), logout(), me(), perfilParaRole(), setToken() (+3 more)

### Community 137 - "sqlalchemy"
Cohesion: 0.29
Nodes (3): alembic_config, Aplica as migracoes do Alembic. Banco que ja existia (criado pelo create_all…, sqlalchemy

### Community 139 - "test_agente_que_parou_sem_correcao_tenta_de_novo_ao_clicar"
Cohesion: 0.29
Nodes (8): _chamada(), _cliente_roteirizado(), O bug do botao 'nada acontece': o agente parou sem corrigir e o clique seguinte…, test_agente_nao_roda_de_novo_sem_refazer(), test_agente_que_cai_ainda_entrega_a_correcao(), test_agente_que_parou_sem_correcao_tenta_de_novo_ao_clicar(), test_sinalizar_nao_grava_sozinho_se_o_agente_cai(), token()

### Community 140 - "test_calendario.py"
Cohesion: 0.44
Nodes (9): _evento(), Calendario por escola: todos da escola veem o mesmo dado; o resto e RBAC no…, test_aluno_nao_ve_evento_de_turma_alheia_e_feriado_vem_pronto(), test_evento_da_escola_toda_aparece_para_todos_e_nao_vaza_para_outra_escola(), test_lembrete_do_aluno_e_so_dele(), test_professor_nao_apaga_evento_do_gestor_mas_gestor_apaga_o_dele(), test_professor_so_cria_para_a_propria_turma(), _titulos() (+1 more)

### Community 142 - "CampoComSimbolos.tsx"
Cohesion: 0.32
Nodes (5): CampoComSimbolos(), GRUPOS, inserirNoCursor(), Props, vitest

### Community 145 - "3. Versão por versão"
Cohesion: 0.33
Nodes (6): 3. Versão por versão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10), Fase 4: base INEP de 53 redações, foco na C3 (19/10), Fase 5: dia da entrega (20/10)

### Community 147 - "analisa.py"
Cohesion: 0.60
Nodes (4): pearson(), ranks(), score(), statistics

### Community 148 - "6. Fluxos e estados"
Cohesion: 0.40
Nodes (5): 6. Fluxos e estados, Envio e aprovação, Navegação, Prática, Texto e arquivo

### Community 149 - "Validação do frontend"
Cohesion: 0.40
Nodes (4): Limites da validação, Roteiro manual, Validação do frontend, Verificação automatizada

## Knowledge Gaps
- **317 isolated node(s):** `dev.sh script`, `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script`, `roda_v12.sh script` (+312 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 632 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `4. O que já foi feito (em ordem)` connect `Domina` to `DocumentoBase`?**
  _High betweenness centrality (0.255) - this node is a cross-community bridge._
- **Why does `ResultadoMini()` connect `Domina` to `App.tsx`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Why does `DocumentoBase` connect `DocumentoBase` to `main.py`, `PerfilEnum`, `Domina`, `models/usuario.py`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Are the 131 inferred relationships involving `Usuario` (e.g. with `registrar()` and `confirmar_senha()`) actually correct?**
  _`Usuario` has 131 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `PerfilEnum` (e.g. with `escola_do_escopo()` and `exigir_perfil()`) actually correct?**
  _`PerfilEnum` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `Atividade` (e.g. with `registrar_erros()` and `progresso()`) actually correct?**
  _`Atividade` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `dev.sh script`, `roda_dupla.sh script`, `roda_v10.sh script` to the rest of the system?**
  _317 weakly-connected nodes found - possible documentation gaps or missing edges._