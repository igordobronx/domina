# Graph Report - domina  (2026-11-09)

## Corpus Check
- 116 files · ~133,134 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 51 file(s) not represented in the graph (top: .jsonl 37, (none) 5, .xlsm 3)

## Summary
- 1171 nodes · 2585 edges · 104 communities (57 shown, 47 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 310 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ebfe3ec2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- Usuario
- Divisão por Pessoa (cronograma de 2 semanas)
- E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita
- routers/agente.py
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- api
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Correcao
- Dashboard.tsx
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- _ferramentas
- Custo Variável de IA/OCR
- Dependência: Hash de Senha
- Dependência: Pydantic
- Cautela sobre Estimativas
- monta_base_externa.py
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
- routers/compliance.py
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- correcoes.py
- models/usuario.py
- submissoes.py
- test_exatas.py
- Learning.tsx
- Usuario
- Escopo do Protótipo
- Documentação do frontend Domina
- routers/evolucao.py
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- erro_nao_tratado
- api.ts
- compilerOptions
- test_estudos.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- extract_text_from_image
- test_fluxo_envio.py
- E10 Privacidade e operação — LGPD, auditoria e custo
- DominioAluno
- vercel.json
- usePwa.ts
- App.tsx
- atividades.ts
- vite-env.d.ts
- Domina
- rodar_agente
- Settings.tsx
- LGPD (Lei Geral de Proteção de Dados)
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- criar_usuario
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 70 edges
2. `PerfilEnum` - 40 edges
3. `request()` - 35 edges
4. `Domina (plataforma de IA de correção e diagnóstico)` - 30 edges
5. `Atividade` - 29 edges
6. `_ferramentas()` - 27 edges
7. `corrigir_submissao()` - 23 edges
8. `Materia` - 21 edges
9. `Submissao` - 19 edges
10. `Correcao` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Laboratório /laboratorio/ (foto → texto → nota)` --references--> `corrigir()`  [EXTRACTED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → backend/app/correcao.py
- `Prompt de correção v2 (descritores oficiais do INEP por nível)` --references--> `corrigir()`  [EXTRACTED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → backend/app/correcao.py
- `Prompt de correção v2 (descritores oficiais do INEP por nível)` --implements--> `E4 Correção por IA — Nota estimada, feedback e nível de confiança`  [INFERRED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf
- `gerar()` --indirect_call--> `notas()`  [INFERRED]
  backend/tests/test_evolucao.py → docs/calibracao/2026-10-16/monta_base_externa.py
- `gerar()` --indirect_call--> `notas()`  [INFERRED]
  backend/tests/test_exatas.py → docs/calibracao/2026-10-16/monta_base_externa.py

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

## Communities (104 total, 47 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.13
Nodes (17): AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend), Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança), IPE (piloto institucional desejado), João Pedro (Co-fundador; estatística, matemática e IA; ponte de entrada no CEIA via UFG) (+9 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.10
Nodes (33): ActivityDetail(), compoeEnunciado(), destacarTrechos(), ImagemComCaixas(), MATERIAS_COM_GABARITO, NOMES_FERRAMENTAS, NOTAS_ENEM, NovaAtividade() (+25 more)

### Community 2 - "Usuario"
Cohesion: 0.19
Nodes (35): PerfilEnum, UsuarioTurmaPapelEnum, Turma, Usuario, UsuarioTurma, _atividade_response(), confirmar_texto(), criar_atividade() (+27 more)

### Community 3 - "Divisão por Pessoa (cronograma de 2 semanas)"
Cohesion: 0.22
Nodes (13): Últimos 2–3 Dias — Buffer, Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, João Pedro, Lucas, Motor de Correção (prompt ancorado nas 5 competências + API de LLM), Motor de Diagnóstico de Domínio (percentual por competência) (+5 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 5 - "routers/agente.py"
Cohesion: 0.14
Nodes (20): Session, registrar(), get_current_user(), Session, decode_access_token(), Settings, get_db(), AuditLog (+12 more)

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.18
Nodes (11): E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Ponto em aberto: segunda matéria do MVP restrita às matérias do segundo dia do ENEM, RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-09 (Matéria e base): Versionar a base de uma matéria, registrando quem mudou o quê e quando, RN-04 (Correção): A IA só corrige com critérios de uma base de matéria aprovada por um professor; sem base aprovada, não corrige, US-03 (MVP): Como professor de redação, quero começar com as 5 competências do ENEM já carregadas, para usar sem configurar nada (+3 more)

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

### Community 12 - "Correcao"
Cohesion: 0.17
Nodes (16): Atividade, Correcao, CorrecaoCriterio, DocumentoBase, Materia, Submissao, Tema, Arquitetura: Base da matéria (temas e critérios validados pelo professor) (+8 more)

### Community 13 - "Dashboard.tsx"
Cohesion: 0.15
Nodes (21): EvolutionChart(), RealSparkline(), Card(), Empty(), initialActivities, initialState, studyTasks, topics (+13 more)

### Community 14 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (6): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos, Risco: capacidade de execução (equipe de quatro, ainda validando divisão de papéis), Risco: dependência de poucos pilotos

### Community 15 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 16 - "Modelo de Cobrança"
Cohesion: 0.67
Nodes (3): Ponto em aberto: definição de "aluno ativo" para cobrança, Ponto em aberto: preço (rascunho R$1.000 fixos + R$8/aluno, sem validação), RN-24 (Comercial): Cobrança proposta: mensalidade fixa por escola mais valor por aluno ativo por mês. Rascunho: R$ 1.000 fixos + R$ 8 por aluno; ainda não validado

### Community 17 - "_ferramentas"
Cohesion: 0.07
Nodes (39): Anthropic, ErroFerramenta, Ferramenta, Exception, Agente de correcao: o Claude recebe um objetivo e decide sozinho quais…, Erro esperado de uma ferramenta: volta para o agente como resultado com…, Roda o loop ate o agente chamar a ferramenta de fim (terminou() vira True) ou…, _resumo() (+31 more)

### Community 18 - "Custo Variável de IA/OCR"
Cohesion: 0.67
Nodes (3): Risco: custo variável de LLM e OCR por correção acima do previsto, RN-26 (Comercial): O valor por aluno deve superar o custo variável de IA e OCR por aluno; o preço só fecha depois de medir o custo real, RNF-17 (Custo): Custo variável por correção monitorado e abaixo do valor cobrado por aluno

### Community 23 - "monta_base_externa.py"
Cohesion: 0.05
Nodes (45): ast, pearson(), ranks(), score(), Mede a correcao da IA contra notas conhecidas, via Groq (gratis). Nao altera o…, Mede a correcao da IA contra notas conhecidas (so texto, sem OCR). Nao altera o…, CompetenciaV3, para_v2() (+37 more)

### Community 58 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 59 - "routers/compliance.py"
Cohesion: 0.26
Nodes (15): ConsentimentoLGPD, custo_uso_do_mes(), listar_auditoria(), meu_consentimento(), get, post, Session, registrar_consentimento() (+7 more)

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.15
Nodes (14): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E4 Correção por IA — Nota estimada, feedback e nível de confiança, Ponto em aberto: correção por gabarito (RF-18) — resolvido, tornou-se obrigatório no MVP, RF-14 (Correção): Corrigir redação do ENEM com nota estimada por competência (0 a 200) e total, com justificativa, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção (+6 more)

### Community 61 - "correcoes.py"
Cohesion: 0.24
Nodes (26): StatusCorrecaoEnum, Atividade, Correcao, CorrecaoCriterio, Submissao, Tema, aprovar_correcao(), _atualizar_dominio() (+18 more)

### Community 62 - "models/usuario.py"
Cohesion: 0.12
Nodes (27): Session, registrar_uso(), StatusProcessamentoEnum, TipoAtividadeEnum, TipoDocumentoEnum, TipoMateriaEnum, AgenteExecucao, CustoUso (+19 more)

### Community 63 - "submissoes.py"
Cohesion: 0.17
Nodes (23): TipoEnvioEnum, AlunoResumo, AprovarRequest, AtividadeResponse, ConfirmarTextoRequest, CorrecaoResponse, CorrigirRequest, CriarAtividadeRequest (+15 more)

### Community 64 - "test_exatas.py"
Cohesion: 0.17
Nodes (22): _gemini_falso(), gerar(), Evolucao real por materia: historico de correcoes aprovadas, agrupado por…, test_evolucao_agrupa_por_materia_sem_tocar_dominio(), test_evolucao_so_para_aluno(), token(), criar_atividade_com_gabarito(), criar_turma_e_materia() (+14 more)

### Community 65 - "Learning.tsx"
Cohesion: 0.15
Nodes (16): Dashboard(), doBackend(), doDemo(), Evolution(), ExercicioComum, HABILIDADE_NOME, Studies(), DominioAPI (+8 more)

### Community 66 - "Usuario"
Cohesion: 0.20
Nodes (12): AuditLog, CustoUso, Escola, Ponto em aberto: particionamento de AuditLog e CustoUso, Turma, Usuario, UsuarioTurma, Perfil: Administrador Domina (+4 more)

### Community 67 - "Escopo do Protótipo"
Cohesion: 0.17
Nodes (12): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Chamadas de IA Síncronas (sem fila), Escopo do Protótipo, Fila Assíncrona (Celery) — fora de escopo, Gustavo, Igor, Ingestão Genérica de Documento de Qualquer Escola — fora de escopo, Modelo de Dados Reduzido + Endpoints de Envio e Listagem (+4 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.05
Nodes (39): Publicar o Domina na Vercel, Verificação no celular, 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual (+31 more)

### Community 69 - "routers/evolucao.py"
Cohesion: 0.33
Nodes (8): minha_evolucao(), get, Session, EvolucaoMateriaResponse, EvolucaoPontoResponse, BaseModel, sqlalchemy, uuid

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (13): Banco compartilhado + escola_id + RLS (estratégia escolhida), Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados (+5 more)

### Community 71 - "package.json"
Cohesion: 0.04
Nodes (45): dependencies, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, lucide-react, react, react-dom, react-native-web (+37 more)

### Community 72 - "erro_nao_tratado"
Cohesion: 0.40
Nodes (5): erro_nao_tratado(), Exception, exception_handler, JSONResponse, Request

### Community 73 - "api.ts"
Cohesion: 0.12
Nodes (29): AdicionarMembro(), AlunoRow(), Classes(), Materials(), TIPOS_DOCUMENTO, TurmaCard(), CaixaAPI, ConsentimentoAPI (+21 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "test_estudos.py"
Cohesion: 0.14
Nodes (19): create_access_token(), hash_password(), verify_password(), login(), post, Session, LoginRequest, BaseModel (+11 more)

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 77 - "extract_text_from_image"
Cohesion: 0.25
Nodes (8): extract_text_from_image(), ler_imagem(), ocr(), post, Session, UploadFile, OCRResponse, BaseModel

### Community 78 - "test_fluxo_envio.py"
Cohesion: 0.06
Nodes (55): CaixaIA, CompetenciaIA, corrigir(), corrigir(), BaseModel, field_validator, QuestaoCorrigida, Correcao de exercicios de materias exatas (matematica, fisica, quimica) pelo… (+47 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (13): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+5 more)

### Community 80 - "DominioAluno"
Cohesion: 0.33
Nodes (7): DominioAluno, Exercicio, ExercicioResposta, Arquitetura: Motor de domínio (% por tema; só com correção aprovada), Arquitetura: Painéis (aluno, professor e gestor), Arquitetura: Professor revisa (aprova, edita ou rejeita cada nota), Arquitetura: Recomendação (temas a estudar e exercícios)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "usePwa.ts"
Cohesion: 0.53
Nodes (4): InstallEvent, isStandalone(), usePwa(), wasDismissed()

### Community 84 - "App.tsx"
Cohesion: 0.11
Nodes (26): App(), iniciais(), navItems, InstallBanner(), Button(), IconButton(), Logo(), Modal() (+18 more)

### Community 86 - "atividades.ts"
Cohesion: 0.29
Nodes (11): Activities(), listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData(), paraStatus() (+3 more)

### Community 89 - "Domina"
Cohesion: 0.06
Nodes (31): 1. Como ler os números, 2. Tabela resumo, 3. Versão por versão, 4. O que aprendemos, 5. Conclusão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10) (+23 more)

### Community 90 - "rodar_agente"
Cohesion: 0.29
Nodes (10): get, post, Session, UUID, _resposta(), rodar_agente(), ver_agente(), AgenteRequest (+2 more)

### Community 91 - "Settings.tsx"
Cohesion: 0.23
Nodes (11): Badge(), Consentimento(), CustoEAuditoria(), Help(), Settings(), auditLog(), AuditLogAPI, custoUso() (+3 more)

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

### Community 101 - "criar_usuario"
Cohesion: 0.17
Nodes (16): criar_usuario(), listar_usuarios(), meu_usuario(), get, post, Session, _resposta(), CriarTurmaRequest (+8 more)

## Knowledge Gaps
- **292 isolated node(s):** `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script`, `roda_v12.sh script`, `roda_v9.sh script` (+287 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 450 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prompt de correção v2 (descritores oficiais do INEP por nível)` connect `test_fluxo_envio.py` to `E4 Correção por IA — Nota estimada, feedback e nível de confiança`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `Domina (plataforma de IA de correção e diagnóstico)` connect `Domina (plataforma de IA de correção e diagnóstico)` to `Usuario`, `E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita`, `E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria`, `Banco compartilhado + escola_id + RLS (estratégia escolhida)`, `Relatório: teste de calibração da correção (14/10/2026)`, `E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios`, `Diagnóstico de Domínio`, `Tendências do ENEM`, `E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor`, `E10 Privacidade e operação — LGPD, auditoria e custo`, `E4 Correção por IA — Nota estimada, feedback e nível de confiança`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `E4 Correção por IA — Nota estimada, feedback e nível de confiança` connect `E4 Correção por IA — Nota estimada, feedback e nível de confiança` to `Domina (plataforma de IA de correção e diagnóstico)`, `E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita`, `test_fluxo_envio.py`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Usuario` (e.g. with `get_current_user()` and `PerfilEnum`) actually correct?**
  _`Usuario` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `PerfilEnum` (e.g. with `Usuario` and `registrar_consentimento()`) actually correct?**
  _`PerfilEnum` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Atividade` (e.g. with `TipoAtividadeEnum` and `_ferramentas()`) actually correct?**
  _`Atividade` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script` to the rest of the system?**
  _292 weakly-connected nodes found - possible documentation gaps or missing edges._