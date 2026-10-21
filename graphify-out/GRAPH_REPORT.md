# Graph Report - domina  (2026-10-21)

## Corpus Check
- 109 files · ~125,627 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 51 file(s) not represented in the graph (top: .jsonl 37, (none) 5, .xlsm 3)

## Summary
- 1055 nodes · 2243 edges · 110 communities (51 shown, 59 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 279 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `734d6076`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- submissoes.py
- Escopo do Protótipo
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- extract_text_from_image
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- app
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Escola
- app_auth_dependencies
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- app_models
- Custo Variável de IA/OCR
- Dependência: Hash de Senha
- Dependência: Pydantic
- Cautela sobre Estimativas
- app_models_enum
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
- app_routers
- google_auth_exceptions
- google_cloud
- app_models_usuario
- test_estudos.py
- app_routers_ocr
- app_schemas_ocr
- app_schemas_submissao
- Documentação do frontend Domina
- variantes.py
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- main.py
- api.ts
- compilerOptions
- routers/auth.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- app_ocr_gemini
- test_fluxo_envio.py
- E10 Privacidade e operação — LGPD, auditoria e custo
- routers/dominio.py
- vercel.json
- Dashboard.tsx
- Learning.tsx
- App.tsx
- Correcao
- atividades.ts
- vite-env.d.ts
- Histórico das versões do prompt de correção (v1 a v21)
- pydantic
- Settings.tsx
- routers/usuario.py
- LGPD (Lei Geral de Proteção de Dados)
- usePwa.ts
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- routers/turma.py
- routers/ocr.py
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh
- DominioAluno

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 65 edges
2. `PerfilEnum` - 40 edges
3. `request()` - 33 edges
4. `Domina (plataforma de IA de correção e diagnóstico)` - 30 edges
5. `Atividade` - 23 edges
6. `corrigir_submissao()` - 19 edges
7. `Materia` - 18 edges
8. `aprovar_correcao()` - 17 edges
9. `UsuarioTurma` - 16 edges
10. `Submissao` - 16 edges

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

## Communities (110 total, 59 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.11
Nodes (24): Exercicio, ExercicioResposta, Usuario, AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend) (+16 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.12
Nodes (28): ActivityDetail(), compoeEnunciado(), destacarTrechos(), ImagemComCaixas(), MATERIAS_COM_GABARITO, NOTAS_ENEM, NovaAtividade(), Ponto (+20 more)

### Community 2 - "submissoes.py"
Cohesion: 0.07
Nodes (113): Session, registrar(), PerfilEnum, StatusCorrecaoEnum, StatusProcessamentoEnum, TipoAtividadeEnum, TipoDocumentoEnum, TipoEnvioEnum (+105 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (26): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Últimos 2–3 Dias — Buffer, Chamadas de IA Síncronas (sem fila), Correção de Redação do ENEM (5 competências INEP), Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Escopo do Protótipo (+18 more)

### Community 4 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.09
Nodes (22): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, E4 Correção por IA — Nota estimada, feedback e nível de confiança, Ponto em aberto: correção por gabarito (RF-18) — resolvido, tornou-se obrigatório no MVP, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria (+14 more)

### Community 5 - "extract_text_from_image"
Cohesion: 0.29
Nodes (7): extract_text_from_image(), ler_imagem(), post, Session, UploadFile, OCRResponse, BaseModel

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.13
Nodes (16): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), Ponto em aberto: segunda matéria do MVP restrita às matérias do segundo dia do ENEM, RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP) (+8 more)

### Community 7 - "Relatório: teste de calibração da correção (14/10/2026)"
Cohesion: 0.06
Nodes (38): Calibração com 30–50 redações de nota conhecida (erro médio e viés por competência), Decisão em aberto: prompt × RAG × fine-tuning (conversar com o Igor), Correção por IA: calibração e decisão RAG/fine-tuning (13/10/2026), Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir), Opção 1: prompt com exemplos corrigidos (few-shot), Opção 3: fine-tuning com pares nota_ia × nota_professor, Laboratório /laboratorio/ (foto → texto → nota), Opção 2: RAG com redações corrigidas parecidas (+30 more)

### Community 9 - "E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios"
Cohesion: 0.17
Nodes (13): E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios, RF-28 (Recomendação): Indicar ao aluno os temas prioritários de estudo com base nas lacunas, RF-29 (Recomendação): Sugerir exercícios direcionados a cada lacuna, a partir de um banco etiquetado por tema e habilidade, RF-30 (Recomendação): Gerar exercícios novos com IA para a turma, sujeitos à aprovação do professor antes de circular, RF-46 (Recomendação): Aluno gera exercício de prática individual sob demanda, ancorado na base aprovada da matéria, sem aprovação prévia do professor, RF-47 (Recomendação): Gerar material de estudo (resumo ou mapa mental) a partir do conteúdo da matéria, para download, RN-13 (Recomendação): Exercícios gerados por IA para a turma só chegam ao aluno depois de aprovados por um professor; exercícios gerados sob demanda pelo próprio aluno seguem a RN-28, RN-28 (Recomendação): O aluno pode gerar exercício de prática individual sem aprovação prévia do professor, desde que ancorado na base aprovada da matéria; o exercício é identificado como gerado por IA, sem revisão (+5 more)

### Community 10 - "Diagnóstico de Domínio"
Cohesion: 0.20
Nodes (10): E6 Diagnóstico de domínio — Estimar o domínio por tema e mostrar a evolução, RF-24 (Domínio): Cada correção aprovada atualiza a estimativa de domínio do aluno nos temas e habilidades avaliados, RF-25 (Domínio): Exibir domínio em percentual por tema, com o número de evidências que o sustenta, RF-26 (Domínio): Histórico de evolução do domínio por tema ao longo do tempo, RF-27 (Domínio): Agregar domínio por turma e por escola, RN-08 (Domínio): O domínio por tema só aparece em percentual quando há um mínimo de evidências (número a definir); abaixo disso, "poucos dados", RN-09 (Domínio): Só correções aprovadas pelo professor entram no cálculo do domínio, US-20 (MVP): Como aluno, quero ver meu domínio por tema em percentual com o número de evidências, para não confiar em número com pouco dado (+2 more)

### Community 11 - "Tendências do ENEM"
Cohesion: 0.20
Nodes (10): E9 Tendências — Recorrência histórica de assuntos do ENEM, Ponto em aberto: conferir licença e formato dos dados públicos do ENEM e de outros vestibulares, RF-31 (Recomendação): Cruzar a lacuna do aluno com a recorrência do tema em provas passadas para priorizar, RF-36 (Tendências): Ingerir provas públicas do ENEM e de outros vestibulares (UFG, UFU, FUVEST, UEG) e classificar as questões por assunto e gênero textual, RF-37 (Tendências): Calcular o índice de recorrência (frequência, nº de provas, recência, consistência) e classificar em 4 categorias, RF-38 (Tendências): Exibir por assunto o nível de atenção, as evidências históricas e o grau de confiança, nunca como probabilidade de cair, RF-39 (Tendências): Indicar alta ou queda de frequência só com amostra suficiente; senão, avisar que não há tendência confiável, US-30 (Piloto): Como estudante, quero ver os assuntos do ENEM classificados por recorrência histórica, para priorizar meu tempo (+2 more)

### Community 12 - "Escola"
Cohesion: 0.18
Nodes (14): Atividade, AuditLog, CustoUso, DocumentoBase, Escola, Materia, Ponto em aberto: particionamento de AuditLog e CustoUso, Tema (+6 more)

### Community 14 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (6): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos, Risco: capacidade de execução (equipe de quatro, ainda validando divisão de papéis), Risco: dependência de poucos pilotos

### Community 15 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 16 - "Modelo de Cobrança"
Cohesion: 0.67
Nodes (3): Ponto em aberto: definição de "aluno ativo" para cobrança, Ponto em aberto: preço (rascunho R$1.000 fixos + R$8/aluno, sem validação), RN-24 (Comercial): Cobrança proposta: mensalidade fixa por escola mais valor por aluno ativo por mês. Rascunho: R$ 1.000 fixos + R$ 8 por aluno; ainda não validado

### Community 18 - "Custo Variável de IA/OCR"
Cohesion: 0.67
Nodes (3): Risco: custo variável de LLM e OCR por correção acima do previsto, RN-26 (Comercial): O valor por aluno deve superar o custo variável de IA e OCR por aluno; o preço só fecha depois de medir o custo real, RNF-17 (Custo): Custo variável por correção monitorado e abaixo do valor cobrado por aluno

### Community 58 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 59 - "routers/compliance.py"
Cohesion: 0.20
Nodes (18): Session, registrar_uso(), ConsentimentoLGPD, CustoUso, custo_uso_do_mes(), listar_auditoria(), meu_consentimento(), get (+10 more)

### Community 64 - "test_estudos.py"
Cohesion: 0.12
Nodes (28): hash_password(), _claude_falso(), Plano de estudo: GET /estudos/meu gera exercicios a partir do dominio real do…, test_gera_exercicios_para_as_piores_competencias_e_usa_cache(), gerar_contado(), test_professor_nao_usa_a_rota(), test_sem_chave_do_claude_responde_503(), test_sem_correcao_aprovada_responde_409() (+20 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.05
Nodes (35): Publicar o Domina na Vercel, Verificação no celular, 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual (+27 more)

### Community 69 - "variantes.py"
Cohesion: 0.06
Nodes (40): pearson(), ranks(), score(), Mede a correcao da IA contra notas conhecidas, via Groq (gratis). Nao altera o…, Mede a correcao da IA contra notas conhecidas (so texto, sem OCR). Nao altera o…, CompetenciaV3, para_v2(), pegar() (+32 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (13): Banco compartilhado + escola_id + RLS (estratégia escolhida), Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados (+5 more)

### Community 71 - "package.json"
Cohesion: 0.04
Nodes (45): dependencies, @fontsource/bricolage-grotesque, @fontsource/ibm-plex-mono, @fontsource/ibm-plex-sans, lucide-react, react, react-dom, react-native-web (+37 more)

### Community 72 - "main.py"
Cohesion: 0.15
Nodes (9): erro_nao_tratado(), Exception, health_check(), get, exception_handler, fastapi_middleware_cors, fastapi_staticfiles, JSONResponse (+1 more)

### Community 73 - "api.ts"
Cohesion: 0.12
Nodes (28): AdicionarMembro(), AlunoRow(), Classes(), Materials(), TIPOS_DOCUMENTO, TurmaCard(), CaixaAPI, ConsentimentoAPI (+20 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "routers/auth.py"
Cohesion: 0.27
Nodes (10): create_access_token(), verify_password(), login(), post, Session, LoginRequest, BaseModel, TokenResponse (+2 more)

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 78 - "test_fluxo_envio.py"
Cohesion: 0.07
Nodes (43): CaixaIA, CompetenciaIA, corrigir(), corrigir(), BaseModel, field_validator, QuestaoCorrigida, Correcao de exercicios de materias exatas (matematica, fisica, quimica) pelo… (+35 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (13): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+5 more)

### Community 80 - "routers/dominio.py"
Cohesion: 0.33
Nodes (10): _compartilha_turma(), _dominio_de(), dominio_do_aluno(), meu_dominio(), get, Session, UUID, meus_exercicios() (+2 more)

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 82 - "Dashboard.tsx"
Cohesion: 0.18
Nodes (19): EvolutionChart(), Card(), Progress(), SectionTitle(), initialActivities, initialState, studyTasks, topics (+11 more)

### Community 83 - "Learning.tsx"
Cohesion: 0.14
Nodes (17): RealSparkline(), Dashboard(), doBackend(), doDemo(), Evolution(), ExercicioComum, HABILIDADE_NOME, Studies() (+9 more)

### Community 84 - "App.tsx"
Cohesion: 0.10
Nodes (28): App(), iniciais(), navItems, InstallBanner(), Badge(), Button(), Empty(), IconButton() (+20 more)

### Community 85 - "Correcao"
Cohesion: 0.43
Nodes (7): Correcao, CorrecaoCriterio, Submissao, Arquitetura: Correção por IA (rubrica + LLM: nota e confiança), Arquitetura: Envio (texto, foto ou PDF de aluno/professor), Arquitetura: OCR (lê o manuscrito, usuário confere), Arquitetura: Professor revisa (aprova, edita ou rejeita cada nota)

### Community 86 - "atividades.ts"
Cohesion: 0.29
Nodes (11): Activities(), listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData(), paraStatus() (+3 more)

### Community 89 - "Histórico das versões do prompt de correção (v1 a v21)"
Cohesion: 0.15
Nodes (12): 1. Como ler os números, 2. Tabela resumo, 3. Versão por versão, 4. O que aprendemos, 5. Conclusão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10) (+4 more)

### Community 90 - "pydantic"
Cohesion: 0.18
Nodes (15): Anthropic, ExercicioGerado, gerar_exercicios(), BaseModel, Geracao de exercicios de pratica (plano de estudo) pelo Claude Haiku, a partir…, _RespostaIA, _client(), gerar_json() (+7 more)

### Community 91 - "Settings.tsx"
Cohesion: 0.25
Nodes (10): Consentimento(), CustoEAuditoria(), Help(), Settings(), auditLog(), AuditLogAPI, custoUso(), CustoUsoAPI (+2 more)

### Community 92 - "routers/usuario.py"
Cohesion: 0.53
Nodes (4): CriarUsuarioRequest, BaseModel, UsuarioResponse, typing

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (8): Ponto em aberto: retenção de conteudo_bruto, LGPD (Lei Geral de Proteção de Dados), Ponto em aberto: RN-21 (dados não usados para treinar modelos de terceiros) mantida, pendente confirmação do usuário, Risco: dados de menores de idade (legal e reputacional), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

### Community 94 - "usePwa.ts"
Cohesion: 0.53
Nodes (4): InstallEvent, isStandalone(), usePwa(), wasDismissed()

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

### Community 100 - "routers/turma.py"
Cohesion: 0.62
Nodes (5): CriarTurmaRequest, MatricularRequest, MembroTurmaResponse, BaseModel, TurmaResponse

### Community 101 - "routers/ocr.py"
Cohesion: 0.21
Nodes (14): get_current_user(), Session, decode_access_token(), Settings, get_db(), EvolucaoMateriaResponse, EvolucaoPontoResponse, BaseModel (+6 more)

### Community 109 - "DominioAluno"
Cohesion: 0.67
Nodes (4): DominioAluno, Arquitetura: Motor de domínio (% por tema; só com correção aprovada), Arquitetura: Painéis (aluno, professor e gestor), Arquitetura: Recomendação (temas a estudar e exercícios)

## Knowledge Gaps
- **253 isolated node(s):** `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script`, `roda_v12.sh script`, `roda_v9.sh script` (+248 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 396 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **59 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prompt de correção v2 (descritores oficiais do INEP por nível)` connect `test_fluxo_envio.py` to `E4 Correção por IA — Nota estimada, feedback e nível de confiança`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `Domina (plataforma de IA de correção e diagnóstico)` connect `Domina (plataforma de IA de correção e diagnóstico)` to `E4 Correção por IA — Nota estimada, feedback e nível de confiança`, `E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria`, `Relatório: teste de calibração da correção (14/10/2026)`, `Banco compartilhado + escola_id + RLS (estratégia escolhida)`, `E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios`, `Diagnóstico de Domínio`, `Tendências do ENEM`, `E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor`, `E10 Privacidade e operação — LGPD, auditoria e custo`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `E4 Correção por IA — Nota estimada, feedback e nível de confiança` connect `E4 Correção por IA — Nota estimada, feedback e nível de confiança` to `Domina (plataforma de IA de correção e diagnóstico)`, `test_fluxo_envio.py`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `Usuario` (e.g. with `get_current_user()` and `PerfilEnum`) actually correct?**
  _`Usuario` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `PerfilEnum` (e.g. with `Usuario` and `registrar_consentimento()`) actually correct?**
  _`PerfilEnum` has 26 INFERRED edges - model-reasoned connections that need verification._
- **What connects `roda_dupla.sh script`, `roda_v10.sh script`, `roda_v11.sh script` to the rest of the system?**
  _253 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Domina (plataforma de IA de correção e diagnóstico)` be split into smaller, more focused modules?**
  _Cohesion score 0.10507246376811594 - nodes in this community are weakly interconnected._