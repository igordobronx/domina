# Notificações (sino do topo)

Decidido em 23/11/2026. Tabela `aviso` (migration 0033: `tipo`, `destino`, `chave`, `qtd`), código em `backend/app/avisos.py`, rotas `GET /avisos` e `POST /avisos/lidos` em `routers/avisos.py`.

**Dois jeitos de nascer**
- **Evento** (a rota chama `avisos.tentar`, que nunca derruba a requisição): atividade nova → alunos da turma; exercício novo → alunos alvo; correção aprovada → aluno; aluno enviou → professor da atividade (agrupado: "5 novos envios em X"); IA corrigiu → professor (agrupado; "pede a sua atenção" quando a correção requer atenção).
- **Alerta por tempo** (conferido em `GET /avisos`, no máximo a cada 5 min por pessoa, sem tarefa agendada). `chave` impede repetir:
  - aluno: prazo em 2 dias / amanhã / hoje / vencido ontem (só se ainda não enviou), meta batida, meta termina em até 3 dias, conquista nova (últimos 3 dias), subiu de nível, sequência em risco (depois das 18h), feriado e evento do calendário amanhã;
  - professor: prazo acabou e N alunos não enviaram, envios parados há mais de 3 dias (1 por semana), feriado e evento amanhã.

**Regras**
- Primeiro acesso não vira enxurrada: nível só avisa quando sobe depois da 1ª conferência (guarda um aviso `MARCADOR`, que nunca aparece); meta/conquista só valem se forem dos últimos dias.
- O texto do aviso fica dentro do sistema (sem e-mail nem push externo), por causa da LGPD dos menores.
- Clicar no aviso abre a tela do `destino` (atividades, revisoes, metas, evolucao, estudos, calendario).

**Ficou para depois:** preferências para silenciar tipos, resumo semanal, "aluno em risco" para o professor, avisos do Treinar IA, e-mail/push no celular, avisos para o gestor.
