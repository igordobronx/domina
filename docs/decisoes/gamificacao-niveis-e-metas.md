# Gamificação: níveis e metas

## Ideia em uma frase
Professores e gestores criam **metas**; o aluno cumpre; cada meta cumprida dá **pontos**; os pontos
somados definem o **nível**. Tudo é calculado dos dados reais (envios, notas aprovadas, domínio):
ninguém marca "cumprido" à mão.

## Como o aluno sobe de nível (XP, desde 18/11/2026)
**Nível = XP total.** O XP vem de **ações do aluno + metas cumpridas** e é **calculado na hora** dos dados
que já existem (`backend/app/gamificacao.py`); nada é gravado, então o passado conta sozinho.

| Ação do aluno | XP |
|---|---|
| Enviar uma atividade (confirmada; 1 vez por atividade) | +10 |
| Enviar dentro do prazo | +5 a mais |
| Professor aprovou a correção | +5 |
| Nota aprovada de 80% ou mais | +10 a mais |
| Responder um exercício | +2 |
| Acertar um exercício ("Parcial" não conta como acerto) | +3 a mais |
| Cumprir uma meta | os pontos da meta |
| A cada 7 dias seguidos estudando | +15 |
| Ganhar uma conquista | +20 |

- **Nota da IA não dá XP.** Só a nota aprovada pelo professor.
- **Exercícios: no máximo 30 XP por dia** (não dá para subir só gerando exercícios da IA).
- **Dia de estudo** = enviou atividade ou respondeu exercício. A sequência continua viva se estudou hoje ou ontem.
- **Conquistas** (+20 XP cada): Primeiro passo, Pontual (5 no prazo), Redator (5 redações), Nota 900+,
  Mão na massa (20 exercícios), Certeiro (50 certos), Constância (7 dias seguidos), Imparável (30 dias), Meta batida.
- A data do "+5 aprovada" no histórico é a data do envio (o banco não guarda quando o professor aprovou).

| Nível | Nome | XP a partir de |
|---|---|---|
| 1 | Iniciante | 0 |
| 2 | Aprendiz | 80 (cerca de 1 semana) |
| 3 | Explorador | 300 |
| 4 | Estudante dedicado | 550 |
| 5 | Veterano | 850 |
| 6 | Mestre | 1200 |
| 7 | Lenda | 1600 |

As faixas ficam em `NIVEIS`, em `backend/app/metas.py`. A API continua chamando o XP de `pontos`
(`NivelResponse`); a tela mostra "XP". O aluno vê tudo em "Minha evolução" (`GET /gamificacao/minha`).

O professor/gestor escolhe quanto cada meta vale: **10, 20, 30, 50 ou 100 pontos** (a API aceita
1 a 100). Regra prática: meta fácil e curta vale 10 a 20; meta que exige semanas ou nota alta vale 50
ou 100. Assim o ritmo do nível depende da dificuldade da meta, não só de quantas metas existem.

## Critérios de uma meta (quando ela conta como cumprida)
| Tipo | O aluno cumpre quando… | Unidade do alvo |
|---|---|---|
| `ENTREGAS` | entregou (e confirmou) N atividades no período | quantidade |
| `ENTREGAS_NO_PRAZO` | entregou N atividades até o prazo de cada uma | quantidade |
| `NOTA_ATIVIDADE` | teve **pelo menos X%** em UMA atividade com correção aprovada | percentual (1–100) |
| `MEDIA_MATERIA` | tem **média de X%** nas correções aprovadas de uma matéria | percentual (1–100) |
| `DOMINIO_COMPETENCIA` | chegou a **X% de domínio** numa competência (C1–C5) de uma matéria de redação | percentual (1–100) |
| `PRATICA_RESPONDIDOS` | respondeu N exercícios do plano de estudo no período | quantidade |
| `PRATICA_ACERTOS` | **acertou** N exercícios do plano de estudo no período | quantidade |

Detalhes que valem para todas:
- **Só conta a partir da data de início** da meta (padrão: hoje). Uma meta nova nunca nasce cumprida
  por causa do passado. Se houver data de fim, só conta o que foi enviado até ela.
- **Entrega só conta depois de confirmada.** Foto lida pelo OCR e ainda não confirmada pelo aluno não é entrega.
- **Nota só conta depois de aprovada** pelo professor (a prova objetiva já nasce aprovada). Nota provisória da IA não conta.
- Percentual de nota = nota aprovada ÷ valor total da atividade (redação = 1000).
- **Domínio** é acumulado (não depende do período) e só existe para redação; a meta deixa de poder ser
  cumprida depois do fim, se houver.
- Matéria é opcional em `ENTREGAS`, `ENTREGAS_NO_PRAZO` e `NOTA_ATIVIDADE` (vazio = todas) e obrigatória nas outras duas.

## Quem cria, para quem, e quem vê
| | Cria metas para | Vê |
|---|---|---|
| **Aluno** | (não cria) | só as metas que valem para ele e o próprio nível. **Nunca** vê ranking |
| **Professor** | as turmas dele, ou um aluno dessas turmas | as metas das turmas dele, as que criou e as da escola toda; ranking das turmas dele |
| **Gestor** | qualquer turma, qualquer aluno ou a **escola toda** | tudo da escola; ranking da escola |

Escopo da meta: `aluno_id` preenchido = individual; senão `turma_id` preenchido = turma; senão escola toda.
O backend decide tudo isso (`backend/app/routers/metas.py`): turma de outro professor dá 403; aluno
ou meta de outra escola dá 404; escola toda por professor dá 403. Quem edita: quem criou ou o gestor.

## Como o progresso é calculado
- O progresso **não é gravado**; é recalculado dos envios, correções e domínio (`progresso()` em `app/metas.py`).
- Só a **conclusão** é gravada (`meta_concluida`: meta, aluno, data). Por isso editar ou arquivar uma meta
  nunca deixa o nível de alguém inconsistente.
- Quando roda: logo depois de (1) o aluno enviar ou confirmar um envio, (2) uma prova objetiva ser corrigida,
  (3) o professor aprovar uma correção. Roda também ao abrir `GET /metas/minhas`, como rede de segurança.
  Repetir o cálculo não duplica nada (a chave de `meta_concluida` é meta + aluno).
- Se o cálculo falhar, o envio/aprovação **não** falha: o erro vai para o log e a próxima abertura da tela corrige.

## Editar, arquivar e o que acontece com os pontos
- Título, descrição e fim sempre podem mudar.
- **Alvo e pontos congelam** assim que alguém conclui a meta (409), para o nível de ninguém mudar de repente.
  Para mudar o critério depois disso, crie uma meta nova.
- "Excluir" **arquiva** a meta (`ativa = false`). Quem já concluiu **mantém os pontos**. Nada é apagado.
- Toda criação, edição e arquivamento entra na auditoria (`CRIAR`, `EDITAR`, `ARQUIVAR` em `Meta`).

## Tela de edição e calendário
- Na tela "Metas e níveis", quem criou a meta (ou o gestor) vê **Editar** e **Arquivar**. A edição mostra título, descrição e fim;
  alvo e pontos só aparecem enquanto ninguém concluiu (depois disso a tela avisa e o servidor recusa com 409).
  Limpar o campo "Termina em" tira o fim da meta.
- O **fim da meta aparece no calendário** (tipo "Meta", "Fim da meta: …") no dia do fim, para quem enxerga a meta:
  o aluno vê só as dele que ainda não concluiu; professor e gestor veem as da lista de metas deles. Meta sem fim não aparece.

## Ranking: privacidade (LGPD)
Os alunos são em boa parte menores de idade. Por isso:
- O ranking é **só para professor e gestor** (rota `GET /metas/ranking`); o aluno recebe 403.
- Ordena por **XP**, nunca por nota. Não mostra notas nem erros de ninguém.
- O aluno vê só o próprio nível e as próprias metas; metas individuais de um aluno não aparecem para os colegas.

## O que o sistema não faz (de propósito)
- Não dá XP por login, tempo de uso ou nota da IA.
- Não tem ranking público entre alunos.
- Não tira pontos: nível não desce, nem quando a meta é arquivada.
- Não há medalhas criadas pelo professor (as 9 conquistas são fixas).

## Onde está no código
| Parte | Arquivo |
|---|---|
| Modelo (`Meta`, `MetaConcluida`) | `backend/app/models/usuario.py` |
| Migration | `backend/migrations/versions/0011_metas.py` |
| Regras: níveis, progresso, conclusão | `backend/app/metas.py` |
| Rotas e permissões | `backend/app/routers/metas.py` |
| Contratos (validação dos tipos e alvos) | `backend/app/schemas/metas.py` |
| Ganchos que reavaliam as metas | `routers/submissoes.py` (envio, confirmação, objetiva) e `routers/correcoes.py` (aprovar) |
| Testes | `backend/tests/test_metas.py` |
| Telas | `frontend/src/screens/Metas.tsx` (aluno e equipe) e o cartão de nível em `Dashboard.tsx` |

## Rotas
| Rota | Quem | O quê |
|---|---|---|
| `POST /metas` | professor, gestor | cria meta |
| `GET /metas` | professor, gestor | lista metas ativas com "X de Y concluíram" |
| `PUT /metas/{id}` | quem criou, ou gestor | edita (alvo/pontos só sem conclusões) |
| `DELETE /metas/{id}` | quem criou, ou gestor | arquiva |
| `GET /metas/minhas` | aluno | nível e metas com progresso |
| `GET /metas/ranking?turma_id=` | professor, gestor | ranking por pontos |

## Plano de estudo: respostas salvas
- Os exercícios do plano (`GET /estudos/meu`) ficam **salvos no banco** (`exercicio`), ligados à competência e ao aluno.
  O aluno recebe o exercício **sem gabarito**; quem confere é o servidor (`POST /exercicios/{id}/responder`), que grava a resposta
  (`exercicio_resposta`, uma por aluno e exercício) e só então devolve certo/errado e a explicação.
- A rota só gera exercícios novos quando não sobra nenhum pendente, e até 9 por aluno por dia (`LIMITE_DIARIO`).
- A prática fica **separada do domínio**: o domínio continua vindo só de correções aprovadas. A prática por competência está em
  `GET /estudos/minha-pratica` (aluno) e `GET /alunos/{id}/pratica` (professor/gestor, mesmas regras de escopo do domínio).
- Os exercícios de reforço que o agente gera depois de corrigir uma redação também são salvos e entram no plano do aluno.
- As metas `PRATICA_RESPONDIDOS` e `PRATICA_ACERTOS` contam essas respostas.

## Plano de estudo de exatas: onde o aluno erra
- Quando uma correção de exatas é aprovada (ou ao abrir o plano, o que também pega correções antigas e as objetivas),
  cada questão em que o aluno ficou **abaixo de 80% do valor dela** vira uma linha em `erro_aluno` (`app/erros.py`):
  matéria, atividade, correção, a questão, o gabarito, a nota e **onde errou** (justificativa + pontos de erro da correção).
  Uma linha por questão, então registrar de novo não duplica.
- O plano gera um exercício por erro (os mais fracos primeiro), com o mesmo assunto e o mesmo tipo de erro. Cada exercício guarda
  `erro_id`, então dá para ver de qual correção ele veio. O aluno vê a matéria e "Você errou: …" no cartão.
- Redação continua pelo domínio C1–C5. O domínio não muda com a prática; os limites diários valem para os dois tipos.
