import type { Activity } from "../types";
import { listarAtividades, listarSubmissoesRevisao } from "./api";
import { paraStatus } from "./atividades";

function paraData(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

// fila de revisao do professor: uma submissao real por linha (nao agrupada por atividade,
// diferente de carregarAtividadesDoAluno, pois o professor revisa aluno por aluno). Atividades
// que ainda nao receberam nenhum envio tambem entram (uma linha so, status "disponivel") --
// sem isso, uma atividade recem-criada so aparecia pro professor depois que um aluno enviasse.
export async function carregarRevisoes(): Promise<Activity[]> {
  const [submissoes, atividades] = await Promise.all([listarSubmissoesRevisao(), listarAtividades()]);
  const linhas = submissoes.map((s): Activity => ({
    id: s.id,
    title: s.atividade_titulo,
    subject: s.materia,
    date: paraData(s.criado_em),
    status: paraStatus(s.status),
    kind: "redacao",
    student: s.aluno_nome,
    scores: s.nota != null ? [s.nota] : undefined,
    valorTotal: s.valor_total,
  }));

  const atividadesComEnvio = new Set(submissoes.map((s) => s.atividade_id));
  const semEnvio = atividades
    .filter((a) => !atividadesComEnvio.has(a.id))
    .map((a): Activity => ({
      id: a.id,
      title: a.titulo,
      subject: a.materia,
      date: "",
      status: "disponivel",
      kind: a.questoes?.length ? "matematica" : "redacao",
      student: a.alunos.length === 1 ? a.alunos[0].nome : `${a.alunos.length} alunos`,
      questoes: a.questoes ?? undefined,
      valorTotal: a.valor_total,
    }));

  return [...linhas, ...semEnvio];
}
