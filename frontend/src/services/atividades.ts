import type { Activity, ActivityStatus } from "../types";
import { listarAtividades, minhasSubmissoes, type MinhaSubmissaoAPI } from "./api";

// chamada so quando ja existe submissao; qualquer status != APROVADA conta como "em revisao"
// (AGUARDANDO_CORRECAO, PENDENTE ou REQUER_ATENCAO -- o aluno nao distingue essas fases)
function paraStatus(statusBackend: string): ActivityStatus {
  return statusBackend === "APROVADA" ? "aprovada" : "pendente";
}

function paraData(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

// carrega as atividades do aluno logado e junta com as submissoes dele (uma por atividade, a mais recente)
export async function carregarAtividadesDoAluno(nomeAluno: string): Promise<Activity[]> {
  const [atividades, submissoes] = await Promise.all([listarAtividades(), minhasSubmissoes()]);
  const porAtividade = new Map<string, MinhaSubmissaoAPI>();
  for (const s of submissoes) if (!porAtividade.has(s.atividade_id)) porAtividade.set(s.atividade_id, s);

  return atividades.map((a): Activity => {
    const submissao = porAtividade.get(a.id);
    const kind = a.tipo === "REDACAO" ? "redacao" : "matematica";
    if (!submissao) {
      return { id: a.id, title: a.titulo, subject: a.materia, date: "", status: "disponivel", kind, student: nomeAluno };
    }
    const aprovada = submissao.status === "APROVADA";
    return {
      id: a.id,
      title: a.titulo,
      subject: a.materia,
      date: paraData(submissao.criado_em),
      status: paraStatus(submissao.status),
      kind,
      student: nomeAluno,
      scores: aprovada ? (submissao.criterios ?? []).map((c) => c.nota_professor ?? c.nota) : undefined,
      feedback: aprovada ? (submissao.feedback ?? undefined) : undefined,
    };
  });
}
