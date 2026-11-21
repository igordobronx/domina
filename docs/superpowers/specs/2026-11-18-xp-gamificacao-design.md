# XP, sequência e conquistas na "Minha evolução" (task 2)

## Por quê
Hoje o aluno só ganha pontos quando cumpre uma meta criada pelo professor. Sem metas, fica no nível 1
para sempre. O objetivo é **engajamento todo dia**: o aluno sobe sozinho fazendo o que já faz no Domina.

## Decidido com o usuário (18/11)
- XP vem de **metas + ações do aluno** (opção B).
- Peças na tela "Minha evolução": **barra de XP e nível, histórico de XP, sequência de dias, conquistas**.
- Tabela de XP:

| Ação | XP |
|---|---|
| Enviar uma atividade (confirmada; 1 vez por atividade) | +10 |
| Enviar dentro do prazo | +5 a mais |
| Professor aprovou a correção | +5 |
| Nota aprovada ≥ 80% | +10 a mais |
| Responder um exercício | +2 |
| Acertar um exercício | +3 a mais |
| Cumprir uma meta | os pontos da meta |
| A cada 7 dias seguidos estudando | +15 |
| Ganhar uma conquista | +20 |

- Nota da IA não dá XP. Exercícios: no máximo **30 XP por dia**. Dia de estudo = enviou atividade ou
  respondeu exercício. **O passado conta.**
- Níveis: mesmos 7 nomes; nível 1 → 2 em **cerca de 1 semana**, depois 2 a 3 semanas por nível.
- Conquistas (+20 XP cada): Primeiro passo (1ª atividade), Pontual (5 no prazo), Redator (5 redações),
  Nota 900+ (redação aprovada ≥ 900), Mão na massa (20 exercícios), Certeiro (50 exercícios certos),
  Constância (7 dias seguidos), Imparável (30 dias seguidos), Meta batida (1ª meta).
- O usuário dispensou o desenho de tela ("eu confio, pode implementar").

## Abordagens
1. **XP calculado na hora dos dados que já existem (escolhida).** Igual ao nível hoje. Sem migration,
   o passado conta sozinho, nada fica inconsistente.
2. Tabela de eventos de XP gravados: precisaria de migration, ganchos em cada ação e um "backfill" do passado.
3. Contador de XP no usuário: rápido de ler, mas fácil de dessincronizar e não dá histórico.

## Decisões minhas (para conferir)
- Faixas de XP: 0 Iniciante, 80 Aprendiz, 300 Explorador, 550 Estudante dedicado, 850 Veterano,
  1200 Mestre, 1600 Lenda (aluno ativo faz uns 80–100 XP por semana).
- A data do "+5 aprovada" no histórico é a data do envio (o banco não guarda quando o professor aprovou).
- Exercício discursivo marcado "Parcial" conta como respondido, não como acerto.
- Sequência "viva" se o aluno estudou hoje ou ontem.
- O campo `pontos` da API continua com esse nome, mas agora é XP; a tela mostra "XP".
- Ranking do professor/gestor ordena por XP. Visão geral e "Metas e níveis" passam a falar em XP.
- Nova rota `GET /gamificacao/minha` (só aluno) com nível, histórico, sequência e conquistas.

## Fora do escopo
Task 3 (visão geral por matéria). Medalhas criadas pelo professor. Ranking para aluno (continua proibido).
