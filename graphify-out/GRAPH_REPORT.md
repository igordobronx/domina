# Graph Report - domina  (2026-10-24)

## Corpus Check
- 114 files · ~116,352 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 51 file(s) not represented in the graph (top: .jsonl 37, (none) 5, .xlsm 3)

## Summary
- 1137 nodes · 2654 edges · 102 communities (51 shown, 51 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 314 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `352540e8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Domina (plataforma de IA de correção e diagnóstico)
- Activities.tsx
- submissoes.py
- Escopo do Protótipo
- E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita
- routers/evolucao.py
- E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria
- Relatório: teste de calibração da correção (14/10/2026)
- api
- E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios
- Diagnóstico de Domínio
- Tendências do ENEM
- Usuario
- ui.tsx
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- routers/ocr.py
- Custo Variável de IA/OCR
- Dependência: Hash de Senha
- Dependência: Pydantic
- Cautela sobre Estimativas
- E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA
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
- routers/compliance.py
- E4 Correção por IA — Nota estimada, feedback e nível de confiança
- database.py
- RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta
- Laboratório /laboratorio/ (foto → texto → nota)
- test_estudos.py
- Documentação do frontend Domina
- variantes.py
- Banco compartilhado + escola_id + RLS (estratégia escolhida)
- package.json
- main.py
- api.ts
- compilerOptions
- routers/auth.py
- E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor
- test_fluxo_envio.py
- E10 Privacidade e operação — LGPD, auditoria e custo
- routers/dominio.py
- vercel.json
- Learning.tsx
- App.tsx
- Correcao
- atividades.ts
- vite-env.d.ts
- Histórico das versões do prompt de correção (v1 a v21)
- app/estudos.py
- Settings.tsx
- models/usuario.py
- LGPD (Lei Geral de Proteção de Dados)
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- CLAUDE.md: domina, correção de redação do ENEM por IA
- erro_nao_tratado
- routers/usuario.py
- Teste do v21 (nota do meio)
- roda_dupla.sh
- roda_v10.sh
- roda_v11.sh
- roda_v12.sh
- roda_v9.sh

## God Nodes (most connected - your core abstractions)
1. `Usuario` - 69 edges
2. `PerfilEnum` - 40 edges
3. `request()` - 35 edges
4. `Domina (plataforma de IA de correção e diagnóstico)` - 30 edges
5. `App()` - 28 edges
6. `Atividade` - 27 edges
7. `_ferramentas()` - 27 edges
8. `Card()` - 26 edges
9. `Button()` - 25 edges
10. `corrigir_submissao()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Laboratório /laboratorio/ (foto → texto → nota)` --references--> `corrigir()`  [EXTRACTED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → backend/app/correcao.py
- `Envio e aprovação` --references--> `approveActivity()`  [INFERRED]
  frontend/docs/FRONTEND.md → frontend/src/services/demoStore.ts
- `7. Persistência e contratos` --references--> `DemoState`  [INFERRED]
  frontend/docs/FRONTEND.md → frontend/src/types.ts
- `Prompt de correção v2 (descritores oficiais do INEP por nível)` --references--> `corrigir()`  [EXTRACTED]
  docs/decisoes/2026-10-13-correcao-ia-calibracao.md → backend/app/correcao.py
- `4. Identidade visual` --references--> `Logo()`  [INFERRED]
  frontend/docs/FRONTEND.md → frontend/src/components/ui.tsx

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

## Communities (102 total, 51 thin omitted)

### Community 0 - "Domina (plataforma de IA de correção e diagnóstico)"
Cohesion: 0.13
Nodes (12): AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend), Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança), IPE (piloto institucional desejado), João Pedro (Co-fundador; estatística, matemática e IA; ponte de entrada no CEIA via UFG) (+4 more)

### Community 1 - "Activities.tsx"
Cohesion: 0.09
Nodes (44): ActivityDetail(), compoeEnunciado(), destacarTrechos(), ImagemComCaixas(), MATERIAS_COM_GABARITO, NOMES_FERRAMENTAS, NOTAS_ENEM, PassoAPassoAgente() (+36 more)

### Community 2 - "submissoes.py"
Cohesion: 0.06
Nodes (95): ErroFerramenta, registrar(), registrar_uso(), gerar_exercicios(), PerfilEnum, StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum (+87 more)

### Community 3 - "Escopo do Protótipo"
Cohesion: 0.10
Nodes (15): Esqueleto do Backend (FastAPI) + Auth + Deploy Inicial, Diagnóstico de Domínio por Competência + Recomendação, Divisão por Pessoa (cronograma de 2 semanas), Documentação do AKCIT, Gustavo, Igor, João Pedro, Lucas (+7 more)

### Community 4 - "E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 5 - "routers/evolucao.py"
Cohesion: 0.36
Nodes (3): get_current_user(), EvolucaoMateriaResponse, EvolucaoPontoResponse

### Community 6 - "E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria"
Cohesion: 0.12
Nodes (16): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP), RF-09 (Matéria e base): Versionar a base de uma matéria, registrando quem mudou o quê e quando (+8 more)

### Community 7 - "Relatório: teste de calibração da correção (14/10/2026)"
Cohesion: 0.15
Nodes (10): Calibração com 30–50 redações de nota conhecida (erro médio e viés por competência), Decisão em aberto: prompt × RAG × fine-tuning (conversar com o Igor), Correção por IA: calibração e decisão RAG/fine-tuning (13/10/2026), Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir), Teste: redação ENEM 2023 do Igor (oficial 880; IA 600 → 680), Base de redações (essays/base_redacoes_enem_domina_ai.xlsm, 2.327 redações), Relatório: teste de calibração da correção (14/10/2026), Ferramenta de calibração (backend/calibracao) (+2 more)

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
Cohesion: 0.12
Nodes (22): Atividade, AuditLog, CustoUso, DocumentoBase, DominioAluno, Escola, Exercicio, ExercicioResposta (+14 more)

### Community 13 - "ui.tsx"
Cohesion: 0.22
Nodes (4): Logo(), colors, fonts, react

### Community 14 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (4): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos

### Community 15 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 17 - "routers/ocr.py"
Cohesion: 0.29
Nodes (3): extract_text_from_image(), ler_imagem(), OCRResponse

### Community 23 - "E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA"
Cohesion: 0.22
Nodes (8): E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA, RF-21 (Revisão): Professor edita nota e feedback e aceita ou rejeita a sugestão por critério, RF-22 (Revisão): Guardar a nota da IA e a nota final do professor, para medir concordância, RN-02 (Revisão humana): A nota final é sempre a do professor; a nota da IA é uma sugestão e fica guardada para medir qualidade, RN-27 (IA / Infraestrutura): O Domina usa API comercial de LLM para correção e geração de conteúdo, em vez de treinar um modelo próprio do zero; modelos são comparados por custo, qualidade e confiabilidade em benchmark interno, RNF-18 (Manutenibilidade): Provedores de LLM e de OCR acessados por camada de abstração, para trocar sem reescrever o sistema, US-17 (MVP): Como professor, quero editar nota e feedback e aceitar ou rejeitar por critério, para ajustar a sugestão da IA, US-18 (MVP): Como administrador, quero comparar a nota da IA com a nota final do professor, para medir a qualidade

### Community 58 - "CLAUDE.md: domina, correção de redação do ENEM por IA"
Cohesion: 0.18
Nodes (10): 0. Estado em 20/10/2026 à noite (leia primeiro), 1. Objetivo do prompt, 2. Onde as coisas estão, 3. Bases de teste (planilhas em `essays/`), 4. Histórico: o que funcionou e o que falhou, 5. Próximos passos antigos (19/10; vale o que está na seção 0), 6. Prompt antigo (v9; o atual é o v14, ver seção 0), 7. Commit e push (usuário cola no terminal do Mac, na pasta do projeto) (+2 more)

### Community 59 - "routers/compliance.py"
Cohesion: 0.26
Nodes (10): ConsentimentoLGPD, custo_uso_do_mes(), listar_auditoria(), meu_consentimento(), registrar_consentimento(), _so_gestor(), AuditLogResponse, ConsentimentoRequest (+2 more)

### Community 60 - "E4 Correção por IA — Nota estimada, feedback e nível de confiança"
Cohesion: 0.20
Nodes (9): E4 Correção por IA — Nota estimada, feedback e nível de confiança, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção, US-11 (MVP): Como professor, quero corrigir prova discursiva de qualquer matéria pela minha rubrica, para ter o mesmo apoio fora do ENEM, US-13 (MVP): Como aluno, quero feedback que aponte trechos do meu texto, para entender exatamente o que melhorar, US-14 (MVP): Como professor, quero questões objetivas corrigidas por gabarito, para incluí-las no diagnóstico (+1 more)

### Community 62 - "RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta"
Cohesion: 0.33
Nodes (5): RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta, RF-23 (Revisão): Fila de revisão que mostra primeiro as correções de menor confiança, RN-06 (Correção): Quando a confiança da IA fica abaixo do limiar definido, a correção é marcada como "requer atenção" e sobe na fila de revisão, US-12 (MVP): Como professor, quero ver o nível de confiança e alertas de incerteza da IA, para focar minha revisão onde há mais risco, US-19 (Piloto): Como professor, quero uma fila de revisão que priorize as correções de baixa confiança, para revisar primeiro o que é mais preciso

### Community 63 - "Laboratório /laboratorio/ (foto → texto → nota)"
Cohesion: 0.40
Nodes (4): Laboratório /laboratorio/ (foto → texto → nota), RF-20 (Revisão): Nenhuma correção é liberada ao aluno sem aprovação do professor, RN-01 (Revisão humana): Nenhuma nota ou feedback gerado pela IA é exibido ao aluno sem aprovação do professor responsável, US-16 (MVP): Como professor, quero que nada chegue ao aluno sem minha aprovação, para manter a decisão final comigo

### Community 64 - "test_estudos.py"
Cohesion: 0.07
Nodes (30): hash_password(), _claude_falso(), test_gera_exercicios_para_as_piores_competencias_e_usa_cache(), gerar_contado(), test_professor_nao_usa_a_rota(), test_sem_chave_do_claude_responde_503(), test_sem_correcao_aprovada_responde_409(), token() (+22 more)

### Community 68 - "Documentação do frontend Domina"
Cohesion: 0.05
Nodes (39): Publicar o Domina na Vercel, Verificação no celular, 10. Responsividade, 11. Limitações e próximos incrementos, 1. Objetivo e decisões, 2. Linguagens, bibliotecas e ferramentas, 3. Organização de pastas, 4. Identidade visual (+31 more)

### Community 69 - "variantes.py"
Cohesion: 0.06
Nodes (17): Ferramenta, _resumo(), rodar(), pearson(), ranks(), score(), chamar(), _groq_key() (+9 more)

### Community 70 - "Banco compartilhado + escola_id + RLS (estratégia escolhida)"
Cohesion: 0.15
Nodes (12): Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados, RF-03 (Conta e acesso): Cadastro de turmas e vínculo de alunos e professores (+4 more)

### Community 71 - "package.json"
Cohesion: 0.05
Nodes (45): dependencies, @fontsource/bricolage-grotesque@^5.3.0, @fontsource/ibm-plex-mono@^5.3.0, @fontsource/ibm-plex-sans@^5.3.0, lucide-react@^1.52.0, react@^19.3.0, react-dom@^19.3.0, react-native-web@^0.21.3 (+37 more)

### Community 73 - "api.ts"
Cohesion: 0.17
Nodes (19): AdicionarMembro(), AlunoRow(), Classes(), Materials(), TIPOS_DOCUMENTO, TurmaCard(), criarTurma(), criarUsuario() (+11 more)

### Community 74 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, allowImportingTsExtensions, esModuleInterop, jsx, lib, module, moduleResolution, noEmit (+4 more)

### Community 75 - "routers/auth.py"
Cohesion: 0.23
Nodes (6): create_access_token(), decode_access_token(), verify_password(), login(), LoginRequest, TokenResponse

### Community 76 - "E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 78 - "test_fluxo_envio.py"
Cohesion: 0.05
Nodes (38): CaixaIA, CompetenciaIA, corrigir(), corrigir(), QuestaoCorrigida, ResultadoExatasIA, PontoIA, ResultadoIA (+30 more)

### Community 79 - "E10 Privacidade e operação — LGPD, auditoria e custo"
Cohesion: 0.17
Nodes (12): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+4 more)

### Community 80 - "routers/dominio.py"
Cohesion: 0.29
Nodes (6): consultar_historico(), _compartilha_turma(), _dominio_de(), dominio_do_aluno(), meu_dominio(), meus_exercicios()

### Community 81 - "vercel.json"
Cohesion: 0.29
Nodes (6): buildCommand, framework, headers, installCommand, outputDirectory, $schema

### Community 83 - "Learning.tsx"
Cohesion: 0.16
Nodes (32): EvolutionChart(), RealSparkline(), Badge(), Button(), Card(), Empty(), Progress(), topics (+24 more)

### Community 84 - "App.tsx"
Cohesion: 0.12
Nodes (29): App(), iniciais(), navItems, InstallBanner(), IconButton(), Modal(), initialActivities, initialState (+21 more)

### Community 85 - "Correcao"
Cohesion: 0.36
Nodes (8): Correcao, CorrecaoCriterio, Submissao, Arquitetura: Correção por IA (rubrica + LLM: nota e confiança), Arquitetura: Envio (texto, foto ou PDF de aluno/professor), Arquitetura: OCR (lê o manuscrito, usuário confere), Arquitetura: Professor revisa (aprova, edita ou rejeita cada nota), Correção de Redação do ENEM (5 competências INEP)

### Community 86 - "atividades.ts"
Cohesion: 0.32
Nodes (10): listarAtividades(), listarSubmissoesRevisao(), minhasSubmissoes(), MinhaSubmissaoAPI, carregarAtividadesDoAluno(), paraData(), paraStatus(), carregarRevisoes() (+2 more)

### Community 89 - "Histórico das versões do prompt de correção (v1 a v21)"
Cohesion: 0.15
Nodes (12): 1. Como ler os números, 2. Tabela resumo, 3. Versão por versão, 4. O que aprendemos, 5. Conclusão, Fase 1: primeiras versões (13 e 14/10), Fase 2: regras mais justas e a base externa (15 e 16/10), Fase 3: base INEP de 50 redações (18/10) (+4 more)

### Community 90 - "app/estudos.py"
Cohesion: 0.29
Nodes (4): ExercicioGerado, _RespostaIA, AgenteRequest, AgenteResponse

### Community 91 - "Settings.tsx"
Cohesion: 0.35
Nodes (10): SectionTitle(), Consentimento(), CustoEAuditoria(), Settings(), auditLog(), AuditLogAPI, custoUso(), CustoUsoAPI (+2 more)

### Community 92 - "models/usuario.py"
Cohesion: 0.27
Nodes (6): StatusProcessamentoEnum, TipoDocumentoEnum, DocumentoBase, enviar_documento(), listar_documentos(), DocumentoBaseResponse

### Community 93 - "LGPD (Lei Geral de Proteção de Dados)"
Cohesion: 0.32
Nodes (5): LGPD (Lei Geral de Proteção de Dados), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

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

### Community 101 - "routers/usuario.py"
Cohesion: 0.31
Nodes (6): criar_usuario(), listar_usuarios(), meu_usuario(), _resposta(), CriarUsuarioRequest, UsuarioResponse

## Knowledge Gaps
- **88 isolated node(s):** `Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir)`, `COPE (piloto institucional desejado)`, `Escola do Professor Beto (candidata a piloto adicional, foco em redação)`, `Gustavo (Co-fundador; desenvolvimento backend)`, `Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança)` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 388 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Prompt de correção v2 (descritores oficiais do INEP por nível)` connect `test_fluxo_envio.py` to `E4 Correção por IA — Nota estimada, feedback e nível de confiança`, `Relatório: teste de calibração da correção (14/10/2026)`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `Usuario` (e.g. with `get_current_user()` and `PerfilEnum`) actually correct?**
  _`Usuario` has 50 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Corpus Essay-BR (redações estilo ENEM com nota por competência; licença a conferir)`, `COPE (piloto institucional desejado)`, `Escola do Professor Beto (candidata a piloto adicional, foco em redação)` to the rest of the system?**
  _88 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Domina (plataforma de IA de correção e diagnóstico)` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._
- **Why does `E4 Correção por IA — Nota estimada, feedback e nível de confiança` connect `E4 Correção por IA — Nota estimada, feedback e nível de confiança` to `Domina (plataforma de IA de correção e diagnóstico)`, `E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita`, `E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria`, `test_fluxo_envio.py`, `RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `PerfilEnum` (e.g. with `Usuario` and `registrar_consentimento()`) actually correct?**
  _`PerfilEnum` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `Activities.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.09371980676328502 - nodes in this community are weakly interconnected._