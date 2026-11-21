# Graph Report - domina  (2026-11-21)

## Corpus Check
- 223 files · ~209,066 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 56 file(s) not represented in the graph (top: .jsonl 37, (none) 6, .xlsm 3)

## Summary
- 2291 nodes · 6369 edges · 162 communities (109 shown, 53 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 850 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `47bdfdef`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- ref_child_process
- Escopo do Protótipo
- E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita
- memoria.py
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- api
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Correcao
- routers/documento.py
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- test_fluxo_envio.py
- Custo Variável de IA/OCR
- Dependência: Hash de Senha
- Dependência: Pydantic
- Cautela sobre Estimativas
- routers/estudos.py
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
- Logs.tsx
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- test_agente.py
- exercicios.py
- correcoes.py
- test_exatas.py
- Learning.tsx
- Admin.tsx
- routers/metas.py
- Documentação do frontend Domina
- App.tsx
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- questoes.py
- request
- compilerOptions
- analisa_externa.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- Calendar.tsx
- Usuario
- E10 Privacidade e operação — LGPD, auditoria e custo
- test_gamificacao.py
- vercel.json
- token
- atividades.ts
- main.tsx
- ErroFerramenta
- E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA
- schemas/compliance.py
- vite-env.d.ts
- sys
- correcao_exatas.py
- CLAUDE.md: domina, correção de redação do ENEM por IA
- frontend/README.md
- LGPD (Lei Geral de Proteção de Dados)
- api.ts
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- Histórico das versões do prompt de correção (v1 a v21)
- CLAUDE.md: Domina
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh
- pydantic
- Domina · Frontend
- devDependencies
- monta_base_externa.py
- 5. Mapa de telas e funcionalidades
- submissoes.py
- test_memoria_ia.py
- registro.py
- registrar
- uuid
- dev.sh
- main.py
- routers/calendario.py
- routers/usuario.py
- models/usuario.py
- Logs do sistema
- app/gamificacao.py
- sqlalchemy
- dependencies
- Metas.tsx
- scripts
- routers/ocr.py
- routers/logs.py
- @playwright/test
- tema.ts
- usePwa.ts
- test_atividades.py
- nivel_de
- app/logs.py
- Professor e matéria (quem leciona o quê)
- vincular
- test_rbac.py
- calibra_groq.py
- Gamificação: níveis e metas
- 2026-11-16-verificac-a-o-po-s-ia-joa.md
- 6. Fluxos e estados
- 2026-11-17-verificac-a-o-17-11-graphify-joa.md
- 4. O que já foi feito (em ordem)
- test_metas.py
- config.py
- variantes.py
- test_calendario.py
- 2026-11-18-treinar-ia-por-mate-ria-18-joa.md
- test_logs.py
- Review Focus
- Status "Corrigida pela IA" nas atividades do aluno (task 1)
- XP, sequência e conquistas na "Minha evolução" (task 2)
- analisa.py
- minhas_metas
- ref_fs
- ref_os
- ref_path
- ref_url

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 208 edges
2. `request()` - 97 edges
3. `PerfilEnum` - 94 edges
4. `token()` - 62 edges
5. `Atividade` - 56 edges
6. `Materia` - 54 edges
7. `Correcao` - 46 edges
8. `Tema` - 45 edges
9. `registrar()` - 43 edges
10. `Submissao` - 42 edges

## Surprising Connections (you probably didn't know these)
- `2.1 Redação: o prompt (versão v14)` --references--> `ResultadoIA`  [INFERRED]
  README.md → backend/app/correcao.py
- `Como o progresso é calculado` --references--> `progresso()`  [INFERRED]
  docs/decisoes/gamificacao-niveis-e-metas.md → backend/app/metas.py
- `Visão geral do fluxo` --references--> `TipoMateriaEnum`  [INFERRED]
  README.md → backend/app/models/enum.py
- `Editar, arquivar e o que acontece com os pontos` --references--> `Meta`  [INFERRED]
  docs/decisoes/gamificacao-niveis-e-metas.md → backend/app/models/usuario.py
- `2.4 Nota total e status` --references--> `corrigir_submissao()`  [INFERRED]
  README.md → backend/app/routers/correcoes.py

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

## Communities (162 total, 53 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.11
Nodes (24): Exercicio, ExercicioResposta, Usuario, AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend) (+16 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.06
Nodes (49): initialActivities, ActivityDetail(), alternativasDe(), BarraAtividade(), compoeEnunciado(), destacarTrechos(), EditarAtividade(), FiguraQuestao() (+41 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (25): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Últimos 2–3 Dias — Buffer, Chamadas de IA Síncronas (sem fila), Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Escopo do Protótipo, Fila Assíncrona (Celery) — fora de escopo (+17 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 5 - "memoria.py"
Cohesion: 0.09
Nodes (43): aprendido(), buscar(), _chave(), concordancia(), _cosseno(), _do_professor(), _exemplo(), _fonte() (+35 more)

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.13
Nodes (16): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), Ponto em aberto: segunda matéria do MVP restrita às matérias do segundo dia do ENEM, RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP) (+8 more)

### Community 7 - "Relatório: teste de calibração da correção (14/10/2026)"
Cohesion: 0.15
Nodes (17): Calibração com 30–50 redações de nota conhecida (erro médio e viés por competência), Decisão em aberto: prompt × RAG × fine-tuning (conversar com o Igor), Correção por IA: calibração e decisão RAG/fine-tuning (13/10/2026), Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir), Opção 1: prompt com exemplos corrigidos (few-shot), Opção 2: RAG com redações corrigidas parecidas, Teste: redação ENEM 2023 do Igor (oficial 880; IA 600 → 680), Base de redações (essays/base_redacoes_enem_domina_ai.xlsm, 2.327 redações) (+9 more)

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
Cohesion: 0.11
Nodes (26): Atividade, AuditLog, Correcao, CorrecaoCriterio, CustoUso, DocumentoBase, DominioAluno, Escola (+18 more)

### Community 13 - "routers/documento.py"
Cohesion: 0.15
Nodes (43): TipoDocumentoEnum, DocumentoBase, apagar_instrucao(), baixar_documento(), criar_instrucao(), dispensar_sugestao(), enviar_documento(), erros_da_ia() (+35 more)

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
Cohesion: 0.14
Nodes (20): extract_text(), Exception, TextoPublicado, atividade_id(), Fluxo do aluno: login -> envia foto -> OCR (falso) -> confirma texto. cd…, test_aluno_gera_propria_correcao_e_professor_aprova_depois(), test_corrigir_faz_uma_correcao_so(), test_falha_do_gemini_nao_vaza_detalhe() (+12 more)

### Community 18 - "Custo Variável de IA/OCR"
Cohesion: 0.67
Nodes (3): Risco: custo variável de LLM e OCR por correção acima do previsto, RN-26 (Comercial): O valor por aluno deve superar o custo variável de IA e OCR por aluno; o preço só fecha depois de medir o custo real, RNF-17 (Custo): Custo variável por correção monitorado e abaixo do valor cobrado por aluno

### Community 23 - "routers/estudos.py"
Cohesion: 0.19
Nodes (23): _apresentar(), _base(), _erros_sem_exercicio(), ExercicioAluno, gerar_meus_exercicios(), _lote(), meus_exercicios(), minha_pratica() (+15 more)

### Community 58 - "Domina"
Cohesion: 0.14
Nodes (14): 1.2 A resposta do aluno, 1.3 O que mais vai para a IA, 1. Entrada (inputs), 2.1 Redação: o prompt (versão v14), 2.2 Matemática: conferir com o gabarito, 2.3 Validação, 2.4 Nota total e status, 2.5 Aprovação do professor (+6 more)

### Community 59 - "Logs.tsx"
Cohesion: 0.20
Nodes (14): Empty(), Aba, hora(), Logs(), verificar(), TIPOS, TOM(), AuditoriaAPI (+6 more)

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.12
Nodes (17): Achado: confiança da IA não serve (0,93–0,96 mesmo errando 500 pontos), E4 Correção por IA — Nota estimada, feedback e nível de confiança, Ponto em aberto: correção por gabarito (RF-18) — resolvido, tornou-se obrigatório no MVP, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção (+9 more)

### Community 61 - "test_agente.py"
Cohesion: 0.16
Nodes (21): CaixaIA, CompetenciaIA, corrigir(), PontoIA, BaseModel, field_validator, Correcao da redacao ENEM pelo Gemini nas 5 competencias do INEP. A nota fica…, ResultadoIA (+13 more)

### Community 62 - "exercicios.py"
Cohesion: 0.07
Nodes (78): contexto_do_professor(), So o texto do contexto (ver montar_contexto)., Exercicio, ExercicioResposta, Exercicio de PRATICA criado pelo professor (escrito por ele ou com ajuda da IA,…, _alunos_da_turma(), _alvo(), _aplicar() (+70 more)

### Community 63 - "correcoes.py"
Cohesion: 0.10
Nodes (45): Ferramenta, garantir_competencias(), Session, Cria (sem commit) as competencias que faltam na materia. Repetir nao duplica., avaliar_seguro(), Chamada depois de um envio/aprovacao: sessao propria e nunca derruba a…, AgenteExecucao, _ferramentas() (+37 more)

### Community 64 - "test_exatas.py"
Cohesion: 0.23
Nodes (18): criar_atividade_com_gabarito(), criar_turma_e_materia(), _gemini_falso(), Correcao de exercicios de materias exatas (matematica/fisica/quimica): gabarito…, test_aluno_gera_propria_correcao_exatas_e_professor_aprova_depois(), test_aprovar_exige_todos_os_criterios(), test_atividade_de_exatas_exige_gabarito(), test_enunciado_longo_nao_quebra_a_criacao() (+10 more)

### Community 65 - "Learning.tsx"
Cohesion: 0.07
Nodes (40): Task 3: tela "Minha evolução", RealSparkline(), Card(), SectionTitle(), COMO_GANHAR, dataCurta(), ICONE, PainelXP() (+32 more)

### Community 66 - "Admin.tsx"
Cohesion: 0.11
Nodes (28): BlocosResumo(), brl(), EditarConta(), EditarEscola(), Equipe(), Escolas(), mb(), mesAtual() (+20 more)

### Community 67 - "routers/metas.py"
Cohesion: 0.20
Nodes (26): pontos_do_aluno(), Meta, MetaConcluida, Meta de estudo criada por professor/gestor. Escopo: aluno_id preenchido =…, _alunos_da_escola(), _alunos_das_turmas(), criar_meta(), editar_meta() (+18 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.22
Nodes (9): 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual, 7. Persistência e contratos, 9. Usabilidade e acessibilidade (+1 more)

### Community 69 - "App.tsx"
Cohesion: 0.09
Nodes (43): Task 2: selo azul e linha da lista, App(), iniciais(), navItems, EvolutionChart(), InstallBanner(), Badge(), Button() (+35 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (13): Banco compartilhado + escola_id + RLS (estratégia escolhida), Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados (+5 more)

### Community 71 - "package.json"
Cohesion: 0.15
Nodes (13): name, private, type, version, prettier, react-native-web, @types/react, @types/react-dom (+5 more)

### Community 72 - "questoes.py"
Cohesion: 0.18
Nodes (23): editar_atividade(), excluir_atividade(), _minha(), delete, put, Session, UUID, Editar e excluir atividade. Quem pode: o professor da turma e o gestor da… (+15 more)

### Community 73 - "request"
Cohesion: 0.08
Nodes (49): Código, ListaContas(), NovaConta(), AdicionarMembro(), Classes(), Materials(), MateriasDoProfessor(), TIPOS_DOCUMENTO (+41 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "analisa_externa.py"
Cohesion: 0.38
Nodes (5): csv, pearson(), ranks(), Compara a IA com as notas humanas da base externa (AES-ENEM com 3 humanos,…, spearman()

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 77 - "Calendar.tsx"
Cohesion: 0.13
Nodes (22): iso(), useCalendario(), br(), Calendar(), apagar(), cobre(), MESES, NovoEvento() (+14 more)

### Community 78 - "Usuario"
Cohesion: 0.10
Nodes (65): leciona(), materias_do_professor(), materias_visiveis_do_aluno(), Session, O que o professor leciona (materia por turma, definido pelo gestor).…, Materias de que `usuario` pode ver estatistica deste aluno. None = todas…, Professor so cria atividade/exercicio de uma materia que ele da naquela turma.…, PerfilEnum (+57 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (13): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+5 more)

### Community 80 - "test_gamificacao.py"
Cohesion: 0.18
Nodes (27): Aprovacao, carregar_eventos(), Envio, MetaFeita, montar_xp(), Le do banco o que da XP. Envio: so confirmado e 1 por atividade (o primeiro).…, Resposta, conquista() (+19 more)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "token"
Cohesion: 0.24
Nodes (18): _objetivo(), Exercicios do professor: criar (objetivo/discursivo), IA sugere rascunhos,…, _setup(), test_aluno_ve_so_da_turma_e_gabarito_depois_de_responder(), test_criar_validacoes_e_permissoes(), test_discursivo_com_varias_respostas_de_exemplo(), test_editar_e_excluir_somem_para_o_aluno(), test_exercicio_so_para_alguns_alunos() (+10 more)

### Community 83 - "atividades.ts"
Cohesion: 0.10
Nodes (26): 4. O que já foi feito (resumo), Global Constraints, Review Focus, Status "Corrigida pela IA" (aluno): plano de implementação, Task 1: função de status do aluno, Task 3: abas de filtro do aluno, Task 4: cartões da Visão geral, Task 5: fechar (+18 more)

### Community 84 - "main.tsx"
Cohesion: 0.33
Nodes (5): frontend_src_styles, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, react-dom

### Community 85 - "ErroFerramenta"
Cohesion: 0.18
Nodes (13): ErroFerramenta, Exception, Erro esperado de uma ferramenta: volta para o agente como resultado com…, peso(), correcao_atual(), _corrigir(), corrigir_mat(), corrigir_redacao() (+5 more)

### Community 86 - "E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA"
Cohesion: 0.14
Nodes (15): Opção 3: fine-tuning com pares nota_ia × nota_professor, Laboratório /laboratorio/ (foto → texto → nota), E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA, Ponto em aberto: LLM própria — resolvido (não treinar modelo do zero), RF-20 (Revisão): Nenhuma correção é liberada ao aluno sem aprovação do professor, RF-21 (Revisão): Professor edita nota e feedback e aceita ou rejeita a sugestão por critério, RF-22 (Revisão): Guardar a nota da IA e a nota final do professor, para medir concordância, Risco: correção de IA errada ou inconsistente (+7 more)

### Community 87 - "schemas/compliance.py"
Cohesion: 0.53
Nodes (5): AuditLogResponse, ConsentimentoRequest, ConsentimentoResponse, CustoUsoResponse, BaseModel

### Community 89 - "sys"
Cohesion: 0.30
Nodes (7): Roda calibra.py com prompt de arquivo na planilha externa. uso (de backend/):…, Roda calibra.py com prompt de arquivo na base INEP (nota oficial). uso (de…, Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da…, Igual ao roda_inep.py, mas junta as redacoes 51-53 (novas_51_53.jsonl) as 50 da…, openpyxl, runpy, sys

### Community 90 - "correcao_exatas.py"
Cohesion: 0.10
Nodes (26): corrigir(), BaseModel, field_validator, QuestaoCorrigida, Correcao de exercicios de materias exatas (matematica, fisica, quimica) pelo…, ResultadoExatasIA, ArquivoNaoLido, _docx() (+18 more)

### Community 91 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 92 - "frontend/README.md"
Cohesion: 0.17
Nodes (6): Publicar o Domina na Vercel, Verificação no celular, Limites da validação, Roteiro manual, Validação do frontend, Verificação automatizada

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (8): Ponto em aberto: retenção de conteudo_bruto, LGPD (Lei Geral de Proteção de Dados), Ponto em aberto: RN-21 (dados não usados para treinar modelos de terceiros) mantida, pendente confirmação do usuário, Risco: dados de menores de idade (legal e reputacional), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

### Community 94 - "api.ts"
Cohesion: 0.07
Nodes (46): erroDe(), ExerciciosProfessor(), FormExercicio(), LinhaResposta(), Rascunho, RespostasExercicio(), ResumoTurma(), vazio (+38 more)

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

### Community 101 - "CLAUDE.md: Domina"
Cohesion: 0.25
Nodes (7): 1. O que é o Domina, 2. Onde as coisas estão, 3. Regras de trabalho (preferências do usuário), 5. Correção da redação: estado do prompt, 6. Mapa rápido do código, CLAUDE.md: Domina, IA própria: resumo (detalhe da memória, tela e migrations 0024 a 0030 em `docs/historico_domina.md` e `docs/decisoes/ia-propria.md`)

### Community 109 - "pydantic"
Cohesion: 0.18
Nodes (17): ExercicioExatasGerado, ExercicioGerado, gerar_exercicios(), gerar_exercicios_exatas(), BaseModel, Geracao de exercicios de pratica (plano de estudo) pelo Claude Haiku, a partir…, erros: linhas ErroAluno; nomes_materia: materia_id -> nome. Um exercicio por…, Grava (sem commit) um exercicio por erro, ligado ao erro e a materia (sem… (+9 more)

### Community 110 - "Domina · Frontend"
Cohesion: 0.18
Nodes (11): Comandos, Conexão com o backend, Documentação, Domina · Frontend, Executar, Experimente o fluxo, O agente de correção na tela, O que o frontend faz (+3 more)

### Community 111 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, @playwright/test, prettier, @types/react, @types/react-dom, @types/react-native-web, typescript, vite (+3 more)

### Community 112 - "monta_base_externa.py"
Cohesion: 0.11
Nodes (16): ast, gerar(), gerar(), collections, copy, norm(), notas(), palavras() (+8 more)

### Community 113 - "5. Mapa de telas e funcionalidades"
Cohesion: 0.33
Nodes (6): 5. Mapa de telas e funcionalidades, Acesso demonstrativo, Aluno, Compartilhadas, Gestor, Professor

### Community 114 - "submissoes.py"
Cohesion: 0.14
Nodes (28): Folhas de um envio por foto, em ordem (ordem 0 = primeira). Envio antigo, de…, SubmissaoPagina, AlunoResumo, AprovarRequest, _AtividadeBase, AtividadeResponse, AvaliacaoIARequest, ConfirmarTextoRequest (+20 more)

### Community 115 - "test_memoria_ia.py"
Cohesion: 0.13
Nodes (30): dividir(), Corta o texto em trechos de ~tamanho letras, respeitando paragrafos; cada…, concorda_pouco(), IaChamada, Material de treino da IA propria: um pedido ao modelo de fora e a resposta…, apagar_treinados(), espia_gemini(), gerar() (+22 more)

### Community 116 - "registro.py"
Cohesion: 0.15
Nodes (17): BaseModel, IA ajudando o PROFESSOR a criar exercicios de pratica: rascunhos sobre um tema…, _RespostaExemplo, _RespostaSugestao, sugerir_exercicios(), sugerir_resposta_exemplo(), SugestaoExercicio, anotar() (+9 more)

### Community 117 - "registrar"
Cohesion: 0.17
Nodes (20): _campos(), Session, Log de auditoria (quem fez o que sobre quais dados), append-only e com cadeia…, registrar(), verificar_auditoria(), hash_de(), proximo_elo(), Session (+12 more)

### Community 118 - "uuid"
Cohesion: 0.13
Nodes (17): criar_escola(), editar_escola(), listar_escolas(), get, post, put, Session, UUID (+9 more)

### Community 120 - "main.py"
Cohesion: 0.07
Nodes (51): escola_do_escopo(), escola_inativa(), exigir_perfil(), get_current_user(), Session, UUID, Dependencia: so deixa passar quem tem um dos perfis., Escola sobre a qual a consulta vale. E AQUI que o RBAC acontece, no backend. -… (+43 more)

### Community 121 - "routers/calendario.py"
Cohesion: 0.14
Nodes (31): feriados(), _pascoa(), date, Feriados nacionais do Brasil de um ano, calculados (nao precisam de manutencao…, metas_do_aluno(), Metas ativas que valem para o aluno: da escola toda, das turmas dele ou so dele., Evento, Calendario da escola: uma tabela so, todo mundo le dela (por isso fica… (+23 more)

### Community 122 - "routers/usuario.py"
Cohesion: 0.19
Nodes (29): confirmar_senha(), Reautenticacao em acao sensivel: o JWT roubado/esquecido aberto nao basta, pede…, _aplicar_vinculos(), ativar_ou_desativar(), criar_usuario(), definir_vinculos(), editar_usuario(), _gerido() (+21 more)

### Community 123 - "models/usuario.py"
Cohesion: 0.10
Nodes (58): hash_password(), As 5 competencias da redacao do ENEM (INEP). Cada uma vira um Tema da materia…, _detalhe(), Session, Onde o aluno erra em exatas. Le as correcoes APROVADAS e guarda cada questao em…, Grava (sem commit) os erros novos do aluno. Devolve quantos criou., registrar_erros(), erros_da_ia() (+50 more)

### Community 124 - "Logs do sistema"
Cohesion: 0.29
Nodes (6): Acesso, Integridade, Logs do sistema, O que existe e onde fica, Railway (testes), VPS (depois)

### Community 125 - "app/gamificacao.py"
Cohesion: 0.17
Nodes (15): dia_local(), hoje_local(), date, datetime, _quando_atinge(), XP, sequencia de dias e conquistas do aluno (docs/decisoes/gamificacao-niveis-…, O banco grava UTC (server_default now()). O dia de estudo/prazo e o dia em…, Resultado completo de montar_xp para um aluno. (+7 more)

### Community 126 - "sqlalchemy"
Cohesion: 0.03
Nodes (8): alembic, alembic_config, Aplica as migracoes do Alembic. Banco que ja existia (criado pelo create_all…, Alembic usa o mesmo banco e os mesmos modelos do app (app.database /…, sqlalchemy, sqlalchemy_dialects, sqlalchemy_dialects_postgresql, typing

### Community 127 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, lucide-react, react, react-dom, react-native-web

### Community 128 - "Metas.tsx"
Cohesion: 0.13
Nodes (22): br(), EditarMeta(), MetaLinha(), Metas(), MetasAluno(), MetasEquipe(), NovaMeta(), Ranking() (+14 more)

### Community 129 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, format, preview, test, test:e2e

### Community 130 - "routers/ocr.py"
Cohesion: 0.18
Nodes (15): Session, registrar_uso(), CustoUso, extract_text_from_image(), ler_folhas(), ler_imagem(), ocr(), post (+7 more)

### Community 131 - "routers/logs.py"
Cohesion: 0.28
Nodes (14): integridade(), logs_auditoria(), logs_seguranca(), _periodo(), date, get, Session, UUID (+6 more)

### Community 133 - "tema.ts"
Cohesion: 0.47
Nodes (5): Aparencia(), aplicarTema(), lerTema(), salvarTema(), Tema

### Community 134 - "usePwa.ts"
Cohesion: 0.36
Nodes (6): 8. PWA, Instalação, InstallEvent, isStandalone(), usePwa(), wasDismissed()

### Community 135 - "test_atividades.py"
Cohesion: 0.24
Nodes (19): _lote(), _objetiva(), Professor com varias turmas: lancar em lote, editar e excluir/arquivar…, Um professor PROPRIO deste teste (nao mexe no do seed, que os outros testes…, _setup(), test_atividade_sem_autor_nao_aparece_para_professor_so_para_gestor(), test_depois_do_primeiro_envio_so_titulo_e_prazo_mudam(), test_editar_titulo_prazo_e_gabarito_enquanto_ninguem_enviou() (+11 more)

### Community 136 - "nivel_de"
Cohesion: 0.40
Nodes (5): nivel_de(), minha_gamificacao(), get, Session, test_faixas_de_nivel()

### Community 137 - "app/logs.py"
Cohesion: 0.12
Nodes (17): configurar_logging(), ip_do_cliente(), JsonFormatter, novo_request_id(), Request, Logging do sistema: JSON em stdout (uma linha por evento) + contexto da…, IP real. Atras do proxy (Railway, Nginx) o IP do socket e o do proxy; o real…, access_log() (+9 more)

### Community 140 - "Professor e matéria (quem leciona o quê)"
Cohesion: 0.29
Nodes (6): Cadastro de pessoas pelo gestor (tela "Equipe e alunos"), Como o gestor define, Migration 0022, O que muda para o professor, Professor e matéria (quem leciona o quê), Regra

### Community 141 - "vincular"
Cohesion: 0.17
Nodes (15): _enviar(), Materiais: vinculo com materia, visibilidade por professor, baixar e arquivar.…, _segundo_professor(), test_envio_vincula_materia_valida_arquivo_baixa_e_arquiva(), token(), _gemini_falso(), Evolucao real por materia: historico de correcoes aprovadas, agrupado por…, test_evolucao_agrupa_por_materia_sem_tocar_dominio() (+7 more)

### Community 143 - "test_rbac.py"
Cohesion: 0.23
Nodes (15): test_admin_precisa_da_escola_e_feriados_calculados(), test_telas_de_log_so_para_quem_pode_e_gestor_so_ve_a_propria_escola(), escola_id(), novo(), Administrador x Gestor: o isolamento por escola e garantido no backend (RBAC),…, test_admin_cria_escola_gestor_e_professor(), test_admin_lista_turmas_da_escola_e_cria_conta_nela(), test_admin_ve_cada_escola_e_o_total() (+7 more)

### Community 144 - "calibra_groq.py"
Cohesion: 0.22
Nodes (4): Mede a correcao da IA contra notas conhecidas, via Groq (gratis). Nao altera o…, Roda corrigir() do app (v12, 2 correcoes + media) nas 53 do INEP. uso (de…, httpx, time

### Community 146 - "Gamificação: níveis e metas"
Cohesion: 0.14
Nodes (13): Como o aluno sobe de nível (XP, desde 18/11/2026), Como o progresso é calculado, Critérios de uma meta (quando ela conta como cumprida), Editar, arquivar e o que acontece com os pontos, Gamificação: níveis e metas, Ideia em uma frase, O que o sistema não faz (de propósito), Plano de estudo de exatas: onde o aluno erra (+5 more)

### Community 147 - "2026-11-16-verificac-a-o-po-s-ia-joa.md"
Cohesion: 0.50
Nodes (3): Decided, Tried and ruled out, Watch out

### Community 148 - "6. Fluxos e estados"
Cohesion: 0.40
Nodes (5): 6. Fluxos e estados, Envio e aprovação, Navegação, Prática, Texto e arquivo

### Community 149 - "2026-11-17-verificac-a-o-17-11-graphify-joa.md"
Cohesion: 0.50
Nodes (3): Decided, Tried and ruled out, Watch out

### Community 151 - "4. O que já foi feito (em ordem)"
Cohesion: 0.33
Nodes (6): finalizar(), ler_envio(), 4. O que já foi feito (em ordem), Histórico detalhado do Domina (tirado do CLAUDE.md em 18/11/2026), ResultadoMini(), O agente de correção

### Community 152 - "test_metas.py"
Cohesion: 0.36
Nodes (11): _entregar_objetiva(), _meta(), Niveis e metas: escopo (escola/turma/aluno), conclusao automatica, nivel por…, Turma, professor e dois alunos PROPRIOS deste teste (nao mexe nos do seed)., Cria uma prova objetiva de 1 questao na turma e o aluno acerta (correcao nasce…, _setup(), test_editar_arquivar_e_pontos_ficam(), test_escopo_e_permissoes_de_criacao() (+3 more)

### Community 154 - "config.py"
Cohesion: 0.11
Nodes (20): Anthropic, Agente de correcao: o Claude recebe um objetivo e decide sozinho quais…, Roda o loop ate o agente chamar a ferramenta de fim (terminou() vira True) ou…, _resumo(), rodar(), Settings, embutir(), Texto -> vetor, para achar trechos parecidos pelo SENTIDO (nao so pelas mesmas… (+12 more)

### Community 160 - "variantes.py"
Cohesion: 0.27
Nodes (8): CompetenciaV3, para_v2(), pegar(), BaseModel, Variantes de prompt para o teste de calibracao (nao fazem parte do projeto)., ResultadoV3, _v3b(), random

### Community 161 - "test_calendario.py"
Cohesion: 0.44
Nodes (9): _evento(), Calendario por escola: todos da escola veem o mesmo dado; o resto e RBAC no…, test_aluno_nao_ve_evento_de_turma_alheia_e_feriado_vem_pronto(), test_evento_da_escola_toda_aparece_para_todos_e_nao_vaza_para_outra_escola(), test_lembrete_do_aluno_e_so_dele(), test_professor_nao_apaga_evento_do_gestor_mas_gestor_apaga_o_dele(), test_professor_so_cria_para_a_propria_turma(), _titulos() (+1 more)

### Community 162 - "2026-11-18-treinar-ia-por-mate-ria-18-joa.md"
Cohesion: 0.50
Nodes (3): Decided, Tried and ruled out, Watch out

### Community 164 - "test_logs.py"
Cohesion: 0.19
Nodes (17): EventoSeguranca, Log de autenticacao/acesso. Append-only: a aplicacao so faz INSERT (nunca…, Session, verificar_cadeia(), aplicar(), Retencao dos logs no banco. Rodar periodicamente (Railway Cron / cron da VPS):…, _eventos(), Access log em JSON, eventos de seguranca no banco e IP atras de proxy. (+9 more)

### Community 165 - "Review Focus"
Cohesion: 0.25
Nodes (7): Global Constraints, Review Focus, Task 1: contas de XP (função pura), Task 2: leitura do banco e rotas, Task 4: XP na Visão geral e em Metas, Task 5: fechar, XP e gamificação: plano de implementação

### Community 169 - "Status "Corrigida pela IA" nas atividades do aluno (task 1)"
Cohesion: 0.29
Nodes (6): Abordagens, Decisões minhas (para o usuário conferir), Fora do escopo, O que muda (aprovado pelo usuário em 17/11), Por quê, Status "Corrigida pela IA" nas atividades do aluno (task 1)

### Community 170 - "XP, sequência e conquistas na "Minha evolução" (task 2)"
Cohesion: 0.29
Nodes (6): Abordagens, Decidido com o usuário (18/11), Decisões minhas (para conferir), Fora do escopo, Por quê, XP, sequência e conquistas na "Minha evolução" (task 2)

### Community 173 - "analisa.py"
Cohesion: 0.38
Nodes (5): pearson(), ranks(), score(), Compara a IA com a nota oficial do INEP. uso: python analisa_inep.py <ia.jsonl>…, statistics

### Community 179 - "minhas_metas"
Cohesion: 0.20
Nodes (15): minhas_metas(), ConquistaResponse, MinhaGamificacaoResponse, BaseModel, SequenciaResponse, XpItem, MetaAlunoResponse, MetaEditRequest (+7 more)

## Knowledge Gaps
- **354 isolated node(s):** `dev.sh script`, `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script`, `roda_v12.sh script` (+349 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 765 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IA própria: memória do professor (RAG) — 2026-11-16` connect `memoria.py` to `request`, `Activities.tsx`, `4. O que já foi feito (em ordem)`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `Materials()` connect `request` to `App.tsx`, `memoria.py`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `concordancia()` connect `memoria.py` to `models/usuario.py`, `correcoes.py`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 168 inferred relationships involving `Usuario` (e.g. with `registrar()` and `confirmar_senha()`) actually correct?**
  _`Usuario` has 168 INFERRED edges - model-reasoned connections that need verification._
- **Are the 64 inferred relationships involving `PerfilEnum` (e.g. with `escola_do_escopo()` and `exigir_perfil()`) actually correct?**
  _`PerfilEnum` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Atividade` (e.g. with `registrar_erros()` and `carregar_eventos()`) actually correct?**
  _`Atividade` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `dev.sh script`, `roda_dupla.sh script`, `roda_v10.sh script` to the rest of the system?**
  _354 weakly-connected nodes found - possible documentation gaps or missing edges._