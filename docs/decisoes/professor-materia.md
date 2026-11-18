# Professor e matéria (quem leciona o quê)

## Regra
O **gestor** define, por turma, quais matérias cada professor leciona (tabela `professor_materia`: professor + turma + matéria).
O professor **não se atribui** matérias. Uma exceção: quando ele **cria** uma matéria, ela passa a ser dele em todas as turmas onde ele leciona.

## O que muda para o professor
| Onde | Regra |
|---|---|
| Estatística do aluno (`/alunos/{id}/dominio`, `/pratica`, `/evolucao`) | só as matérias que ele leciona **nas turmas do aluno**. Gestor vê todas |
| `GET /materias` | só as dele (gestor vê todas) |
| Criar atividade, exercício | só matéria que ele leciona **naquela turma** (403 com "Você não leciona X na turma Y") |
| Criar meta com matéria, enviar material | só matéria dele (em qualquer turma) |
| Fila de Revisões | **não muda**: continua pelo autor/corretor da atividade |
| Sem nenhuma matéria atribuída | telas vazias, com aviso para pedir ao gestor |

## Como o gestor define
Em **Turmas** → abrir a turma → ao lado de cada professor, "Definir matérias" (marcar e salvar). Rotas:
`GET /turmas/{id}/materias-dos-professores` (gestor vê todos; professor só as dele) e
`PUT /turmas/{id}/professores/{prof}/materias` (só gestor; troca o conjunto; entra na auditoria).

## Migration 0022
Preenche o vínculo a partir do histórico: matéria/turma das atividades que o professor **criou** ou **corrigiu**.
Quem não tem histórico começa sem matéria até o gestor definir.

## Código
`app/lecionados.py` (regras), `routers/turma.py` (rotas do gestor), `routers/dominio.py`, `evolucao.py`, `estudos.py` (filtros),
`routers/submissoes.py`, `exercicios.py`, `metas.py`, `documento.py` (limites de criação), tela `Management.tsx` (`MateriasDoProfessor`).

## Cadastro de pessoas pelo gestor (tela "Equipe e alunos")
- **Editar** nome e e-mail (`PUT /usuarios/{id}`), **trocar senha** (`PUT /usuarios/{id}/senha`: o gestor define a senha nova e passa para a pessoa;
  ele confirma a própria senha em `X-Confirmar-Senha`), **desativar/reativar** (`PUT /usuarios/{id}/ativo`).
- **Turmas e matérias de uma vez:** `GET/PUT /usuarios/{id}/vinculos` troca o conjunto de turmas da pessoa; no professor, cada turma leva as
  matérias que ele leciona nela. Turma que sai da lista perde o vínculo (e as matérias dela); atividades e notas ficam. Mover aluno = trocar a turma.
  Criar professor já aceita `turmas: [{turma_id, materia_ids}]`.
- **Desativar, nunca excluir:** conta desativada não entra (403 no login) e o token que já existia deixa de valer (401). Notas e histórico ficam.
- **Quem mexe em quem:** gestor edita aluno e professor da própria escola; conta de gestor só o administrador; ninguém edita o admin.
- Tudo entra na auditoria (`EDITAR`, `TROCAR_SENHA`, `DESATIVAR`, `ATIVAR`). Migration 0023 (`usuario.ativo`).
