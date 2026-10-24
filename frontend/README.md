# Domina · Frontend

Interface web do **Domina**, a plataforma de correção com IA para escolas: o aluno envia a
atividade, a IA corrige e o professor revisa e aprova a nota. Este README descreve o frontend e
como ele se conecta ao backend. Para o fluxo completo da correção (entrada, lógica e saída),
veja o [README geral](../README.md).

> O Domina está desenvolvendo e treinando o seu **próprio modelo de IA**, personalizado por
> matéria, ainda em desenvolvimento e treinamento. O frontend conversa só com a API do Domina:
> qualquer versão do modelo que entrar no backend aparece na tela sem mudar a interface.

## O que o frontend faz

Aplicação responsiva e instalável (PWA) com **login real** contra o backend e três perfis, cada
um com as suas telas.

**Aluno**
- **Início:** visão geral do aluno, com o domínio por competência.
- **Atividades:** envia a resposta por **texto** ou por **foto**; na foto, confere e corrige o
  texto que a IA leu antes de confirmar. Pede a correção (o agente roda) e vê a nota da IA como **provisória**.
- **Evolução:** histórico de notas e de domínio por matéria.
- **Estudos:** exercícios de reforço gerados para as competências mais fracas.

**Professor**
- **Revisões:** fila de correções, com as que **requerem atenção** (confiança baixa) no topo.
  Abre cada envio, vê a foto original, os trechos marcados como acerto ou erro, ajusta a nota
  de cada critério, escreve o feedback e **aprova**. A nota final é sempre do professor.
- **Atividades:** cria matérias e atividades. Em redação, basta o título. Em matemática, informa
  as questões com o gabarito e o valor total da atividade.
- **Turmas:** cria turmas, matricula alunos e acompanha o domínio de cada um.
- **Materiais:** envia os materiais de cada matéria (apostilas, rubricas, gabaritos).

**Gestor**
- Acompanha revisões e turmas da escola, sem corrigir nem aprovar (só observa).
- Painel de custo de uso, log de auditoria e consentimento (em Configurações).

## O agente de correção na tela

Na revisão do professor aparece o card **"Passo a passo do agente"**: cada decisão que o agente
tomou ao tratar o envio (ler o texto, escolher o corretor, consultar o histórico, gerar reforço,
avisar o professor) com o **motivo** em uma frase. A mensagem para o aluno, o resumo para o
professor e os exercícios de reforço também vêm do agente. Sem passo a passo gravado, a tela
mostra a correção direta normalmente.

## Redação e matemática

- **Redação ENEM:** as 5 competências (C1 a C5), de 0 a 200 cada em níveis de 40 em 40, total até
  1000, com justificativa e trechos marcados no texto do aluno.
- **Matemática:** uma nota por questão, conferida com o gabarito. O professor define o valor
  total e ele é dividido igualmente entre as questões (50 pontos e 5 questões = 10 por questão).
  Quando a resposta vem por foto, a tela marca na imagem **onde** está cada resposta.

## Tecnologia

**TypeScript + React + React Native for Web + Vite.** Os controles compartilhados usam
`Pressable`, `Text`, `View` e `TextInput` de React Native, resolvidos para React Native for Web.
A composição das telas usa também HTML semântico, CSS responsivo e SVG, específicos da web.

Executa em **navegadores/PWA** de celular e computador. Não é um projeto Expo, APK, IPA nem
aplicativo Windows nativo: um build nativo exigiria adaptar os elementos DOM, arquivos, estilos
CSS, navegação e armazenamento. As fontes são empacotadas localmente (sem Google Fonts).

## Conexão com o backend

Toda a comunicação fica em `src/services/api.ts`, que usa o endereço de `VITE_API_URL` (padrão
`http://localhost:8000`) e o token de login (guardado em `localStorage`, enviado em
`Authorization: Bearer`). Os componentes visuais não chamam a API diretamente.

| Tela | Rotas da API que usa |
|---|---|
| Login | `POST /auth/login`, `GET /usuarios/me` |
| Atividades (aluno) | `POST /submissoes/texto`, `POST /submissoes/imagem`, `PUT /submissoes/{id}/confirmar`, `POST`/`GET /submissoes/{id}/agente` (o agente corrige), `GET /submissoes/{id}/correcao`, `GET /submissoes/minhas` |
| Revisões (professor) | `GET /submissoes`, `PUT /submissoes/{id}/aprovar`, `POST` e `GET /submissoes/{id}/agente` |
| Atividades e matérias | `GET`/`POST /atividades`, `GET`/`POST /materias` (o gestor também lista `/submissoes`) |
| Turmas e usuários | `/turmas`, `/turmas/minhas`, matrícula e membros, `/usuarios`, `GET /alunos/{id}/dominio` |
| Materiais | `GET`/`POST /materias/{id}/documentos` |
| Evolução e estudos | `GET /dominio/meu`, `GET /evolucao/minha`, `GET /estudos/meu` |
| Configurações | `/consentimento`, `/custo-uso` e `/audit-log` |

A API só devolve o que o perfil pode ver (escola, turma e dono do dado são conferidos no
servidor). Esconder um botão na tela não substitui essa checagem.

## Executar

Pré-requisitos: Node.js 22.12+ (validado com Node 24), npm e o backend rodando (veja o README
geral: `docker compose up -d --build`).

```sh
cp .env.example .env.local   # ajuste VITE_API_URL se a API não estiver em localhost:8000
npm ci
npm run dev
```

Abra o endereço exibido no terminal e entre com um usuário do backend (o `seed.py` cria usuários
de exemplo, como `aluno@domina.com`, com a senha definida no próprio `seed.py`). Para testar **instalação e offline**, use a versão de produção:

```sh
npm run build
npm run preview
```

O preview usa normalmente `http://localhost:4173`. Em produção, publique a pasta `dist/` em um
servidor HTTPS e configure `ALLOWED_ORIGINS` no backend com a URL do frontend (veja o README
geral).

## Comandos

| Comando            | Finalidade                                         |
| ------------------ | -------------------------------------------------- |
| `npm run dev`      | Desenvolvimento com atualização automática         |
| `npm run build`    | Verificação TypeScript e build com PWA             |
| `npm run preview`  | Servir a versão de produção localmente             |
| `npm test`         | Testes de regras e navegação                       |
| `npm run test:e2e` | Fluxos em Chrome; requer preview em localhost:4173 |
| `npm run format`   | Formatar o projeto                                 |

## PWA e usabilidade

- Ícones, manifest, cache da interface, aviso offline e atualização com confirmação.
- Layout para celular, tablet e computador, com navegação inferior no celular e teclado no
  desktop.
- Preferências, rascunhos por atividade e exportação/restauração ficam em `localStorage`, só no
  aparelho. O que vem da correção e das notas vem sempre do backend.

## Documentação

- [Documentação completa do frontend](docs/FRONTEND.md)
- [Roteiro de validação](docs/VALIDACAO.md)
- [Publicar na Vercel](docs/DEPLOY-VERCEL.md)

## Experimente o fluxo

1. Entre como **Aluno**, abra **Atividades** e escolha uma redação.
2. Digite a resposta (ou envie uma foto e confira o texto lido), confirme e envie.
3. Peça a correção: a nota da IA aparece como provisória.
4. Entre como **Professor**, abra a redação na **fila de revisões** e veja o passo a passo do agente.
5. Ajuste as notas, escreva o feedback e aprove.
6. Volte ao **Aluno** e abra a atividade para ver o resultado final.

Não use dados de alunos reais fora de um ambiente com consentimento e retenção definidos.
