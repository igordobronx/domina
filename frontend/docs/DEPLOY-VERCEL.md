# Publicar o Domina na Vercel

O projeto já contém `vercel.json` com as configurações de build. A publicação não exige variáveis de ambiente nem backend.

1. Acesse sua conta na Vercel e escolha **Add New → Project**.
2. Conecte sua conta GitHub, se necessário, e permita acesso ao repositório do Domina.
3. Importe o repositório `domina-front`.
4. Mantenha **Root Directory** na raiz (`./`).
5. Confira estas opções:

| Campo | Valor |
|---|---|
| Framework Preset | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Node.js | 24.x |
| Environment Variables | Nenhuma |

6. Clique em **Deploy** e aguarde o build.
7. Abra o endereço HTTPS fornecido pela Vercel no computador e no celular.

As rotas usam fragmentos como `/#aluno/atividades`, portanto não precisam de reescrita de caminhos. O service worker e o manifest recebem `Cache-Control: no-cache` para permitir revalidação das atualizações.

## Verificação no celular

- Confira o envio demonstrativo, a troca de perfis e a aprovação.
- No Android/Chrome, use **Instalar app** na página inicial.
- No iPhone/Safari, use **Compartilhar → Adicionar à Tela de Início**.
- Abra pelo ícone instalado: o convite de instalação deve desaparecer.
- Depois de uma primeira visita online, teste reabrir sem internet.

O armazenamento é local a cada navegador/aparelho. O que você fizer no computador não aparece automaticamente no celular. O repositório privado não torna o site publicado privado: verifique as configurações de acesso do projeto na Vercel antes de compartilhar seu endereço.

Referência: [documentação oficial de Vite na Vercel](https://vercel.com/docs/frameworks/frontend/vite).
