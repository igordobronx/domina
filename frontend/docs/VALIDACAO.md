# Validação do frontend

Resultado em 6 de outubro de 2026:

- Build de produção e TypeScript: aprovados.
- Vitest: 6 testes aprovados.
- Playwright/Chrome: 6 testes de fluxo aprovados.
- Recarga offline, manifest e ocultação em standalone simulado: aprovados.
- Capturas de aluno no desktop/celular e professor/revisão inspecionadas visualmente.
- `npm audit --omit=dev`: nenhuma vulnerabilidade reportada.
- `npm audit` completo: 9 alertas altos na cadeia de desenvolvimento descrita ao final.

## Verificação automatizada

```sh
npm run build
npm test
```

Em outro terminal, inicie o preview e execute os testes de navegador:

```sh
npm run preview -- --port 4173
npm run test:e2e
```

A configuração usa o Chrome instalado (`channel: chrome`). Caso não exista, instale o navegador ou adapte `playwright.config.ts` ao ambiente. Não execute os testes do service worker no servidor de desenvolvimento, pois o registro fica restrito ao build.

Os testes cobrem:

1. Resultado pendente invisível ao aluno, preservação da sugestão de IA e notas válidas.
2. Escalas distintas de redação e matemática.
3. Links e normalização de páginas por perfil.
4. Texto obrigatório, rascunho após recarga, envio, aprovação e persistência.
5. Exercício com explicação, busca vazia, Escape e Voltar do navegador.
6. Convite de instalação dispensável e oculto em standalone simulado.
7. Manifest, controle pelo service worker e recarga offline.
8. Larguras 360, 390, 768 e desktop 1440 px, ausência de overflow horizontal e erros de execução.

## Roteiro manual

- Navegar por teclado, abrir/fechar modais e observar o retorno de foco.
- Enviar um arquivo inválido ou maior que 10 MB e corrigir o erro.
- Alternar atividade enquanto digita e verificar separação dos rascunhos.
- Enviar resposta de matemática e conferir escala 0–10 na revisão.
- Cancelar a confirmação de aprovação e verificar que o resultado continua pendente.
- Exportar dados e restaurar a demonstração após confirmação.
- Testar fonte ampliada, leitor de tela e modo de movimento reduzido.
- Publicar em HTTPS para testar instalação real em Android e iOS.
- Instalar, abrir pelo ícone e verificar ausência do convite.
- Publicar nova versão e confirmar o fluxo de atualização sem perda do rascunho.

## Limites da validação

Chrome local não representa todos os navegadores. O modo standalone é simulado nos testes; a instalação real em iPhone/Android requer dispositivos e hospedagem HTTPS. Os testes não comprovam autenticação, segurança multi-escola, conformidade legal nem qualidade pedagógica.

O arquivo `package-lock.json` fixa as dependências utilizadas. Na instalação, `npm audit` apontou 9 alertas altos na cadeia de ferramentas de desenvolvimento de React Native/Metro, causados pelo pacote `braces`; a correção compatível automática não eliminou os alertas. Isso precisa ser reavaliado antes de exposição de qualquer servidor de desenvolvimento. O frontend de produção usa React Native for Web, não o servidor Metro.
