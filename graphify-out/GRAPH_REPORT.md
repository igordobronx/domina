# Graph Report - domina  (2026-11-15)

## Corpus Check
- 180 files · ~174,794 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 56 file(s) not represented in the graph (top: .jsonl 37, (none) 7, .xlsm 3)

## Summary
- 1813 nodes · 4951 edges · 136 communities (85 shown, 51 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 599 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0677bb66`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- hook.cjs
- Escopo do Protótipo
- E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita
- sqlalchemy
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- api
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Usuario
- uuid
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
- CLAUDE.md: Domina
- routers/painel.py
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- Usuario
- routers/usuario.py
- routers/agente.py
- test_exatas.py
- Learning.tsx
- Admin.tsx
- routers/calendario.py
- Documentação do frontend Domina
- App.tsx
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- _pode_editar
- api.ts
- compilerOptions
- test_logs.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- Calendar.tsx
- test_fluxo_envio.py
- E10 Privacidade e operação — LGPD, auditoria e custo
- main.py
- vercel.json
- escolas.py
- pydantic
- main.tsx
- correcao.py
- atividades.ts
- routers/compliance.py
- vite-env.d.ts
- Domina
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
- PerfilEnum
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh
- test_agente.py
- Domina · Frontend
- devDependencies
- analisa_externa.py
- 5. Mapa de telas e funcionalidades
- submissao.py
- routers/logs.py
- variantes.py
- 6. Fluxos e estados
- models/usuario.py
- dev.sh
- token
- Logs.tsx
- monta_base_externa.py
- correcoes.py
- Logs do sistema
- Card
- atividades.py
- dependencies
- test_estudos.py
- scripts
- dominio_do_aluno
- 2. Lógica (o que o agente faz)
- @playwright/test
- .trail/README.md
- usePwa.ts
- 3. Versão por versão

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 150 edges
2. `request()` - 70 edges
3. `PerfilEnum` - 68 edges
4. `Card()` - 50 edges
5. `token()` - 47 edges
6. `Button()` - 47 edges
7. `Atividade` - 41 edges
8. `Badge()` - 39 edges
9. `SectionTitle()` - 39 edges
10. `App()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `2.1 Redação: o prompt (versão v14)` --references--> `ResultadoIA`  [INFERRED]
  README.md → backend/app/correcao.py
- `Visão geral do fluxo` --references--> `TipoMateriaEnum`  [INFERRED]
  README.md → backend/app/models/enum.py
- `2.4 Nota total e status` --references--> `corrigir_submissao()`  [INFERRED]
  README.md → backend/app/routers/correcoes.py
- `3.2 O que a API devolve` --references--> `CorrecaoResponse`  [INFERRED]
  README.md → backend/app/schemas/submissao.py
- `3.1 O que a IA devolve` --references--> `ResultadoIA`  [INFERRED]
  README.md → backend/app/correcao.py

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

## Communities (136 total, 51 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.13
Nodes (12): AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend), Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança), IPE (piloto institucional desejado), João Pedro (Co-fundador; estatística, matemática e IA; ponte de entrada no CEIA via UFG) (+4 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.07
Nodes (52): CampoComSimbolos(), GRUPOS, inserirNoCursor(), Props, Empty(), Activities(), ActivityDetail(), alternativasDe() (+44 more)

### Community 2 - "hook.cjs"
Cohesion: 0.12
Nodes (16): best(), entry(), { execFileSync }, fromPkg(), fs, globalRoot(), newer(), onPath() (+8 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (16): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Correção de Redação do ENEM (5 competências INEP), Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Gustavo, Igor, João Pedro (+8 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 5 - "sqlalchemy"
Cohesion: 0.06
Nodes (19): upgrade(), downgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade() (+11 more)

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

### Community 13 - "uuid"
Cohesion: 0.12
Nodes (7): configurar_logging(), ip_do_cliente(), JsonFormatter, novo_request_id(), access_log(), erro_nao_tratado(), _usuario_do_token()

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
Cohesion: 0.12
Nodes (10): corrigir(), QuestaoCorrigida, ResultadoExatasIA, _client(), extract_text(), gerar(), reduzir(), test_exatas_varias_folhas_vao_todas_ao_gemini_e_caixa_aceita_pagina() (+2 more)

### Community 58 - "CLAUDE.md: Domina"
Cohesion: 0.29
Nodes (6): 1. O que é o Domina, 2. Onde as coisas estão, 3. Regras de trabalho (preferências do usuário), 5. Correção da redação: estado do prompt, 6. Mapa rápido do código, CLAUDE.md: Domina

### Community 59 - "routers/painel.py"
Cohesion: 0.22
Nodes (9): escola_do_escopo(), CustoUso, Escola, _periodo(), _resumo(), resumo_da_escola(), resumo_da_plataforma(), ResumoEscola (+1 more)

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.18
Nodes (10): E4 Correção por IA — Nota estimada, feedback e nível de confiança, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção, US-10 (MVP): Como professor, quero a nota estimada da redação ENEM por competência e total, com justificativa, para revisar mais rápido, US-11 (MVP): Como professor, quero corrigir prova discursiva de qualquer matéria pela minha rubrica, para ter o mesmo apoio fora do ENEM, US-13 (MVP): Como aluno, quero feedback que aponte trechos do meu texto, para entender exatamente o que melhorar (+2 more)

### Community 61 - "Usuario"
Cohesion: 0.18
Nodes (23): avaliar_seguro(), TipoEnvioEnum, SubmissaoPagina, Usuario, ocr(), caminhos_da_submissao(), confirmar_texto(), criar_atividade() (+15 more)

### Community 62 - "routers/usuario.py"
Cohesion: 0.32
Nodes (6): criar_usuario(), listar_usuarios(), meu_usuario(), _resposta(), CriarUsuarioRequest, UsuarioResponse

### Community 63 - "routers/agente.py"
Cohesion: 0.10
Nodes (29): ErroFerramenta, registrar_uso(), gerar_exercicios(), AgenteExecucao, _ferramentas(), consultar_historico(), correcao_atual(), _corrigir() (+21 more)

### Community 64 - "test_exatas.py"
Cohesion: 0.26
Nodes (16): criar_atividade_com_gabarito(), criar_turma_e_materia(), _gemini_falso(), test_aluno_gera_propria_correcao_exatas_e_professor_aprova_depois(), test_aprovar_exige_todos_os_criterios(), test_atividade_de_exatas_exige_gabarito(), test_enunciado_longo_nao_quebra_a_criacao(), test_figura_da_questao_vai_para_o_aluno_e_para_o_corretor() (+8 more)

### Community 65 - "Learning.tsx"
Cohesion: 0.13
Nodes (27): RealSparkline(), Badge(), doBackend(), doDemo(), DoProfessor(), Evolution(), ExercicioComum, ExercicioDoProfessor() (+19 more)

### Community 66 - "Admin.tsx"
Cohesion: 0.26
Nodes (15): BlocosResumo(), brl(), mb(), mesAtual(), num(), PainelEscola(), PainelPlataforma(), PerfilConta (+7 more)

### Community 67 - "routers/calendario.py"
Cohesion: 0.15
Nodes (15): feriados(), _pascoa(), Evento, apagar_evento(), criar_evento(), editar_evento(), _escola(), _evento_do_usuario() (+7 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.22
Nodes (9): 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual, 7. Persistência e contratos, 9. Usabilidade e acessibilidade (+1 more)

### Community 69 - "App.tsx"
Cohesion: 0.10
Nodes (37): App(), iniciais(), navItems, EvolutionChart(), InstallBanner(), IconButton(), Logo(), Modal() (+29 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (12): Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados, RF-03 (Conta e acesso): Cadastro de turmas e vínculo de alunos e professores (+4 more)

### Community 71 - "package.json"
Cohesion: 0.15
Nodes (13): name, private, type, version, prettier, react-native-web, @types/react, @types/react-dom (+5 more)

### Community 72 - "_pode_editar"
Cohesion: 0.18
Nodes (7): extract_text_from_image(), ler_imagem(), anexar_figura(), _pode_editar(), _questao(), remover_figura(), ver_figura()

### Community 73 - "api.ts"
Cohesion: 0.06
Nodes (70): CircleHalf(), erroDe(), ExerciciosProfessor(), FormExercicio(), LinhaResposta(), Rascunho, RespostasExercicio(), ResumoTurma() (+62 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "test_logs.py"
Cohesion: 0.11
Nodes (22): _campos(), verificar_auditoria(), hash_de(), proximo_elo(), verificar(), AuditLog, EventoSeguranca, _campos() (+14 more)

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 77 - "Calendar.tsx"
Cohesion: 0.16
Nodes (18): useCalendario(), br(), Calendar(), apagar(), cobre(), MESES, ROTULO, SEMANA (+10 more)

### Community 78 - "test_fluxo_envio.py"
Cohesion: 0.19
Nodes (15): TextoPublicado, atividade_id(), test_aluno_gera_propria_correcao_e_professor_aprova_depois(), test_falha_do_gemini_nao_vaza_detalhe(), test_fluxo_completo(), test_imagem_sem_texto_responde_422(), test_nota_da_ia_vira_nivel_valido_do_enem(), test_ocr_sem_chave_responde_503() (+7 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (12): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+4 more)

### Community 80 - "main.py"
Cohesion: 0.12
Nodes (11): escola_inativa(), get_current_user(), create_access_token(), decode_access_token(), verify_password(), Settings, get_db(), login() (+3 more)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "escolas.py"
Cohesion: 0.16
Nodes (8): confirmar_senha(), exigir_perfil(), criar_escola(), editar_escola(), listar_escolas(), CriarEscolaRequest, EditarEscolaRequest, EscolaResponse

### Community 83 - "pydantic"
Cohesion: 0.22
Nodes (3): EvolucaoMateriaResponse, EvolucaoPontoResponse, OCRResponse

### Community 84 - "main.tsx"
Cohesion: 0.33
Nodes (4): @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, react-dom

### Community 85 - "correcao.py"
Cohesion: 0.17
Nodes (6): CaixaIA, CompetenciaIA, corrigir(), PontoIA, gerar_json(), test_corrigir_faz_uma_correcao_so()

### Community 86 - "atividades.ts"
Cohesion: 0.32
Nodes (10): listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData(), paraStatus(), carregarRevisoes() (+2 more)

### Community 87 - "routers/compliance.py"
Cohesion: 0.25
Nodes (10): ConsentimentoLGPD, custo_uso_do_mes(), listar_auditoria(), meu_consentimento(), registrar_consentimento(), _so_gestor(), AuditLogResponse, ConsentimentoRequest (+2 more)

### Community 89 - "Domina"
Cohesion: 0.18
Nodes (11): 1.2 A resposta do aluno, 1.3 O que mais vai para a IA, 1. Entrada (inputs), 3.1 O que a IA devolve, 3.2 O que a API devolve, 3. Saída (outputs), 4. Como rodar, 5. Como testar (+3 more)

### Community 90 - "routers/metas.py"
Cohesion: 0.09
Nodes (38): avaliar_metas(), metas_do_aluno(), nivel_de(), pontos_do_aluno(), progresso(), Meta, MetaConcluida, _alunos_da_escola() (+30 more)

### Community 91 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 92 - "frontend/README.md"
Cohesion: 0.20
Nodes (6): Publicar o Domina na Vercel, Verificação no celular, Limites da validação, Roteiro manual, Validação do frontend, Verificação automatizada

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (5): LGPD (Lei Geral de Proteção de Dados), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

### Community 94 - "exercicios.py"
Cohesion: 0.09
Nodes (45): registrar(), _RespostaExemplo, _RespostaSugestao, sugerir_exercicios(), sugerir_resposta_exemplo(), SugestaoExercicio, Exercicio, ExercicioResposta (+37 more)

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
Cohesion: 0.25
Nodes (6): 1. Como ler os números, 2. Tabela resumo, 4. O que aprendemos, 5. Conclusão, Histórico das versões do prompt de correção (v1 a v21), Onde estão os arquivos

### Community 101 - "PerfilEnum"
Cohesion: 0.29
Nodes (11): PerfilEnum, Turma, criar_turma(), matricular(), membros_turma(), minhas_turmas(), _so_gestor(), CriarTurmaRequest (+3 more)

### Community 109 - "test_agente.py"
Cohesion: 0.26
Nodes (12): ResultadoIA, ExercicioGerado, _RespostaIA, atividade_id(), _chamada(), _cliente_roteirizado(), test_agente_decide_os_passos_e_grava_o_passo_a_passo(), test_agente_nao_roda_de_novo_sem_refazer() (+4 more)

### Community 110 - "Domina · Frontend"
Cohesion: 0.18
Nodes (11): Comandos, Conexão com o backend, Documentação, Domina · Frontend, Executar, Experimente o fluxo, O agente de correção na tela, O que o frontend faz (+3 more)

### Community 111 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, @playwright/test, prettier, @types/react, @types/react-dom, @types/react-native-web, typescript, vite (+3 more)

### Community 112 - "analisa_externa.py"
Cohesion: 0.27
Nodes (6): pearson(), ranks(), score(), pearson(), ranks(), spearman()

### Community 113 - "5. Mapa de telas e funcionalidades"
Cohesion: 0.33
Nodes (6): 5. Mapa de telas e funcionalidades, Acesso demonstrativo, Aluno, Compartilhadas, Gestor, Professor

### Community 114 - "submissao.py"
Cohesion: 0.14
Nodes (20): AlunoResumo, AprovarRequest, _AtividadeBase, ConfirmarTextoRequest, CriarAtividadeLoteRequest, CriarAtividadeRequest, CriarMateriaRequest, CriterioResponse (+12 more)

### Community 115 - "routers/logs.py"
Cohesion: 0.30
Nodes (7): integridade(), logs_auditoria(), logs_seguranca(), _periodo(), AuditoriaResponse, EventoSegurancaResponse, IntegridadeResponse

### Community 116 - "variantes.py"
Cohesion: 0.11
Nodes (8): chamar(), _groq_key(), amostra(), CompetenciaV3, para_v2(), pegar(), ResultadoV3, _v3b()

### Community 117 - "6. Fluxos e estados"
Cohesion: 0.40
Nodes (5): 6. Fluxos e estados, Envio e aprovação, Navegação, Prática, Texto e arquivo

### Community 118 - "models/usuario.py"
Cohesion: 0.17
Nodes (7): StatusProcessamentoEnum, TipoDocumentoEnum, UsuarioTurmaPapelEnum, DocumentoBase, enviar_documento(), listar_documentos(), DocumentoBaseResponse

### Community 120 - "token"
Cohesion: 0.08
Nodes (55): _lote(), _objetiva(), _setup(), test_atividade_sem_autor_nao_aparece_para_professor_so_para_gestor(), test_depois_do_primeiro_envio_so_titulo_e_prazo_mudam(), test_editar_titulo_prazo_e_gabarito_enquanto_ninguem_enviou(), test_excluir_apaga_se_vazia_e_arquiva_se_tem_envio(), test_fila_traz_turma_e_filtra_por_turma() (+47 more)

### Community 121 - "Logs.tsx"
Cohesion: 0.22
Nodes (13): Aba, hora(), Logs(), verificar(), TIPOS, TOM(), AuditoriaAPI, consulta() (+5 more)

### Community 122 - "monta_base_externa.py"
Cohesion: 0.11
Nodes (8): gerar(), gerar(), norm(), notas(), palavras(), titulo(), valido(), 1.1 A atividade (o professor prepara)

### Community 123 - "correcoes.py"
Cohesion: 0.16
Nodes (23): StatusCorrecaoEnum, TipoAtividadeEnum, TipoMateriaEnum, Atividade, Correcao, CorrecaoCriterio, DominioAluno, Materia (+15 more)

### Community 124 - "Logs do sistema"
Cohesion: 0.29
Nodes (6): Acesso, Integridade, Logs do sistema, O que existe e onde fica, Railway (testes), VPS (depois)

### Community 125 - "Card"
Cohesion: 0.12
Nodes (39): Button(), Card(), SectionTitle(), PassoAPassoAgente(), EditarEscola(), Equipe(), Escolas(), ListaContas() (+31 more)

### Community 126 - "atividades.py"
Cohesion: 0.21
Nodes (9): garantir_competencias(), Tema, editar_atividade(), excluir_atividade(), _minha(), _tem_submissoes(), _apagar_arquivo(), _atividade_response() (+1 more)

### Community 127 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, lucide-react, react, react-dom, react-native-web

### Community 128 - "test_estudos.py"
Cohesion: 0.12
Nodes (12): hash_password(), _claude_falso(), test_gera_exercicios_para_as_piores_competencias_e_usa_cache(), gerar_contado(), test_professor_nao_usa_a_rota(), test_sem_chave_do_claude_responde_503(), test_sem_correcao_aprovada_responde_409(), token() (+4 more)

### Community 129 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, format, preview, test, test:e2e

### Community 130 - "dominio_do_aluno"
Cohesion: 0.47
Nodes (3): _compartilha_turma(), dominio_do_aluno(), meu_dominio()

### Community 131 - "2. Lógica (o que o agente faz)"
Cohesion: 0.33
Nodes (6): 2.1 Redação: o prompt (versão v14), 2.2 Matemática: conferir com o gabarito, 2.3 Validação, 2.4 Nota total e status, 2.5 Aprovação do professor, 2. Lógica (o que o agente faz)

### Community 134 - "usePwa.ts"
Cohesion: 0.36
Nodes (6): 8. PWA, Instalação, InstallEvent, isStandalone(), usePwa(), wasDismissed()

### Community 135 - "3. Versão por versão"
Cohesion: 0.33
Nodes (6): 3. Versão por versão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10), Fase 4: base INEP de 53 redações, foco na C3 (19/10), Fase 5: dia da entrega (20/10)

## Knowledge Gaps
- **94 isolated node(s):** `react-native-web`, `@types/react`, `@types/react-dom`, `@types/react-native-web`, `prettier` (+89 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 588 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `4. O que já foi feito (em ordem)` connect `routers/agente.py` to `Learning.tsx`, `CLAUDE.md: Domina`, `models/usuario.py`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **Are the 120 inferred relationships involving `Usuario` (e.g. with `registrar()` and `confirmar_senha()`) actually correct?**
  _`Usuario` has 120 INFERRED edges - model-reasoned connections that need verification._
- **What connects `react-native-web`, `@types/react`, `@types/react-dom` to the rest of the system?**
  _94 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Domina (plataforma de IA de correção e diagnóstico)` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._
- **Why does `ResultadoMini()` connect `Learning.tsx` to `routers/agente.py`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `PerfilEnum` (e.g. with `escola_do_escopo()` and `exigir_perfil()`) actually correct?**
  _`PerfilEnum` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Should `Activities.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07012987012987013 - nodes in this community are weakly interconnected._