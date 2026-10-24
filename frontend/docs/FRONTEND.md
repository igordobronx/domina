# Documentação do frontend Domina

Versão: 0.1.0 · Entrega de 6 de outubro de 2026.

## 1. Objetivo e decisões

O frontend apresenta o ciclo **enviar → revisar → aprovar → aprender**, com foco em clareza, autonomia do aluno e decisão final do professor. As referências são os documentos de visão/requisitos e banco de dados v0.1 e o PDF de identidade visual do Domina.

A primeira distribuição será pela web/PWA. A implementação usa componentes de React Native for Web em conjunto com recursos próprios do navegador. A opção por Vite permite gerar um pacote estático, sem servidor de aplicação. Não há implantação pública nesta entrega.

Não foram implementados backend, login real, OCR, correção por IA, consentimento jurídico, banco PostgreSQL, RLS ou integrações externas. A presença visual desses conceitos não comprova sua implementação no servidor. O catálogo de funcionalidades abaixo diferencia ações locais de dados ilustrativos.

## 2. Linguagens, bibliotecas e ferramentas

| Tecnologia                | Papel                                                          |
| ------------------------- | -------------------------------------------------------------- |
| TypeScript                | Tipos de atividades, estados, perfis e funções                 |
| TSX / React               | Componentes e composição da interface                          |
| React Native for Web      | Renderização de Pressable, Text, View e TextInput no navegador |
| HTML semântico            | Landmarks, formulários, diálogos, listas, navegação e detalhes |
| CSS                       | Grade responsiva, identidade visual, estados e animações       |
| SVG                       | Logo vetorial simplificado, indicador circular e gráfico       |
| Vite                      | Servidor de desenvolvimento e build                            |
| vite-plugin-pwa / Workbox | Manifest, service worker e pré-cache                           |
| Lucide React              | Ícones de interface                                            |
| Fontsource                | Fontes locais da identidade visual                             |
| Vitest                    | Regras de aprovação e navegação                                |
| Playwright                | Fluxos de navegador, responsividade e PWA                      |
| Prettier                  | Formatação consistente dos arquivos                            |

As versões efetivamente instaladas estão em `package-lock.json`. Para reproduzir, use `npm ci`, não remova o lockfile. React Native é utilizado como fonte de tipos via dependência de desenvolvimento de `@types/react-native-web`; o bundle web resolve os imports para `react-native-web`.

## 3. Organização de pastas

```text
Domina/
├── public/
│   ├── favicon.svg             # Símbolo vetorial da marca
│   └── icons/                  # PNGs reais de 192 e 512 px, incluindo maskable
├── src/
│   ├── App.tsx                 # Shell, perfil, navegação, busca, modais e PWA
│   ├── main.tsx                # Bootstrap e carregamento das fontes
│   ├── theme.ts                # Cores e famílias tipográficas para componentes RN
│   ├── styles.css              # Layout web, tokens e breakpoints
│   ├── types.ts                # Contratos da interface
│   ├── components/
│   │   ├── ui.tsx              # Botões, cartões, badges, modal, logo, progresso
│   │   ├── Chart.tsx           # Gráfico ilustrativo acessível
│   │   └── InstallBanner.tsx   # Convite de instalação
│   ├── data/demo.ts            # Massa de dados e exercícios demonstrativos
│   ├── hooks/usePwa.ts         # Instalação, standalone e conectividade
│   ├── services/
│   │   ├── demoStore.ts        # Persistência e regras locais de aprovação
│   │   ├── navigation.ts       # Leitura e validação das rotas
│   │   └── demoStore.test.ts   # Testes das regras essenciais
│   └── screens/
│       ├── Dashboard.tsx      # Início do aluno e linha reutilizável de atividade
│       ├── EducatorDashboard.tsx # Início de professor e gestor
│       ├── Activities.tsx     # Lista, envio, revisão e resultado
│       ├── Learning.tsx       # Evolução, plano e exercício
│       ├── Management.tsx     # Turmas e materiais
│       └── Settings.tsx       # Preferências e ajuda
├── tests/flows.spec.ts        # Testes de navegador
├── docs/                     # Documentação e roteiro de validação
├── vite.config.ts            # Alias RN Web, PWA e build
├── playwright.config.ts      # Chrome e URL do preview
├── vitest.config.ts          # Escopo dos testes unitários
├── tsconfig.json             # TypeScript em modo estrito
└── package.json / package-lock.json
```

`dist/` é gerado pelo build e não deve ser editado. `tmp/` guarda materiais e capturas locais de validação, ignorados no Git. Os arquivos já existentes em `assets/brand/` foram preservados; o PNG anterior não foi adotado como fonte da identidade nova.

## 4. Identidade visual

| Nome    | Valor     | Aplicação                             |
| ------- | --------- | ------------------------------------- |
| Tinta   | `#141A2E` | Texto, hero e avisos                  |
| Papel   | `#F5F3EC` | Fundo geral                           |
| Domínio | `#2E9E73` | Barras, símbolo e progresso           |
| Caneta  | `#E5A23A` | Referência de revisão e estados âmbar |
| Lacuna  | `#DCD8CC` | Bordas e base do progresso            |

Há tons auxiliares derivados, como verde escuro `#197451` em textos e botões e âmbar escuro `#80500E` sobre fundo claro, para melhorar legibilidade. O verde original permanece nos gráficos e no símbolo. Estado nunca depende apenas da cor: também recebe rótulo ou ícone.

**Bricolage Grotesque**: títulos e wordmark. **IBM Plex Sans**: textos e controles. **IBM Plex Mono**: notas, percentuais e pequenas etiquetas de dados. Fontes latinas empacotadas junto ao site, com acentos portugueses.

O símbolo foi reconstruído em SVG a partir do conceito do PDF: D com progresso verde e trecho restante, sempre incompleto. O wordmark é composição tipográfica, não um arquivo mestre oficial da marca. Se houver SVG oficial, substitua `Logo` e os ícones mantendo proporções e área de proteção.

Cartões usam cantos de 10–17 px, bordas leves e respiro. O conteúdo escuro é reservado a destaques. As animações se limitam a entrada de página, preenchimento de barras e estados de interação; respeitam `prefers-reduced-motion`.

## 5. Mapa de telas e funcionalidades

### Acesso demonstrativo

O site abre no painel do aluno. O seletor superior alterna Aluno, Professor e Gestor. O ícone junto ao perfil abre uma janela com as três opções e explicação de que não existe autenticação. Não são coletadas senhas, e-mail ou dados reais de menores.

### Aluno

| Tela               | Conteúdo                                                                                                                     | Ações                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Visão geral        | Saudação, domínio ilustrativo, práticas da semana, cartões de indicadores, mapa de temas, recomendação e atividades recentes | Enviar, praticar, abrir atividade, ver evolução, instalar PWA               |
| Minhas atividades  | Lista por matéria e status                                                                                                   | Busca, filtros Todas/Para fazer/Em revisão/Corrigidas e abertura do detalhe |
| Envio              | Enunciado, texto ou arquivo, contador, orientação e confirmação                                                              | Salvar rascunho automático, escolher arquivo, enviar ou continuar depois    |
| Aguardando revisão | Confirmação de recebimento e status                                                                                          | Voltar à lista; sem nota ou feedback de IA                                  |
| Resultado          | Nota final, competências/raciocínio, feedback e texto enviado                                                                | Leitura da avaliação aprovada                                               |
| Minha evolução     | Gráfico temporal e cartões de temas                                                                                          | Filtrar Redação ou Matemática                                               |
| Plano de estudo    | Três práticas dirigidas por lacuna                                                                                           | Iniciar ou repetir prática                                                  |
| Exercício          | Enunciado, alternativas e explicação                                                                                         | Selecionar, conferir e concluir                                             |

Notas de redação usam cinco competências, 0–200 em passos de 20, total de 0–1000. A atividade de matemática usa uma nota demonstrativa de raciocínio de 0–10; não reutiliza a escala da redação.

### Professor

| Tela                  | Conteúdo                                                   | Ações                                                   |
| --------------------- | ---------------------------------------------------------- | ------------------------------------------------------- |
| Visão geral           | Pendências, correções, panorama ilustrativo da turma       | Abrir revisão, materiais e turma                        |
| Revisões              | Atividades pendentes e aprovadas                           | Buscar, filtrar e abrir                                 |
| Revisar atividade     | Sugestão fixa de nota, texto do aluno e campos de feedback | Alterar notas, redigir orientação, confirmar publicação |
| Turmas                | Pré-ENEM A e indicadores locais                            | Expandir a lista da aluna demonstrativa                 |
| Materiais e critérios | Base inicial e documentos locais adicionados               | Registrar título, matéria e nome do arquivo             |

Um material novo fica “Aguardando integração”. Nenhuma extração, ingestão de conteúdo ou aprovação fictícia é anunciada como real. Somente a base demonstrativa inicial está marcada como aprovada.

### Gestor

Visão geral agregada e consulta da turma. Não há controles de aprovação de notas no menu do gestor. URLs de revisão com perfil gestor são normalizadas para o início. Isso é organização da interface, não segurança: no protótipo, qualquer visitante pode trocar de perfil.

### Compartilhadas

- **Busca**: páginas disponíveis ao perfil e atividades (para aluno/professor), com estado sem resultado.
- **Notificações**: orientações demonstrativas; não é uma caixa de notificações do servidor.
- **Preferências**: nome do aluno, meta semanal, exportação JSON e restauração com confirmação.
- **Ajuda**: perguntas frequentes sobre correção, fluxo de teste, domínio, rascunho, instalação e offline.
- **Instalação**: convite no início e instruções por plataforma.

## 6. Fluxos e estados

### Envio e aprovação

```text
disponivel
  → aluno preenche resposta e confirma
pendente
  → professor ajusta notas e escreve feedback
  → confirmação explícita de publicação
aprovada
  → aluno consulta nota e orientação
```

O resultado pendente não é renderizado na área do aluno. A sugestão original fica em `aiScores`; a nota final fica em `scores`, para não sobrescrever o dado que futuramente será usado na comparação de qualidade. `approveActivity` valida a escala e exige feedback antes de aprovar.

### Texto e arquivo

- Texto: pelo menos 40 caracteres, limiar apenas demonstrativo; não representa critério oficial do ENEM.
- Rascunhos: salvos por ID da atividade, sem misturar redação e matemática.
- Arquivo: PDF/JPG/PNG de até 10 MB, com validação local de extensão/tamanho.
- O conteúdo binário não é persistido, lido nem enviado. Guarda-se somente o nome. Após recarregar antes do envio, o arquivo precisa ser selecionado novamente.
- A conferência de OCR lado a lado ainda depende de integração; não foi simulada com um texto falsamente extraído.
- Materiais aceitam PDF/DOCX/TXT até 10 MB e igualmente salvam apenas metadados.

### Prática

Escolher alternativa → conferir → ver explicação → concluir → cartão marcado como concluído. A tentativa errada também é considerada prática realizada. Repetir uma prática não duplica a contagem. As conclusões não alteram o domínio porque o cálculo pedagógico ainda não está definido/integrado.

### Navegação

Rotas em fragmento: `#aluno/inicio`, `#aluno/atividades/a1`, `#professor/revisoes/a1`, `#gestor/turmas`. O fragmento permite links e recarga sem exigir configuração de rotas no servidor. Voltar/Avançar do navegador restaura perfil e tela. As páginas permitidas por perfil estão em `services/navigation.ts`.

## 7. Persistência e contratos

Chave `domina.demo.v1` no `localStorage`. Estado: atividades, materiais, IDs de práticas concluídas, nome do aluno, meta e rascunhos por atividade. Falha de leitura retorna os exemplos iniciais; falha de gravação exibe aviso e permite exportação. Não há sincronização entre aparelhos, cookies de sessão ou analytics.

`DemoState` é contrato local de UI, não DTO definitivo do backend. Para integração, substitua o armazenamento por serviços/API e adapte as respostas aos tipos de tela. Evite inserir chamadas de API dentro de componentes visuais reutilizáveis.

| Interface atual     | Integração futura                                              |
| ------------------- | -------------------------------------------------------------- |
| Troca de perfil     | Sessão, convite e autorização por escola/turma                 |
| Enviar atividade    | API de submissões + upload autorizado                          |
| `aiScores` fixos    | Fila de correção, versão de modelo/prompt, rubrica e confiança |
| Aprovar localmente  | Endpoint transacional de revisão + auditoria                   |
| Gráficos fixos      | Histórico de domínio e número de evidências                    |
| Exercícios fixos    | Banco de exercícios etiquetados e registro de respostas        |
| Materiais locais    | Upload, processamento, taxonomia e aprovação de base           |
| Exportar JSON local | Fluxo real de exportação/exclusão autorizado                   |

No servidor, verificar escola, turma, perfil e ownership em todas as operações. A API do aluno não deve devolver sugestões pendentes: esconder pelo frontend não impede acesso ao dado local. Consentimento e retenção precisam de desenho específico antes de uso com alunos reais.

## 8. PWA

O manifest é gerado por `vite-plugin-pwa`: nome Domina, idioma pt-BR, `display: standalone`, `start_url` e `scope` na raiz, cores da identidade e ícones PNG de dimensões reais. O ícone maskable possui margem interna própria. Há favicon SVG e ícone Apple.

O service worker usa pré-cache dos arquivos estáticos gerados e fallback para a interface. Não existe cache de API nem sincronização em segundo plano. A primeira visita precisa de conexão. Em offline, continuam disponíveis a interface previamente armazenada e os exemplos locais.

O registro ocorre apenas no build de produção. Quando uma versão nova está esperando, a interface apresenta “Atualizar agora”; o usuário escolhe quando recarregar.

### Instalação

1. Detectar abertura standalone via `matchMedia('(display-mode: standalone)')` ou `navigator.standalone` no iOS.
2. Ocultar o convite nesse modo e ao receber `appinstalled`.
3. No navegador, mostrar convite discreto somente no início, se não dispensado na sessão.
4. Armazenar o evento `beforeinstallprompt` quando disponível e chamar `prompt()` em ação do usuário.
5. Sem esse evento, abrir instruções para Safari/iOS, Chrome/Android e computador.

Não há API universal para saber que a PWA já está instalada quando a pessoa retorna pelo navegador. Portanto, a garantia é ocultar no modo instalado, após o evento de instalação na execução atual e após dispensa na sessão. Esse limite foi considerado desde o pedido inicial.

Para instalar fora do computador local, é necessário HTTPS. Abrir pelo IP da rede com HTTP pode permitir visualizar o site, mas não comprova a instalação/offline. Um teste real no Safari/iOS e em Android continua necessário antes de publicação.

Referências técnicas: [React Native for Web](https://necolas.github.io/react-native-web/docs/setup/), [evento de instalação](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeinstallprompt_event) e [modo standalone](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Create_a_standalone_app).

## 9. Usabilidade e acessibilidade

Aplicação das [10 heurísticas de Jakob Nielsen](https://www.nngroup.com/articles/ten-usability-heuristics/):

| Heurística                       | Decisão na interface                                                                                    |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Visibilidade do estado           | Status de atividade, rascunho, avisos de sucesso, offline e atualização                                 |
| Correspondência com o mundo real | Linguagem de aluno/professor: enviar, revisar, corrigida, próximo passo                                 |
| Controle e liberdade             | Voltar, cancelar publicação, continuar depois, fechar diálogos e dispensar instalação                   |
| Consistência                     | Botões, cores, ícones, status e navegação compartilhados                                                |
| Prevenção de erros               | Limites de arquivo, campos obrigatórios, notas em escala válida e confirmação de publicação/restauração |
| Reconhecimento                   | Menus rotulados, filtros visíveis, exemplos e instruções junto aos campos                               |
| Flexibilidade                    | Busca global, links diretos, voltar/avançar e rascunhos automáticos                                     |
| Minimalismo                      | Hierarquia clara, espaços livres e uma ação principal por etapa                                         |
| Recuperação de erros             | Mensagens em português indicando como corrigir, sem apagar o texto digitado                             |
| Ajuda                            | Central com perguntas frequentes e instruções de instalação/contexto                                    |

Recursos: documento pt-BR, landmarks, link de salto, labels de formulários, foco visível, estados `aria-current`/`aria-pressed`, progresso com valores acessíveis, gráfico com descrição, avisos vivos, modal com Escape e contenção/restauração de foco. Movimento reduzido respeitado. Layout responsivo e botões principais com área mínima próxima de 44 px.

Não foi realizada auditoria formal WCAG nem avaliação com alunos/professores. Heurísticas são critérios de projeto, não uma certificação de usabilidade.

## 10. Responsividade

- Desktop: sidebar fixa, topo com seletor, conteúdo com grades.
- Tablet: sidebar compacta, grades reduzidas e cartões reorganizados.
- Celular até 760 px: menu lateral recolhível, navegação inferior, conteúdo em uma coluna e botões adaptados.
- Telas muito estreitas: redução de elementos decorativos e redistribuição das notas para evitar rolagem horizontal.

Os valores de domínio, histórico, calendário e a base de práticas anteriores são ilustrativos. Contagens de atividades e novas conclusões refletem o estado local. Não confundir métricas estáticas com resultados produzidos por IA.

## 11. Limitações e próximos incrementos

Ainda faltam: autenticação/convites reais; cadastro completo de escolas/turmas/atividades; consentimento; armazenamento seguro de arquivos; conferência OCR; correção multimodal; ingestão/versões da base; critérios dinâmicos; modelos de domínio; geração de exercícios; tendências; relatórios e observabilidade reais. A documentação original descreve um produto maior do que a demonstração frontend aqui entregue.

O primeiro incremento recomendado é integrar o ciclo de submissão e revisão antes de conectar os indicadores. Depois, substituir dados ilustrativos por respostas do backend, com estados de carregamento/erro/vazio da rede. Ao integrar contas reais, remover o seletor livre de perfil.

Dependências: a instalação reportou uma cadeia de alertas de desenvolvimento relacionada a `braces` → Metro → tipos de React Native; `npm audit fix` compatível não resolveu na data desta entrega. Ver detalhes e status verificado em `VALIDACAO.md`. Não foram forçadas versões incompatíveis nem ignorados os alertas no lockfile.
