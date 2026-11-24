# Criar atividade de exatas: menos informação e atalhos (design)

Task: "Matérias: melhorar o visual do frontend de matemática, física e demais matérias - atalhos e menos informação na tela."
Escopo combinado: tela do professor, formulário de questões em **Nova atividade** e em **Editar atividade**. Só o site; sem mudança no backend nem no banco.

## Atalhos (símbolos da matéria)
- Hoje: um botão "Ω Símbolos" embaixo de **cada** campo, e o painel abre sempre em Química.
- Novo: **um botão "Ω Símbolos" só**, ao lado do título "Questões e gabarito". A barra fica fechada; clicou, ela abre (e acompanha a rolagem). O clique num símbolo põe no campo onde o cursor está. (Primeira versão deixava a barra sempre aberta; o usuário achou poluído.)
- A barra já abre nos símbolos da matéria escolhida: Matemática → Matemática; Física → **grupo novo de Física** (Δ, μ, λ, ω, →, °, ·, ², ³, √, ≈, ±...); Química → Química. Os outros grupos ficam a um clique.
- Nas telas do aluno nada muda (o botão por campo continua lá).

## Menos informação
- Rótulos curtos: "Prazo (opcional)", "Turmas", "Questão 1", "Resposta correta".
- Explicação do formato vira uma linha curta: "Corrige na hora pelo gabarito" (objetiva) e "A IA confere com a resposta correta" (discursiva).
- Valor total e "pontos por questão" numa linha só: "Valor total [1000] pontos · 500 por questão".
- Cada questão num bloco com borda e bom espaço entre os campos; "Remover" vira um ícone no canto do bloco. "+ Alternativa", "+ Item" e "+ Figura" são links discretos.
- Itens a), b)... só aparecem quando o professor clica em "+ Item" (hoje o "Item a)" já vem aberto).
- Figura: botão pequeno "+ Figura" em vez do campo de arquivo sempre à mostra.
- Os textos de exemplo dentro dos campos (placeholder) ficam mais curtos.

## Código
- `components/CampoComSimbolos.tsx`: grupo Física; função que escolhe o grupo pelo nome da matéria (com teste); `BarraSimbolos` + um contexto que guarda o último campo focado; o campo pode esconder o próprio botão quando está dentro da barra única.
- `screens/Activities.tsx`: `NovaAtividade` e `EditarAtividade` usam a barra única e o layout mais enxuto.
- `styles.css`: estilos do bloco da questão e da barra.
