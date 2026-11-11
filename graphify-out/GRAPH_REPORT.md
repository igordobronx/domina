# Graph Report - domina  (2026-11-11)

## Corpus Check
- 149 files · ~148,656 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 54 file(s) not represented in the graph (top: .jsonl 37, (none) 6, .xlsm 3)

## Summary
- 1458 nodes · 3530 edges · 126 communities (78 shown, 48 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 417 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d689e839`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- test_rbac.py
- Escopo do Protótipo
- E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita
- typing
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- api
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Usuario
- main.py
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- app/agente.py
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
- CLAUDE.md: domina, correção de redação do ENEM por IA
- routers/painel.py
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- submissoes.py
- models/usuario.py
- routers/agente.py
- test_exatas.py
- Dashboard.tsx
- Admin.tsx
- Usuario
- Documentação do frontend Domina
- types.ts
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- questoes.py
- api.ts
- compilerOptions
- test_logs.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- Calendar.tsx
- test_fluxo_envio.py
- E10 Privacidade e operação — LGPD, auditoria e custo
- dependencies.py
- vercel.json
- escolas.py
- PerfilEnum
- App.tsx
- correcao.py
- atividades.ts
- routers/compliance.py
- vite-env.d.ts
- Domina
- auditoria.py
- Settings.tsx
- frontend/README.md
- LGPD (Lei Geral de Proteção de Dados)
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- Histórico das versões do prompt de correção (v1 a v21)
- routers/turma.py
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh
- test_agente.py
- Domina · Frontend
- variantes.py
- analisa_externa.py
- 5. Mapa de telas e funcionalidades
- 2. Lógica (o que o agente faz)
- routers/logs.py
- pathlib
- 6. Fluxos e estados
- routers/documento.py
- dev.sh
- routers/usuario.py
- Logs.tsx
- meus_exercicios
- datetime
- Logs do sistema
- config.py

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 104 edges
2. `PerfilEnum` - 56 edges
3. `request()` - 49 edges
4. `Atividade` - 34 edges
5. `Domina (plataforma de IA de correção e diagnóstico)` - 30 edges
6. `_ferramentas()` - 27 edges
7. `Escola` - 26 edges
8. `Turma` - 25 edges
9. `Materia` - 24 edges
10. `token()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Laboratório /laboratorio/ (foto → texto → nota)` --references--> `corrigir()`  [EXTRACTED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → backend/app/correcao.py
- `Prompt de correção v2 (descritores oficiais do INEP por nível)` --references--> `corrigir()`  [EXTRACTED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → backend/app/correcao.py
- `Prompt de correção v2 (descritores oficiais do INEP por nível)` --implements--> `E4 Correção por IA — Nota estimada, feedback e nível de confiança`  [INFERRED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf
- `test_nota_da_ia_vira_nivel_valido_do_enem()` --uses--> `ResultadoIA`  [INFERRED]
  backend/tests/test_fluxo_envio.py → backend/app/correcao.py
- `gerar()` --indirect_call--> `notas()`  [INFERRED]
  backend/tests/test_evolucao.py → docs/calibracao/2026-10-16/monta_base_externa.py

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

## Communities (126 total, 48 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.13
Nodes (17): AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend), Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança), IPE (piloto institucional desejado), João Pedro (Co-fundador; estatística, matemática e IA; ponte de entrada no CEIA via UFG) (+9 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.09
Nodes (39): ActivityDetail(), compoeEnunciado(), destacarTrechos(), FiguraQuestao(), ImagemComCaixas(), MATERIAS_COM_GABARITO, NOMES_FERRAMENTAS, NOTAS_ENEM (+31 more)

### Community 2 - "test_rbac.py"
Cohesion: 0.15
Nodes (29): feriados(), _pascoa(), date, Feriados nacionais do Brasil de um ano, calculados (nao precisam de manutencao…, _evento(), Calendario por escola: todos da escola veem o mesmo dado; o resto e RBAC no…, test_admin_precisa_da_escola_e_feriados_calculados(), test_aluno_nao_cria_e_professor_so_para_a_propria_turma() (+21 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (26): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Últimos 2–3 Dias — Buffer, Chamadas de IA Síncronas (sem fila), Correção de Redação do ENEM (5 competências INEP), Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Escopo do Protótipo (+18 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 5 - "typing"
Cohesion: 0.10
Nodes (4): Aplica as migracoes do Alembic. Banco que ja existia (criado pelo create_all…, sqlalchemy, sqlalchemy_dialects_postgresql, typing

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.13
Nodes (16): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), Ponto em aberto: segunda matéria do MVP restrita às matérias do segundo dia do ENEM, RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP) (+8 more)

### Community 7 - "Relatório: teste de calibração da correção (14/10/2026)"
Cohesion: 0.06
Nodes (38): Calibração com 30–50 redações de nota conhecida (erro médio e viés por competência), Decisão em aberto: prompt × RAG × fine-tuning (conversar com o Igor), Correção por IA: calibração e decisão RAG/fine-tuning (13/10/2026), Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir), Opção 1: prompt com exemplos corrigidos (few-shot), Opção 3: fine-tuning com pares nota_ia × nota_professor, Laboratório /laboratorio/ (foto → texto → nota), Opção 2: RAG com redações corrigidas parecidas (+30 more)

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

### Community 12 - "Usuario"
Cohesion: 0.10
Nodes (32): Atividade, AuditLog, Correcao, CorrecaoCriterio, CustoUso, DocumentoBase, DominioAluno, Escola (+24 more)

### Community 13 - "main.py"
Cohesion: 0.10
Nodes (19): decode_access_token(), ip_do_cliente(), novo_request_id(), Request, IP real. Atras do proxy (Railway, Nginx) o IP do socket e o do proxy; o real…, access_log(), erro_nao_tratado(), Exception (+11 more)

### Community 14 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (6): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos, Risco: capacidade de execução (equipe de quatro, ainda validando divisão de papéis), Risco: dependência de poucos pilotos

### Community 15 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 16 - "Modelo de Cobrança"
Cohesion: 0.67
Nodes (3): Ponto em aberto: definição de "aluno ativo" para cobrança, Ponto em aberto: preço (rascunho R$1.000 fixos + R$8/aluno, sem validação), RN-24 (Comercial): Cobrança proposta: mensalidade fixa por escola mais valor por aluno ativo por mês. Rascunho: R$ 1.000 fixos + R$ 8 por aluno; ainda não validado

### Community 17 - "app/agente.py"
Cohesion: 0.32
Nodes (6): Ferramenta, Agente de correcao: o Claude recebe um objetivo e decide sozinho quais…, Roda o loop ate o agente chamar a ferramenta de fim (terminou() vira True) ou…, _resumo(), rodar(), dataclasses

### Community 18 - "Custo Variável de IA/OCR"
Cohesion: 0.67
Nodes (3): Risco: custo variável de LLM e OCR por correção acima do previsto, RN-26 (Comercial): O valor por aluno deve superar o custo variável de IA e OCR por aluno; o preço só fecha depois de medir o custo real, RNF-17 (Custo): Custo variável por correção monitorado e abaixo do valor cobrado por aluno

### Community 23 - "gemini.py"
Cohesion: 0.15
Nodes (17): corrigir(), BaseModel, field_validator, QuestaoCorrigida, Correcao de exercicios de materias exatas (matematica, fisica, quimica) pelo…, ResultadoExatasIA, _client(), extract_text() (+9 more)

### Community 58 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 59 - "routers/painel.py"
Cohesion: 0.25
Nodes (15): escola_do_escopo(), UUID, Escola sobre a qual a consulta vale. E AQUI que o RBAC acontece, no backend. -…, Escola, _periodo(), get, Session, UUID (+7 more)

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.18
Nodes (11): E4 Correção por IA — Nota estimada, feedback e nível de confiança, Ponto em aberto: correção por gabarito (RF-18) — resolvido, tornou-se obrigatório no MVP, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção, US-10 (MVP): Como professor, quero a nota estimada da redação ENEM por competência e total, com justificativa, para revisar mais rápido, US-11 (MVP): Como professor, quero corrigir prova discursiva de qualquer matéria pela minha rubrica, para ter o mesmo apoio fora do ENEM (+3 more)

### Community 61 - "submissoes.py"
Cohesion: 0.14
Nodes (38): ocr(), _atividade_response(), confirmar_texto(), criar_atividade(), criar_materia(), enviar_imagem(), enviar_texto(), _gestor_da_escola() (+30 more)

### Community 62 - "models/usuario.py"
Cohesion: 0.19
Nodes (29): StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum, TipoMateriaEnum, UsuarioTurmaPapelEnum, Atividade, Correcao, CorrecaoCriterio (+21 more)

### Community 63 - "routers/agente.py"
Cohesion: 0.12
Nodes (34): Session, registrar_uso(), AgenteExecucao, CustoUso, Tema, get, post, Session (+26 more)

### Community 64 - "test_exatas.py"
Cohesion: 0.06
Nodes (49): ast, hash_password(), Roda o agente de verdade (Claude + Gemini, GASTA API) num banco temporario e…, _claude_falso(), Plano de estudo: GET /estudos/meu gera exercicios a partir do dominio real do…, test_gera_exercicios_para_as_piores_competencias_e_usa_cache(), gerar_contado(), test_professor_nao_usa_a_rota() (+41 more)

### Community 65 - "Dashboard.tsx"
Cohesion: 0.08
Nodes (33): EvolutionChart(), RealSparkline(), InstallBanner(), Button(), Empty(), IconButton(), Logo(), Modal() (+25 more)

### Community 66 - "Admin.tsx"
Cohesion: 0.15
Nodes (21): BlocosResumo(), brl(), EditarEscola(), Equipe(), Escolas(), mb(), mesAtual(), num() (+13 more)

### Community 67 - "Usuario"
Cohesion: 0.21
Nodes (25): Evento, Calendario da escola: uma tabela so, todo mundo le dela (por isso fica…, Usuario, apagar_evento(), criar_evento(), editar_evento(), _escola(), _evento_do_usuario() (+17 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.18
Nodes (11): 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual, 7. Persistência e contratos, 8. PWA (+3 more)

### Community 69 - "types.ts"
Cohesion: 0.19
Nodes (14): initialActivities, initialState, studyTasks, topics, approveActivity(), validScores(), visibleResult(), allowedPages (+6 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (13): Banco compartilhado + escola_id + RLS (estratégia escolhida), Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados (+5 more)

### Community 71 - "package.json"
Cohesion: 0.04
Nodes (44): dependencies, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, lucide-react, react, react-dom, react-native-web (+36 more)

### Community 72 - "questoes.py"
Cohesion: 0.19
Nodes (19): extract_text_from_image(), ler_imagem(), post, Session, UploadFile, anexar_figura(), _apagar_arquivo(), _pode_editar() (+11 more)

### Community 73 - "api.ts"
Cohesion: 0.10
Nodes (32): ListaContas(), NovaConta(), AdicionarMembro(), AlunoRow(), Classes(), Materials(), TIPOS_DOCUMENTO, TurmaCard() (+24 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "test_logs.py"
Cohesion: 0.17
Nodes (20): EventoSeguranca, Log de autenticacao/acesso. Append-only: a aplicacao so faz INSERT (nunca…, _campos(), Session, UUID, Eventos de seguranca (autenticacao e acesso negado) gravados no banco, so com…, registrar_seguranca(), verificar_cadeia() (+12 more)

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 77 - "Calendar.tsx"
Cohesion: 0.15
Nodes (19): Badge(), useCalendario(), br(), Calendar(), apagar(), cobre(), MESES, NovoEvento() (+11 more)

### Community 78 - "test_fluxo_envio.py"
Cohesion: 0.18
Nodes (17): Exception, TextoPublicado, atividade_id(), Fluxo do aluno: login -> envia foto -> OCR (falso) -> confirma texto. cd…, test_aluno_gera_propria_correcao_e_professor_aprova_depois(), test_falha_do_gemini_nao_vaza_detalhe(), test_fluxo_completo(), test_gemini_usa_modelo_reserva_quando_cota_estoura() (+9 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (13): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+5 more)

### Community 80 - "dependencies.py"
Cohesion: 0.16
Nodes (20): escola_inativa(), get_current_user(), Session, create_access_token(), verify_password(), get_db(), login(), post (+12 more)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "escolas.py"
Cohesion: 0.17
Nodes (16): confirmar_senha(), exigir_perfil(), Dependencia: so deixa passar quem tem um dos perfis., Reautenticacao em acao sensivel: o JWT roubado/esquecido aberto nao basta, pede…, criar_escola(), editar_escola(), listar_escolas(), get (+8 more)

### Community 83 - "PerfilEnum"
Cohesion: 0.15
Nodes (22): ErroFerramenta, Exception, Erro esperado de uma ferramenta: volta para o agente como resultado com…, PerfilEnum, DominioAluno, _ferramentas(), consultar_historico(), correcao_atual() (+14 more)

### Community 84 - "App.tsx"
Cohesion: 0.15
Nodes (19): App(), iniciais(), navItems, InstallEvent, isStandalone(), usePwa(), wasDismissed(), clearToken() (+11 more)

### Community 85 - "correcao.py"
Cohesion: 0.13
Nodes (16): Anthropic, CaixaIA, CompetenciaIA, corrigir(), PontoIA, BaseModel, field_validator, Correcao da redacao ENEM pelo Gemini nas 5 competencias do INEP. A nota fica… (+8 more)

### Community 86 - "atividades.ts"
Cohesion: 0.27
Nodes (12): Activities(), listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData(), paraStatus() (+4 more)

### Community 87 - "routers/compliance.py"
Cohesion: 0.25
Nodes (15): ConsentimentoLGPD, custo_uso_do_mes(), listar_auditoria(), meu_consentimento(), get, post, Session, UUID (+7 more)

### Community 89 - "Domina"
Cohesion: 0.15
Nodes (13): 1.1 A atividade (o professor prepara), 1.2 A resposta do aluno, 1.3 O que mais vai para a IA, 1. Entrada (inputs), 3.1 O que a IA devolve, 3.2 O que a API devolve, 3. Saída (outputs), 4. Como rodar (+5 more)

### Community 90 - "auditoria.py"
Cohesion: 0.25
Nodes (14): _campos(), Session, Log de auditoria (quem fez o que sobre quais dados), append-only e com cadeia…, registrar(), verificar_auditoria(), hash_de(), proximo_elo(), Session (+6 more)

### Community 91 - "Settings.tsx"
Cohesion: 0.21
Nodes (12): Card(), SectionTitle(), Consentimento(), CustoEAuditoria(), Help(), Settings(), auditLog(), AuditLogAPI (+4 more)

### Community 92 - "frontend/README.md"
Cohesion: 0.17
Nodes (6): Publicar o Domina na Vercel, Verificação no celular, Limites da validação, Roteiro manual, Validação do frontend, Verificação automatizada

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (8): Ponto em aberto: retenção de conteudo_bruto, LGPD (Lei Geral de Proteção de Dados), Ponto em aberto: RN-21 (dados não usados para treinar modelos de terceiros) mantida, pendente confirmação do usuário, Risco: dados de menores de idade (legal e reputacional), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

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
Cohesion: 0.17
Nodes (12): 1. Como ler os números, 2. Tabela resumo, 3. Versão por versão, 4. O que aprendemos, 5. Conclusão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10) (+4 more)

### Community 101 - "routers/turma.py"
Cohesion: 0.29
Nodes (16): Turma, UsuarioTurma, criar_turma(), matricular(), membros_turma(), minhas_turmas(), get, post (+8 more)

### Community 109 - "test_agente.py"
Cohesion: 0.23
Nodes (15): ResultadoIA, ExercicioGerado, gerar_exercicios(), BaseModel, Geracao de exercicios de pratica (plano de estudo) pelo Claude Haiku, a partir…, _RespostaIA, atividade_id(), _chamada() (+7 more)

### Community 110 - "Domina · Frontend"
Cohesion: 0.18
Nodes (11): Comandos, Conexão com o backend, Documentação, Domina · Frontend, Executar, Experimente o fluxo, O agente de correção na tela, O que o frontend faz (+3 more)

### Community 111 - "variantes.py"
Cohesion: 0.27
Nodes (8): CompetenciaV3, para_v2(), pegar(), BaseModel, Variantes de prompt para o teste de calibracao (nao fazem parte do projeto)., ResultadoV3, _v3b(), random

### Community 112 - "analisa_externa.py"
Cohesion: 0.23
Nodes (9): pearson(), ranks(), score(), csv, pearson(), ranks(), Compara a IA com as notas humanas da base externa (AES-ENEM com 3 humanos,…, spearman() (+1 more)

### Community 113 - "5. Mapa de telas e funcionalidades"
Cohesion: 0.33
Nodes (6): 5. Mapa de telas e funcionalidades, Acesso demonstrativo, Aluno, Compartilhadas, Gestor, Professor

### Community 114 - "2. Lógica (o que o agente faz)"
Cohesion: 0.33
Nodes (6): 2.1 Redação: o prompt (versão v14), 2.2 Matemática: conferir com o gabarito, 2.3 Validação, 2.4 Nota total e status, 2.5 Aprovação do professor, 2. Lógica (o que o agente faz)

### Community 115 - "routers/logs.py"
Cohesion: 0.30
Nodes (13): integridade(), logs_auditoria(), logs_seguranca(), _periodo(), date, get, Session, UUID (+5 more)

### Community 116 - "pathlib"
Cohesion: 0.15
Nodes (15): Mede a correcao da IA contra notas conhecidas, via Groq (gratis). Nao altera o…, Roda calibra.py com prompt de arquivo na planilha externa. uso (de backend/):…, Compara a IA com a nota oficial do INEP. uso: python analisa_inep.py <ia.jsonl>…, Roda calibra.py com prompt de arquivo na base INEP (nota oficial). uso (de…, Roda corrigir() do app (v12, 2 correcoes + media) nas 53 do INEP. uso (de…, Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da…, Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da…, httpx (+7 more)

### Community 117 - "6. Fluxos e estados"
Cohesion: 0.40
Nodes (5): 6. Fluxos e estados, Envio e aprovação, Navegação, Prática, Texto e arquivo

### Community 118 - "routers/documento.py"
Cohesion: 0.27
Nodes (12): StatusProcessamentoEnum, TipoDocumentoEnum, DocumentoBase, enviar_documento(), listar_documentos(), get, post, Session (+4 more)

### Community 120 - "routers/usuario.py"
Cohesion: 0.32
Nodes (11): criar_usuario(), listar_usuarios(), meu_usuario(), get, post, Session, UUID, _resposta() (+3 more)

### Community 121 - "Logs.tsx"
Cohesion: 0.22
Nodes (13): Aba, hora(), Logs(), verificar(), TIPOS, TOM(), AuditoriaAPI, consulta() (+5 more)

### Community 122 - "meus_exercicios"
Cohesion: 0.67
Nodes (3): meus_exercicios(), get, Session

### Community 123 - "datetime"
Cohesion: 0.29
Nodes (7): configurar_logging(), JsonFormatter, Logging do sistema: JSON em stdout (uma linha por evento) + contexto da…, Retencao dos logs no banco. Rodar periodicamente (Railway Cron / cron da VPS):…, datetime, logging, LogRecord

### Community 124 - "Logs do sistema"
Cohesion: 0.29
Nodes (6): Acesso, Integridade, Logs do sistema, O que existe e onde fica, Railway (testes), VPS (depois)

### Community 125 - "config.py"
Cohesion: 0.50
Nodes (3): Settings, BaseSettings, pydantic_settings

## Knowledge Gaps
- **309 isolated node(s):** `dev.sh script`, `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script`, `roda_v12.sh script` (+304 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 525 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prompt de correção v2 (descritores oficiais do INEP por nível)` connect `correcao.py` to `E4 Correção por IA — Nota estimada, feedback e nível de confiança`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `E4 Correção por IA — Nota estimada, feedback e nível de confiança` connect `E4 Correção por IA — Nota estimada, feedback e nível de confiança` to `Domina (plataforma de IA de correção e diagnóstico)`, `E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita`, `correcao.py`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `Domina (plataforma de IA de correção e diagnóstico)` connect `Domina (plataforma de IA de correção e diagnóstico)` to `E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita`, `E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria`, `Banco compartilhado + escola_id + RLS (estratégia escolhida)`, `Relatório: teste de calibração da correção (14/10/2026)`, `E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios`, `Diagnóstico de Domínio`, `Tendências do ENEM`, `E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor`, `Usuario`, `E10 Privacidade e operação — LGPD, auditoria e custo`, `E4 Correção por IA — Nota estimada, feedback e nível de confiança`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Usuario` (e.g. with `registrar()` and `confirmar_senha()`) actually correct?**
  _`Usuario` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `PerfilEnum` (e.g. with `escola_do_escopo()` and `exigir_perfil()`) actually correct?**
  _`PerfilEnum` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `Atividade` (e.g. with `TipoAtividadeEnum` and `_ferramentas()`) actually correct?**
  _`Atividade` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `dev.sh script`, `roda_dupla.sh script`, `roda_v10.sh script` to the rest of the system?**
  _309 weakly-connected nodes found - possible documentation gaps or missing edges._