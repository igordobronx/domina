# Graph Report - domina  (2026-11-15)

## Corpus Check
- 173 files · ~154,825 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 54 file(s) not represented in the graph (top: .jsonl 37, (none) 6, .xlsm 3)

## Summary
- 1730 nodes · 4755 edges · 137 communities (86 shown, 51 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 521 edges (avg confidence: 0.93)
- Token cost: 227,945 input · 0 output

## Graph Freshness
- Built from commit: `51052403`
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
- seed.py
- routers/agente.py
- test_exatas.py
- Card
- Admin.tsx
- Usuario
- Documentação do frontend Domina
- Dashboard.tsx
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
- database.py
- App.tsx
- correcao.py
- atividades.ts
- routers/compliance.py
- vite-env.d.ts
- Domina
- routers/metas.py
- Settings.tsx
- frontend/README.md
- LGPD (Lei Geral de Proteção de Dados)
- exercicios.py
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- Histórico das versões do prompt de correção (v1 a v21)
- PerfilEnum
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
- submissao.py
- routers/logs.py
- pathlib
- 6. Fluxos e estados
- routers/documento.py
- dev.sh
- test_atividades.py
- Logs.tsx
- monta_base_externa.py
- correcoes.py
- Logs do sistema
- Metas.tsx
- atividades.py
- test_calendario.py
- test_evolucao.py
- correcao_exatas.py
- test_estudos.py
- test_metas.py
- test_logs.py
- test_exercicios.py
- usePwa.ts
- 3. Versão por versão
- Validação do frontend

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 142 edges
2. `PerfilEnum` - 68 edges
3. `request()` - 66 edges
4. `Card()` - 49 edges
5. `Button()` - 46 edges
6. `token()` - 44 edges
7. `Atividade` - 41 edges
8. `SectionTitle()` - 39 edges
9. `Badge()` - 38 edges
10. `App()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `2.1 Redação: o prompt (versão v14)` --references--> `ResultadoIA`  [INFERRED]
  README.md → backend/app/correcao.py
- `Como o progresso é calculado` --references--> `progresso()`  [INFERRED]
  docs/decisoes/gamificacao-niveis-e-metas.md → backend/app/metas.py
- `Visão geral do fluxo` --references--> `TipoMateriaEnum`  [INFERRED]
  README.md → backend/app/models/enum.py
- `2.4 Nota total e status` --references--> `corrigir_submissao()`  [INFERRED]
  README.md → backend/app/routers/correcoes.py
- `3.2 O que a API devolve` --references--> `CorrecaoResponse`  [INFERRED]
  README.md → backend/app/schemas/submissao.py

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

## Communities (137 total, 51 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.13
Nodes (12): AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend), Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança), IPE (piloto institucional desejado), João Pedro (Co-fundador; estatística, matemática e IA; ponte de entrada no CEIA via UFG) (+4 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.07
Nodes (51): CampoComSimbolos(), GRUPOS, inserirNoCursor(), Props, Empty(), Activities(), ActivityDetail(), alternativasDe() (+43 more)

### Community 2 - "test_rbac.py"
Cohesion: 0.29
Nodes (15): test_admin_precisa_da_escola_e_feriados_calculados(), test_telas_de_log_so_para_quem_pode_e_gestor_so_ve_a_propria_escola(), escola_id(), novo(), test_admin_cria_escola_gestor_e_professor(), test_admin_lista_turmas_da_escola_e_cria_conta_nela(), test_admin_ve_cada_escola_e_o_total(), test_conta_ja_nasce_na_turma_escolhida() (+7 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (16): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Correção de Redação do ENEM (5 competências INEP), Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Gustavo, Igor, João Pedro (+8 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 5 - "typing"
Cohesion: 0.08
Nodes (15): upgrade(), downgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade() (+7 more)

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.13
Nodes (15): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP), RF-09 (Matéria e base): Versionar a base de uma matéria, registrando quem mudou o quê e quando (+7 more)

### Community 7 - "Relatório: teste de calibração da correção (14/10/2026)"
Cohesion: 0.06
Nodes (27): Calibração com 30–50 redações de nota conhecida (erro médio e viés por competência), Decisão em aberto: prompt × RAG × fine-tuning (conversar com o Igor), Correção por IA: calibração e decisão RAG/fine-tuning (13/10/2026), Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir), Laboratório /laboratorio/ (foto → texto → nota), Teste: redação ENEM 2023 do Igor (oficial 880; IA 600 → 680), Base de redações (essays/base_redacoes_enem_domina_ai.xlsm, 2.327 redações), Relatório: teste de calibração da correção (14/10/2026) (+19 more)

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
Nodes (9): E9 Tendências — Recorrência histórica de assuntos do ENEM, RF-31 (Recomendação): Cruzar a lacuna do aluno com a recorrência do tema em provas passadas para priorizar, RF-36 (Tendências): Ingerir provas públicas do ENEM e de outros vestibulares (UFG, UFU, FUVEST, UEG) e classificar as questões por assunto e gênero textual, RF-37 (Tendências): Calcular o índice de recorrência (frequência, nº de provas, recência, consistência) e classificar em 4 categorias, RF-38 (Tendências): Exibir por assunto o nível de atenção, as evidências históricas e o grau de confiança, nunca como probabilidade de cair, RF-39 (Tendências): Indicar alta ou queda de frequência só com amostra suficiente; senão, avisar que não há tendência confiável, US-30 (Piloto): Como estudante, quero ver os assuntos do ENEM classificados por recorrência histórica, para priorizar meu tempo, US-31 (Piloto): Como estudante, quero saber se um assunto está em alta ou queda, para entender a tendência (+1 more)

### Community 12 - "Usuario"
Cohesion: 0.10
Nodes (29): Atividade, AuditLog, Correcao, CorrecaoCriterio, CustoUso, DocumentoBase, DominioAluno, Escola (+21 more)

### Community 13 - "main.py"
Cohesion: 0.08
Nodes (11): Settings, configurar_logging(), ip_do_cliente(), JsonFormatter, novo_request_id(), access_log(), erro_nao_tratado(), _usuario_do_token() (+3 more)

### Community 14 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (4): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos

### Community 15 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 17 - "app/agente.py"
Cohesion: 0.22
Nodes (4): Ferramenta, _resumo(), rodar(), _client()

### Community 23 - "gemini.py"
Cohesion: 0.17
Nodes (10): _client(), extract_text(), gerar(), reduzir(), TextoPublicado, ocr(), test_gemini_usa_modelo_reserva_quando_cota_estoura(), test_reduz_foto_grande_antes_do_gemini() (+2 more)

### Community 58 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 59 - "routers/painel.py"
Cohesion: 0.23
Nodes (7): exigir_perfil(), _periodo(), _resumo(), resumo_da_escola(), resumo_da_plataforma(), ResumoEscola, ResumoPlataforma

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.18
Nodes (10): E4 Correção por IA — Nota estimada, feedback e nível de confiança, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção, US-10 (MVP): Como professor, quero a nota estimada da redação ENEM por competência e total, com justificativa, para revisar mais rápido, US-11 (MVP): Como professor, quero corrigir prova discursiva de qualquer matéria pela minha rubrica, para ter o mesmo apoio fora do ENEM, US-13 (MVP): Como aluno, quero feedback que aponte trechos do meu texto, para entender exatamente o que melhorar (+2 more)

### Community 61 - "submissoes.py"
Cohesion: 0.18
Nodes (20): avaliar_seguro(), TipoEnvioEnum, Submissao, SubmissaoPagina, caminhos_da_submissao(), confirmar_texto(), criar_atividade(), criar_atividades_em_lote() (+12 more)

### Community 62 - "seed.py"
Cohesion: 0.18
Nodes (12): garantir_competencias(), StatusCorrecaoEnum, TipoAtividadeEnum, TipoMateriaEnum, Materia, minha_evolucao(), criar_materia(), aprovar() (+4 more)

### Community 63 - "routers/agente.py"
Cohesion: 0.12
Nodes (22): ErroFerramenta, registrar_uso(), gerar_exercicios(), AgenteExecucao, Correcao, _ferramentas(), correcao_atual(), _corrigir() (+14 more)

### Community 64 - "test_exatas.py"
Cohesion: 0.23
Nodes (17): criar_atividade_com_gabarito(), criar_turma_e_materia(), _gemini_falso(), test_aluno_gera_propria_correcao_exatas_e_professor_aprova_depois(), test_aprovar_exige_todos_os_criterios(), test_atividade_de_exatas_exige_gabarito(), test_enunciado_longo_nao_quebra_a_criacao(), test_exatas_varias_folhas_vao_todas_ao_gemini_e_caixa_aceita_pagina() (+9 more)

### Community 65 - "Card"
Cohesion: 0.23
Nodes (18): RealSparkline(), Badge(), Card(), ListaContas(), doBackend(), doDemo(), DoProfessor(), Evolution() (+10 more)

### Community 66 - "Admin.tsx"
Cohesion: 0.20
Nodes (20): BlocosResumo(), brl(), EditarEscola(), Escolas(), mb(), mesAtual(), num(), PainelEscola() (+12 more)

### Community 67 - "Usuario"
Cohesion: 0.21
Nodes (14): Evento, Usuario, apagar_evento(), criar_evento(), editar_evento(), _escola(), _evento_do_usuario(), _item() (+6 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.22
Nodes (9): 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual, 7. Persistência e contratos, 9. Usabilidade e acessibilidade (+1 more)

### Community 69 - "Dashboard.tsx"
Cohesion: 0.13
Nodes (29): EvolutionChart(), Progress(), initialActivities, initialState, studyTasks, topics, iso(), ActivityRow() (+21 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (12): Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados, RF-03 (Conta e acesso): Cadastro de turmas e vínculo de alunos e professores (+4 more)

### Community 71 - "package.json"
Cohesion: 0.05
Nodes (45): dependencies, @fontsource/bricolage-grotesque@^5.3.0, @fontsource/ibm-plex-mono@^5.3.0, @fontsource/ibm-plex-sans@^5.3.0, lucide-react@^1.52.0, react@^19.3.0, react-dom@^19.3.0, react-native-web@^0.21.3 (+37 more)

### Community 72 - "questoes.py"
Cohesion: 0.20
Nodes (7): extract_text_from_image(), ler_imagem(), anexar_figura(), _pode_editar(), _questao(), remover_figura(), ver_figura()

### Community 73 - "api.ts"
Cohesion: 0.08
Nodes (56): Button(), NovaConta(), erroDe(), ExerciciosProfessor(), FormExercicio(), Rascunho, vazio, AdicionarMembro() (+48 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "test_logs.py"
Cohesion: 0.16
Nodes (10): hash_de(), proximo_elo(), verificar(), EventoSeguranca, _campos(), registrar_seguranca(), verificar_cadeia(), aplicar() (+2 more)

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 77 - "Calendar.tsx"
Cohesion: 0.15
Nodes (19): useCalendario(), br(), Calendar(), apagar(), cobre(), MESES, NovoEvento(), salvar() (+11 more)

### Community 78 - "test_fluxo_envio.py"
Cohesion: 0.19
Nodes (14): hash_password(), atividade_id(), test_aluno_gera_propria_correcao_e_professor_aprova_depois(), test_corrigir_faz_uma_correcao_so(), test_falha_do_gemini_nao_vaza_detalhe(), test_fluxo_completo(), test_imagem_sem_texto_responde_422(), test_nota_da_ia_vira_nivel_valido_do_enem() (+6 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (12): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+4 more)

### Community 80 - "dependencies.py"
Cohesion: 0.20
Nodes (9): confirmar_senha(), escola_inativa(), get_current_user(), create_access_token(), decode_access_token(), verify_password(), login(), LoginRequest (+1 more)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "escolas.py"
Cohesion: 0.23
Nodes (8): Escola, criar_escola(), editar_escola(), listar_escolas(), CriarEscolaRequest, EditarEscolaRequest, EscolaResponse, test_sem_correcao_aprovada_responde_409()

### Community 83 - "database.py"
Cohesion: 0.14
Nodes (9): get_db(), consultar_historico(), _compartilha_turma(), _dominio_de(), dominio_do_aluno(), meu_dominio(), meus_exercicios(), DominioResponse (+1 more)

### Community 84 - "App.tsx"
Cohesion: 0.12
Nodes (23): App(), iniciais(), navItems, InstallBanner(), IconButton(), Logo(), Modal(), Equipe() (+15 more)

### Community 85 - "correcao.py"
Cohesion: 0.24
Nodes (3): CaixaIA, CompetenciaIA, PontoIA

### Community 86 - "atividades.ts"
Cohesion: 0.32
Nodes (10): listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData(), paraStatus(), carregarRevisoes() (+2 more)

### Community 87 - "routers/compliance.py"
Cohesion: 0.21
Nodes (11): ConsentimentoLGPD, CustoUso, custo_uso_do_mes(), listar_auditoria(), meu_consentimento(), registrar_consentimento(), _so_gestor(), AuditLogResponse (+3 more)

### Community 89 - "Domina"
Cohesion: 0.13
Nodes (15): 1.1 A atividade (o professor prepara), 1.2 A resposta do aluno, 1.3 O que mais vai para a IA, 1. Entrada (inputs), 2.1 Redação: o prompt (versão v14), 2.2 Matemática: conferir com o gabarito, 2.3 Validação, 2.4 Nota total e status (+7 more)

### Community 90 - "routers/metas.py"
Cohesion: 0.09
Nodes (37): avaliar_metas(), metas_do_aluno(), nivel_de(), pontos_do_aluno(), Meta, MetaConcluida, _alunos_da_escola(), _alunos_das_turmas() (+29 more)

### Community 91 - "Settings.tsx"
Cohesion: 0.35
Nodes (10): SectionTitle(), Consentimento(), CustoEAuditoria(), Settings(), auditLog(), AuditLogAPI, custoUso(), CustoUsoAPI (+2 more)

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (5): LGPD (Lei Geral de Proteção de Dados), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

### Community 94 - "exercicios.py"
Cohesion: 0.10
Nodes (32): _RespostaExemplo, _RespostaSugestao, sugerir_exercicios(), sugerir_resposta_exemplo(), SugestaoExercicio, gerar_json(), Exercicio, ExercicioResposta (+24 more)

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

### Community 101 - "PerfilEnum"
Cohesion: 0.15
Nodes (20): escola_do_escopo(), PerfilEnum, UsuarioTurmaPapelEnum, Turma, UsuarioTurma, criar_turma(), matricular(), membros_turma() (+12 more)

### Community 109 - "test_agente.py"
Cohesion: 0.27
Nodes (13): corrigir(), ResultadoIA, ExercicioGerado, _RespostaIA, atividade_id(), _chamada(), _cliente_roteirizado(), test_agente_decide_os_passos_e_grava_o_passo_a_passo() (+5 more)

### Community 110 - "Domina · Frontend"
Cohesion: 0.18
Nodes (11): Comandos, Conexão com o backend, Documentação, Domina · Frontend, Executar, Experimente o fluxo, O agente de correção na tela, O que o frontend faz (+3 more)

### Community 111 - "variantes.py"
Cohesion: 0.29
Nodes (6): amostra(), CompetenciaV3, para_v2(), pegar(), ResultadoV3, _v3b()

### Community 112 - "analisa_externa.py"
Cohesion: 0.22
Nodes (6): pearson(), ranks(), score(), pearson(), ranks(), spearman()

### Community 113 - "5. Mapa de telas e funcionalidades"
Cohesion: 0.33
Nodes (6): 5. Mapa de telas e funcionalidades, Acesso demonstrativo, Aluno, Compartilhadas, Gestor, Professor

### Community 114 - "submissao.py"
Cohesion: 0.14
Nodes (19): AlunoResumo, AprovarRequest, _AtividadeBase, ConfirmarTextoRequest, CriarAtividadeLoteRequest, CriarAtividadeRequest, CriarMateriaRequest, CriterioResponse (+11 more)

### Community 115 - "routers/logs.py"
Cohesion: 0.21
Nodes (12): _campos(), registrar(), verificar_auditoria(), AuditLog, integridade(), logs_auditoria(), logs_seguranca(), _periodo() (+4 more)

### Community 117 - "6. Fluxos e estados"
Cohesion: 0.40
Nodes (5): 6. Fluxos e estados, Envio e aprovação, Navegação, Prática, Texto e arquivo

### Community 118 - "routers/documento.py"
Cohesion: 0.19
Nodes (6): StatusProcessamentoEnum, TipoDocumentoEnum, DocumentoBase, enviar_documento(), listar_documentos(), DocumentoBaseResponse

### Community 120 - "test_atividades.py"
Cohesion: 0.24
Nodes (17): _lote(), _objetiva(), _setup(), test_atividade_sem_autor_nao_aparece_para_professor_so_para_gestor(), test_depois_do_primeiro_envio_so_titulo_e_prazo_mudam(), test_editar_titulo_prazo_e_gabarito_enquanto_ninguem_enviou(), test_excluir_apaga_se_vazia_e_arquiva_se_tem_envio(), test_fila_traz_turma_e_filtra_por_turma() (+9 more)

### Community 121 - "Logs.tsx"
Cohesion: 0.22
Nodes (13): Aba, hora(), Logs(), verificar(), TIPOS, TOM(), AuditoriaAPI, consulta() (+5 more)

### Community 122 - "monta_base_externa.py"
Cohesion: 0.13
Nodes (7): gerar(), gerar(), norm(), notas(), palavras(), titulo(), valido()

### Community 123 - "correcoes.py"
Cohesion: 0.21
Nodes (15): progresso(), Atividade, CorrecaoCriterio, DominioAluno, aprovar_correcao(), _atualizar_dominio(), _correcao_response(), corrigir_submissao() (+7 more)

### Community 124 - "Logs do sistema"
Cohesion: 0.29
Nodes (6): Acesso, Integridade, Logs do sistema, O que existe e onde fica, Railway (testes), VPS (depois)

### Community 125 - "Metas.tsx"
Cohesion: 0.19
Nodes (16): br(), MetaLinha(), MetasEquipe(), NovaMeta(), Ranking(), TIPOS, unidade(), arquivarMeta() (+8 more)

### Community 126 - "atividades.py"
Cohesion: 0.28
Nodes (9): Tema, editar_atividade(), excluir_atividade(), _minha(), _tem_submissoes(), _apagar_arquivo(), _atividade_response(), AtividadeResponse (+1 more)

### Community 127 - "test_calendario.py"
Cohesion: 0.26
Nodes (9): feriados(), _pascoa(), _evento(), test_aluno_nao_cria_e_professor_so_para_a_propria_turma(), test_aluno_nao_ve_evento_de_turma_alheia_e_feriado_vem_pronto(), test_evento_da_escola_toda_aparece_para_todos_e_nao_vaza_para_outra_escola(), test_professor_nao_apaga_evento_do_gestor_mas_gestor_apaga_o_dele(), _titulos() (+1 more)

### Community 128 - "test_evolucao.py"
Cohesion: 0.22
Nodes (4): _gemini_falso(), test_evolucao_agrupa_por_materia_sem_tocar_dominio(), test_evolucao_so_para_aluno(), token()

### Community 129 - "correcao_exatas.py"
Cohesion: 0.22
Nodes (6): corrigir(), QuestaoCorrigida, ResultadoExatasIA, 3.1 O que a IA devolve, 3.2 O que a API devolve, 3. Saída (outputs)

### Community 130 - "test_estudos.py"
Cohesion: 0.25
Nodes (6): _claude_falso(), test_gera_exercicios_para_as_piores_competencias_e_usa_cache(), gerar_contado(), test_professor_nao_usa_a_rota(), test_sem_chave_do_claude_responde_503(), token()

### Community 131 - "test_metas.py"
Cohesion: 0.38
Nodes (7): _entregar_objetiva(), _meta(), _setup(), test_editar_arquivar_e_pontos_ficam(), test_escopo_e_permissoes_de_criacao(), test_meta_conclui_sozinha_sobe_nivel_e_aparece_no_ranking(), test_meta_nova_nao_conta_o_passado_e_nota_percentual()

### Community 132 - "test_logs.py"
Cohesion: 0.31
Nodes (8): _eventos(), test_403_vira_acesso_negado_com_usuario_e_request_id(), test_acao_sensivel_pede_a_senha_de_novo(), test_access_log_json_sem_query_string_nem_token(), test_ip_so_vem_do_proxy_quando_configurado(), ip_da_falha(), test_login_falho_e_ok_viram_evento_sem_senha(), test_sem_token_vira_nao_autenticado()

### Community 133 - "test_exercicios.py"
Cohesion: 0.42
Nodes (6): _objetivo(), _setup(), test_aluno_ve_so_da_turma_e_gabarito_depois_de_responder(), test_criar_validacoes_e_permissoes(), test_editar_e_excluir_somem_para_o_aluno(), test_ia_sugere_rascunhos_sem_salvar()

### Community 134 - "usePwa.ts"
Cohesion: 0.32
Nodes (6): 8. PWA, Instalação, InstallEvent, isStandalone(), usePwa(), wasDismissed()

### Community 135 - "3. Versão por versão"
Cohesion: 0.33
Nodes (6): 3. Versão por versão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10), Fase 4: base INEP de 53 redações, foco na C3 (19/10), Fase 5: dia da entrega (20/10)

### Community 136 - "Validação do frontend"
Cohesion: 0.40
Nodes (4): Limites da validação, Roteiro manual, Validação do frontend, Verificação automatizada

## Knowledge Gaps
- **88 isolated node(s):** `Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir)`, `COPE (piloto institucional desejado)`, `Escola do Professor Beto (candidata a piloto adicional, foco em redação)`, `Gustavo (Co-fundador; desenvolvimento backend)`, `Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança)` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 535 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Domina` connect `Domina` to `correcao_exatas.py`, `frontend/README.md`, `routers/agente.py`?**
  _High betweenness centrality (0.288) - this node is a cross-community bridge._
- **Are the 111 inferred relationships involving `Usuario` (e.g. with `registrar()` and `confirmar_senha()`) actually correct?**
  _`Usuario` has 111 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir)`, `COPE (piloto institucional desejado)`, `Escola do Professor Beto (candidata a piloto adicional, foco em redação)` to the rest of the system?**
  _88 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Domina (plataforma de IA de correção e diagnóstico)` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._
- **Why does `Documentação do frontend Domina` connect `Documentação do frontend Domina` to `5. Mapa de telas e funcionalidades`, `frontend/README.md`, `6. Fluxos e estados`, `usePwa.ts`?**
  _High betweenness centrality (0.275) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `PerfilEnum` (e.g. with `escola_do_escopo()` and `exigir_perfil()`) actually correct?**
  _`PerfilEnum` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Should `Activities.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._