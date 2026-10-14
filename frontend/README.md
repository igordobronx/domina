# Domina · Frontend

Interface de aprendizagem da **Domina**, criada para Lucas a partir dos documentos de requisitos v0.1 e da identidade visual fornecida. Entrega exclusivamente frontend: aplicação responsiva e instalável como PWA, com dados demonstrativos.

## Executar

Pré-requisitos: Node.js 22.12+ (validado com Node 24) e npm.

```sh
npm ci
npm run dev
```

Abra o endereço exibido no terminal. Para testar **instalação e offline**, use a versão de produção:

```sh
npm run build
npm run preview
```

O preview usa normalmente `http://localhost:4173`. Não é uma hospedagem pública. Em produção, publique a pasta `dist/` em um servidor HTTPS. A configuração atual pressupõe publicação na raiz do domínio.

## O que está pronto

- Visão geral do aluno com mapa de conhecimento, atividades e plano de prática.
- Envio demonstrativo por texto ou arquivo, validação e rascunhos separados por atividade.
- Fila do professor, edição de notas, feedback e confirmação de aprovação.
- Resultado visível na área do aluno somente depois da aprovação.
- Evolução com gráfico ilustrativo e filtro por matéria.
- Três exercícios interativos, explicação da resposta e registro de conclusão.
- Painéis de professor e gestor, turma demonstrativa e materiais.
- Preferências, exportação/restauração local, ajuda, busca e acesso demonstrativo por perfil.
- PWA com ícones, manifest, cache da interface, aviso offline e atualização com confirmação.
- Layout para celular, tablet e computador, navegação inferior no celular e teclado no desktop.

## Tecnologia e alcance

**TypeScript + React + React Native for Web + Vite.** Os controles compartilhados usam `Pressable`, `Text`, `View` e `TextInput` de React Native, resolvidos para React Native for Web. A composição das telas usa também HTML semântico, CSS responsivo e SVG, específicos da web.

Esta entrega executa em **navegadores/PWA** de celular e computador. Não é um projeto Expo, APK, IPA nem aplicativo Windows nativo. Um futuro build nativo exige adaptar os elementos DOM, arquivos, estilos CSS, navegação e armazenamento. Não se deve tratar esta versão como código já pronto para compilar nas lojas.

As fontes são empacotadas localmente; não há carregamento de Google Fonts nem uso de API de IA. Os dados ficam em `localStorage`, sem envio a servidor.

## Documentação

- [Documentação completa do frontend](docs/FRONTEND.md)
- [Roteiro de validação](docs/VALIDACAO.md)
- [Publicar na Vercel](docs/DEPLOY-VERCEL.md)

## Comandos

| Comando            | Finalidade                                         |
| ------------------ | -------------------------------------------------- |
| `npm run dev`      | Desenvolvimento com atualização automática         |
| `npm run build`    | Verificação TypeScript e build com PWA             |
| `npm run preview`  | Servir a versão de produção localmente             |
| `npm test`         | Testes de regras e navegação                       |
| `npm run test:e2e` | Fluxos em Chrome; requer preview em localhost:4173 |
| `npm run format`   | Formatar o projeto                                 |

## Experimente o fluxo

1. Como **Aluno**, abra **Minhas atividades** e escolha a redação sobre inclusão digital.
2. Digite a resposta, confirme a revisão do texto e envie.
3. Troque para **Professor** no seletor superior.
4. Abra a redação na fila, ajuste notas, escreva feedback e confirme a aprovação.
5. Volte a **Aluno** e abra a atividade para consultar o resultado.

O seletor de perfis é uma ferramenta de demonstração, sem autenticação ou autorização real. Não utilize dados de alunos reais neste protótipo.
