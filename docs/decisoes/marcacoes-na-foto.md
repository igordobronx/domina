# Marcações na foto e avisos ao aluno (19/11/2026)

- **O que já existia:** a IA marca trechos (`CorrecaoCriterio.pontos`): em exatas por foto vêm com `caixa` (posição na folha, fração 0 a 1); na redação vêm como `trecho` destacado no texto transcrito.
- **Etapa 1 (feita):** o PROFESSOR marca à mão sobre a foto (arrasta um retângulo, escolhe Erro/Acerto/Comentário e escreve). Tabela `anotacao` (migration 0032), rotas `/submissoes/{id}/anotacoes` e `/anotacoes/{id}`. Só o professor da turma cria; só o autor edita/apaga; gestor só lê.
- **Quem vê o quê:** o aluno vê as marcas da IA quando pede a correção (como já era) e as do professor **só depois que a correção é aprovada**.
- **Tela "Texto enviado":** exatas por foto mostra a FOTO com as marcas (o texto lido fica recolhido); redação por foto deixa escolher entre "Texto transcrito" e "Foto com marcações". Componente `FotoComMarcas`.
- **Avisos:** tabela `aviso` (0032), `GET /avisos`, `POST /avisos/lidos`. Aprovar a correção avisa o aluno; o sino do topo mostra os avisos reais (confere a cada minuto, sem push).
- **Fica para depois:** posição de cada palavra pelo OCR (palavras clicáveis), IA marcando sobre a foto na redação (sugestões aceitar/editar/descartar, alimentando o Treinar IA), tocar numa marca para destacar o cartão, aviso por e-mail/push.
