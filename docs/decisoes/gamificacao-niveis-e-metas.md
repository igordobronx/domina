# Gamificação: níveis e metas

## Ideia em uma frase
Professores e gestores criam **metas**; o aluno cumpre; cada meta cumprida dá **pontos**; os pontos
somados definem o **nível**. Tudo é calculado dos dados reais (envios, notas aprovadas, domínio):
ninguém marca "cumprido" à mão.

## Como o aluno sobe de nível
**Nível = soma dos pontos das metas concluídas.** Não existe outro caminho: nota alta, tempo de uso
ou número de logins não dão nível por si; só uma meta concluída dá.

| Nível | Nome | Pontos a partir de |
|---|---|---|
| 1 | Iniciante | 0 |
| 2 | Aprendiz | 20 |
| 3 | Explorador | 50 |
| 4 | Estudante dedicado | 100 |
| 5 | Veterano | 180 |
| 6 | Mestre | 300 |
| 7 | Lenda | 500 |

As faixas ficam em `NIVEIS`, em `backend/app/metas.py`. Mudar a tabela muda o nível de todos
na hora, porque o nível não é gravado, é calculado.

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

## Ranking: privacidade (LGPD)
Os alunos são em boa parte menores de idade. Por isso:
- O ranking é **só para professor e gestor** (rota `GET /metas/ranking`); o aluno recebe 403.
- Ordena por **pontos**, nunca por nota. Não mostra notas nem erros de ninguém.
- O aluno vê só o próprio nível e as próprias metas; metas individuais de um aluno não aparecem para os colegas.

## O que o sistema não faz (de propósito)
- Não dá pontos por login, tempo de uso ou nota solta; só por meta concluída.
- Não tem ranking público entre alunos.
- Não tira pontos: nível não desce, nem quando a meta é arquivada.
- Ainda não há tela para editar meta (a API já aceita), nem medalhas, sequência de dias, ou o fim da meta
  no calendário.

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
