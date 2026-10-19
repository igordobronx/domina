import type { Activity } from "../types";
import { listarSubmissoesRevisao } from "./api";
import { paraStatus } from "./atividades";

function paraData(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

// fila de revisao do professor: uma submissao real por linha (nao agrupada por atividade,
// diferente de carregarAtividadesDoAluno, pois o professor revisa aluno por aluno)
export async function carregarRevisoes(): Promise<Activity[]> {
  const submissoes = await listarSubmissoesRevisao();
  return submissoes.map((s): Activity => ({
    id: s.id,
    title: s.atividade_titulo,
    subject: s.materia,
    date: paraData(s.criado_em),
    status: paraStatus(s.status),
    kind: "redacao",
    student: s.aluno_nome,
    scores: s.nota != null ? [s.nota] : undefined,
  }));
}
