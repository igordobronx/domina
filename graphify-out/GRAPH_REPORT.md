# Graph Report - domina  (2026-09-30)

## Corpus Check
- Corpus is ~0 words - fits in a single context window. You may not need a graph.

## Summary
- 224 nodes · 230 edges · 44 communities (18 shown, 26 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.85)
- Token cost: 122,933 input · 0 output

## Community Hubs (Navigation)
- Modelo de Dados (Entidades)
- Time e Parceiros
- Base da Matéria e Redação ENEM
- Revisão Humana da Correção
- Contas, Escolas e Multi-tenancy
- Recomendação de Exercícios
- LGPD, Auditoria e Custo
- Envio e OCR
- Correção por IA
- Diagnóstico de Domínio
- Tendências do ENEM
- Painéis e Gamificação
- Privacidade de Dados de Menores
- Fases e Riscos do Projeto
- Ciclo do Produto
- Modelo de Cobrança
- Escolha de LLM Comercial
- Custo Variável de IA/OCR
- Cautela sobre Estimativas
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

## God Nodes (most connected - your core abstractions)
1. `Domina (plataforma de IA de correção e diagnóstico)` - 30 edges
2. `Usuario` - 14 edges
3. `E4 Correção por IA — Nota estimada, feedback e nível de confiança` - 8 edges
4. `Tema` - 6 edges
5. `Submissao` - 6 edges
6. `Correcao` - 6 edges
7. `E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria` - 6 edges
8. `E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios` - 6 edges
9. `Escola` - 5 edges
10. `Materia` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Tema` --references--> `Matriz de referência do INEP (habilidades/competências)`  [EXTRACTED]
  docs/Domina - Modelagem do Banco de Dados.pdf → docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf
- `Arquitetura: Envio (texto, foto ou PDF de aluno/professor)` --shares_data_with--> `Submissao`  [INFERRED]
  docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf → docs/Domina - Modelagem do Banco de Dados.pdf
- `Ponto em aberto: precisão numeric/decimal das notas` --semantically_similar_to--> `RNF-04 (Qualidade da IA): Concordância entre nota da IA e do corretor humano (meta a definir com especialista)`  [INFERRED] [semantically similar]
  docs/Domina - Modelagem do Banco de Dados.pdf → docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf
- `Perfil: Administrador Domina` --shares_data_with--> `Usuario`  [EXTRACTED]
  docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf → docs/Domina - Modelagem do Banco de Dados.pdf
- `Perfil: Aluno` --shares_data_with--> `Usuario`  [EXTRACTED]
  docs/Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1) (2).pdf → docs/Domina - Modelagem do Banco de Dados.pdf

## Hyperedges (group relationships)
- **Ciclo central do produto Domina (corrigir-diagnosticar-recomendar-evoluir)** — docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_produto_domina, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_corrigir, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_diagnosticar, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_recomendar, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_ciclo_mostrar_evolucao [EXTRACTED 1.00]
- **Pipeline de arquitetura de alto nível do Domina (9 componentes + base comum)** — docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_material_base, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_base_da_materia, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_envio, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_ocr, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_correcao_por_ia, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_professor_revisa, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_paineis, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_recomendacao, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_arch_motor_de_dominio [EXTRACTED 1.00]
- **Conformidade LGPD e privacidade de dados de menores no Domina** — docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_19, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_20, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_21, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rn_22, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rnf_10, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_rnf_11, docs_domina_visao_ers_backlog_e_regras_de_negocio_v0_1_2_risco_dados_menores [INFERRED 0.85]

## Communities (44 total, 26 thin omitted)

### Community 0 - "Modelo de Dados (Entidades)"
Cohesion: 0.09
Nodes (34): Atividade, AuditLog, Correcao, CorrecaoCriterio, CustoUso, DocumentoBase, DominioAluno, Escola (+26 more)

### Community 1 - "Time e Parceiros"
Cohesion: 0.13
Nodes (17): AKCIT / CEIA-UFG / Hub Goiás (possível fonte de fomento, mentoria e infraestrutura), COPE (piloto institucional desejado), Escola do Professor Beto (candidata a piloto adicional, foco em redação), Eu En Wong (ren., contato mantido por e-mail e LinkedIn), Gustavo (Co-fundador; desenvolvimento backend), Igor Ferreira Magalhães Silva (Fundador; backend, infraestrutura, DevOps e segurança), IPE (piloto institucional desejado), João Pedro (Co-fundador; estatística, matemática e IA; ponte de entrada no CEIA via UFG) (+9 more)

### Community 2 - "Base da Matéria e Redação ENEM"
Cohesion: 0.13
Nodes (16): ENEM (Exame Nacional do Ensino Médio) — mercado inicial, E2 Base da matéria — Ensinar ao sistema o conteúdo e os critérios de cada matéria, Matriz de referência do INEP (habilidades/competências), Ponto em aberto: segunda matéria do MVP restrita às matérias do segundo dia do ENEM, RF-05 (Matéria e base): Criar uma matéria e enviar documentos-base (apostila, rubrica, plano de aula, gabarito), RF-06 (Matéria e base): Extrair dos documentos os temas, habilidades e critérios de correção, RF-07 (Matéria e base): Professor edita, aprova ou rejeita a taxonomia e os critérios antes do uso, RF-08 (Matéria e base): Trazer pré-carregadas a matriz de referência do ENEM e as 5 competências da redação (INEP) (+8 more)

### Community 3 - "Revisão Humana da Correção"
Cohesion: 0.14
Nodes (15): E5 Revisão do professor — Garantir que a decisão final é humana e medir a IA, RF-17 (Correção): Registrar nível de confiança em cada correção e sinalizar quando a IA está incerta, RF-20 (Revisão): Nenhuma correção é liberada ao aluno sem aprovação do professor, RF-21 (Revisão): Professor edita nota e feedback e aceita ou rejeita a sugestão por critério, RF-22 (Revisão): Guardar a nota da IA e a nota final do professor, para medir concordância, RF-23 (Revisão): Fila de revisão que mostra primeiro as correções de menor confiança, Risco: correção de IA errada ou inconsistente, RN-01 (Revisão humana): Nenhuma nota ou feedback gerado pela IA é exibido ao aluno sem aprovação do professor responsável (+7 more)

### Community 4 - "Contas, Escolas e Multi-tenancy"
Cohesion: 0.15
Nodes (13): Banco compartilhado + escola_id + RLS (estratégia escolhida), Bancos separados por escola (estratégia alternativa), Domina — Modelagem e Projeto do Banco de Dados (v0.1), Schemas separados por escola (estratégia alternativa), Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1), E1 Contas, escolas e turmas — Acesso seguro por escola, com perfis, RF-01 (Conta e acesso): Cadastro e login de professores, alunos e gestores por convite da escola, RF-02 (Conta e acesso): Controle de acesso por perfil e por escola; cada escola só vê os próprios dados (+5 more)

### Community 5 - "Recomendação de Exercícios"
Cohesion: 0.17
Nodes (13): E7 Recomendação e exercícios — Dizer o que estudar e oferecer exercícios, RF-28 (Recomendação): Indicar ao aluno os temas prioritários de estudo com base nas lacunas, RF-29 (Recomendação): Sugerir exercícios direcionados a cada lacuna, a partir de um banco etiquetado por tema e habilidade, RF-30 (Recomendação): Gerar exercícios novos com IA para a turma, sujeitos à aprovação do professor antes de circular, RF-46 (Recomendação): Aluno gera exercício de prática individual sob demanda, ancorado na base aprovada da matéria, sem aprovação prévia do professor, RF-47 (Recomendação): Gerar material de estudo (resumo ou mapa mental) a partir do conteúdo da matéria, para download, RN-13 (Recomendação): Exercícios gerados por IA para a turma só chegam ao aluno depois de aprovados por um professor; exercícios gerados sob demanda pelo próprio aluno seguem a RN-28, RN-28 (Recomendação): O aluno pode gerar exercício de prática individual sem aprovação prévia do professor, desde que ancorado na base aprovada da matéria; o exercício é identificado como gerado por IA, sem revisão (+5 more)

### Community 6 - "LGPD, Auditoria e Custo"
Cohesion: 0.18
Nodes (11): ConsentimentoLGPD, E10 Privacidade e operação — LGPD, auditoria e custo, RF-40 (Privacidade): Registrar o consentimento dos responsáveis para alunos menores de 18 anos antes do primeiro envio, RF-41 (Privacidade): Exportar e excluir os dados de um aluno mediante solicitação, RF-42 (Operação): Registro de auditoria: quem acessou, corrigiu, aprovou ou alterou, RF-43 (Operação): Monitorar o custo por correção (tokens e OCR) por escola, RN-22 (Privacidade): Pedidos de exportação ou exclusão de dados são atendidos no prazo da política de privacidade (prazo a definir com base na LGPD), US-33 (MVP): Como responsável por um aluno menor, quero dar meu consentimento antes do primeiro envio, para autorizar o uso dos dados (+3 more)

### Community 7 - "Envio e OCR"
Cohesion: 0.18
Nodes (11): E3 Envio e OCR — Receber a produção do aluno, digitada ou manuscrita, RF-10 (Envio): Enviar produção por texto digitado ou por arquivo (PDF ou imagem), RF-11 (Envio): Extrair texto manuscrito por OCR e mostrar o texto extraído para conferência, RF-12 (Envio): Envio em lote pelo professor (várias produções de uma turma), RF-13 (Envio): Associar cada envio a aluno, turma, matéria, atividade e data, RF-45 (Correção): Corrigir resposta com elemento visual (diagrama, estrutura química, gráfico) analisando a imagem diretamente, RN-07 (Correção): Texto extraído por OCR deve ser confirmado antes de a correção começar; respostas com elemento visual são avaliadas pela imagem, não só pelo texto extraído, US-07 (MVP): Como aluno, quero enviar minha redação digitada ou por foto, para receber correção (+3 more)

### Community 8 - "Correção por IA"
Cohesion: 0.18
Nodes (11): E4 Correção por IA — Nota estimada, feedback e nível de confiança, Ponto em aberto: correção por gabarito (RF-18) — resolvido, tornou-se obrigatório no MVP, RF-15 (Correção): Corrigir questão ou prova discursiva de qualquer matéria segundo a rubrica da base da matéria, RF-16 (Correção): Gerar feedback textual por critério, apontando trechos do texto do aluno, RF-18 (Correção): Corrigir questões objetivas por comparação com gabarito, RF-19 (Correção): Registrar modelo, versão de prompt e base usados em cada correção, US-10 (MVP): Como professor, quero a nota estimada da redação ENEM por competência e total, com justificativa, para revisar mais rápido, US-11 (MVP): Como professor, quero corrigir prova discursiva de qualquer matéria pela minha rubrica, para ter o mesmo apoio fora do ENEM (+3 more)

### Community 9 - "Diagnóstico de Domínio"
Cohesion: 0.20
Nodes (10): E6 Diagnóstico de domínio — Estimar o domínio por tema e mostrar a evolução, RF-24 (Domínio): Cada correção aprovada atualiza a estimativa de domínio do aluno nos temas e habilidades avaliados, RF-25 (Domínio): Exibir domínio em percentual por tema, com o número de evidências que o sustenta, RF-26 (Domínio): Histórico de evolução do domínio por tema ao longo do tempo, RF-27 (Domínio): Agregar domínio por turma e por escola, RN-08 (Domínio): O domínio por tema só aparece em percentual quando há um mínimo de evidências (número a definir); abaixo disso, "poucos dados", RN-09 (Domínio): Só correções aprovadas pelo professor entram no cálculo do domínio, US-20 (MVP): Como aluno, quero ver meu domínio por tema em percentual com o número de evidências, para não confiar em número com pouco dado (+2 more)

### Community 10 - "Tendências do ENEM"
Cohesion: 0.20
Nodes (10): E9 Tendências — Recorrência histórica de assuntos do ENEM, Ponto em aberto: conferir licença e formato dos dados públicos do ENEM e de outros vestibulares, RF-31 (Recomendação): Cruzar a lacuna do aluno com a recorrência do tema em provas passadas para priorizar, RF-36 (Tendências): Ingerir provas públicas do ENEM e de outros vestibulares (UFG, UFU, FUVEST, UEG) e classificar as questões por assunto e gênero textual, RF-37 (Tendências): Calcular o índice de recorrência (frequência, nº de provas, recência, consistência) e classificar em 4 categorias, RF-38 (Tendências): Exibir por assunto o nível de atenção, as evidências históricas e o grau de confiança, nunca como probabilidade de cair, RF-39 (Tendências): Indicar alta ou queda de frequência só com amostra suficiente; senão, avisar que não há tendência confiável, US-30 (Piloto): Como estudante, quero ver os assuntos do ENEM classificados por recorrência histórica, para priorizar meu tempo (+2 more)

### Community 11 - "Painéis e Gamificação"
Cohesion: 0.22
Nodes (9): E8 Painéis e gamificação — Tornar o progresso visível para aluno, professor e gestor, RF-32 (Painéis): Painel do aluno: percentual de domínio por tema, barras de progresso e evolução, RF-33 (Painéis): Gamificação (metas, sequência de estudo, níveis), sem ranking público que exponha alunos, RF-34 (Painéis): Painel do professor: turma, lacunas coletivas e correções pendentes, RF-35 (Painéis): Painel do gestor: visão por turma e por professor, US-26 (MVP): Como aluno, quero um painel com percentual por tema e barras de progresso, para acompanhar minha evolução como em um jogo, US-27 (Piloto): Como aluno, quero metas e sequência de estudo, para manter o hábito, US-28 (MVP): Como professor, quero um painel com correções pendentes e lacunas coletivas, para organizar meu trabalho (+1 more)

### Community 12 - "Privacidade de Dados de Menores"
Cohesion: 0.32
Nodes (8): Ponto em aberto: retenção de conteudo_bruto, LGPD (Lei Geral de Proteção de Dados), Ponto em aberto: RN-21 (dados não usados para treinar modelos de terceiros) mantida, pendente confirmação do usuário, Risco: dados de menores de idade (legal e reputacional), RN-19 (Privacidade): Aluno menor de 18 anos só usa o sistema com consentimento dos responsáveis registrado, RN-21 (Privacidade): Dados de alunos não são usados para treinar modelos de terceiros nem compartilhados fora da finalidade do serviço, RNF-10 (Privacidade): Material de alunos não usado para treinar modelos de terceiros, RNF-11 (Privacidade): Minimização de dados e prazo de retenção definido; anonimização em conjuntos de validação

### Community 13 - "Fases e Riscos do Projeto"
Cohesion: 0.33
Nodes (6): Fase 4: Expansão (painel de turma, novas matérias, tendências), Fase 2: MVP técnico (redação ENEM + uma matéria), Fase 3: Piloto institucional (comparar IA com corretor humano), Fase 1: Prova de conceito com alunos conhecidos, Risco: capacidade de execução (equipe de quatro, ainda validando divisão de papéis), Risco: dependência de poucos pilotos

### Community 14 - "Ciclo do Produto"
Cohesion: 0.50
Nodes (4): Ciclo do produto: Corrigir, Ciclo do produto: Diagnosticar, Ciclo do produto: Mostrar a evolução, Ciclo do produto: Recomendar

### Community 15 - "Modelo de Cobrança"
Cohesion: 0.67
Nodes (3): Ponto em aberto: definição de "aluno ativo" para cobrança, Ponto em aberto: preço (rascunho R$1.000 fixos + R$8/aluno, sem validação), RN-24 (Comercial): Cobrança proposta: mensalidade fixa por escola mais valor por aluno ativo por mês. Rascunho: R$ 1.000 fixos + R$ 8 por aluno; ainda não validado

### Community 16 - "Escolha de LLM Comercial"
Cohesion: 0.67
Nodes (3): Ponto em aberto: LLM própria — resolvido (não treinar modelo do zero), RN-27 (IA / Infraestrutura): O Domina usa API comercial de LLM para correção e geração de conteúdo, em vez de treinar um modelo próprio do zero; modelos são comparados por custo, qualidade e confiabilidade em benchmark interno, RNF-18 (Manutenibilidade): Provedores de LLM e de OCR acessados por camada de abstração, para trocar sem reescrever o sistema

### Community 17 - "Custo Variável de IA/OCR"
Cohesion: 0.67
Nodes (3): Risco: custo variável de LLM e OCR por correção acima do previsto, RN-26 (Comercial): O valor por aluno deve superar o custo variável de IA e OCR por aluno; o preço só fecha depois de medir o custo real, RNF-17 (Custo): Custo variável por correção monitorado e abaixo do valor cobrado por aluno

## Knowledge Gaps
- **74 isolated node(s):** `Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1)`, `Schemas separados por escola (estratégia alternativa)`, `Bancos separados por escola (estratégia alternativa)`, `Ciclo do produto: Corrigir`, `Ciclo do produto: Mostrar a evolução` (+69 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 92 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Domina (plataforma de IA de correção e diagnóstico)` connect `Time e Parceiros` to `Modelo de Dados (Entidades)`, `Base da Matéria e Redação ENEM`, `Revisão Humana da Correção`, `Contas, Escolas e Multi-tenancy`, `Recomendação de Exercícios`, `LGPD, Auditoria e Custo`, `Envio e OCR`, `Correção por IA`, `Diagnóstico de Domínio`, `Tendências do ENEM`, `Painéis e Gamificação`?**
  _High betweenness centrality (0.524) - this node is a cross-community bridge._
- **Why does `Usuario` connect `Modelo de Dados (Entidades)` to `LGPD, Auditoria e Custo`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `E4 Correção por IA — Nota estimada, feedback e nível de confiança` connect `Correção por IA` to `Time e Parceiros`, `Revisão Humana da Correção`, `Envio e OCR`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Submissao` (e.g. with `Arquitetura: Envio (texto, foto ou PDF de aluno/professor)` and `Arquitetura: OCR (lê o manuscrito, usuário confere)`) actually correct?**
  _`Submissao` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Domina — Visão, ERS, Backlog e Regras de Negócio (v0.1)`, `Schemas separados por escola (estratégia alternativa)`, `Bancos separados por escola (estratégia alternativa)` to the rest of the system?**
  _74 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Modelo de Dados (Entidades)` be split into smaller, more focused modules?**
  _Cohesion score 0.09269162210338681 - nodes in this community are weakly interconnected._
- **Should `Time e Parceiros` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._