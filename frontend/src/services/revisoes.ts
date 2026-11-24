import type { Activity } from "../types";
import { listarAtividades, listarSubmissoesRevisao } from "./api";
import { paraStatusRevisao } from "./atividades";

function paraData(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

// uma atividade criada para uma turma, com quem ja enviou e quem ainda nao
export interface GrupoAtividade {
  atividadeId: string;
  titulo: string;
  materia: string;
  turmaId: string;
  turmaNome: string;
  kind: "redacao" | "matematica";
  prazo: string | null; // AAAA-MM-DD
  alunos: { id: string; nome: string; envio?: Activity }[]; // envio = o mais recente do aluno; sem envio = nao entregou
}

// fila de revisao: uma linha por atividade/turma (GrupoAtividade); dentro dela, um aluno por linha.
// "linhas" tem as submissoes reais (o id da linha e o da submissao, que abre a revisao).
export async function carregarRevisoes(): Promise<{ linhas: Activity[]; grupos: GrupoAtividade[] }> {
  const [submissoes, atividades] = await Promise.all([listarSubmissoesRevisao(), listarAtividades()]);
  const linhas = submissoes.map((s): Activity => ({
    id: s.id,
    atividadeId: s.atividade_id,
    alunoId: s.aluno_id,
    title: s.atividade_titulo,
    subject: s.materia,
    date: paraData(s.criado_em),
    status: paraStatusRevisao(s.status),
    kind: "redacao",
    student: s.aluno_nome,
    turmaId: s.turma_id,
    turmaNome: s.turma_nome,
    scores: s.nota != null ? [s.nota] : undefined,
    valorTotal: s.valor_total,
  }));

  const grupos = atividades.filter((a) => a.na_minha_revisao).map((a): GrupoAtividade => ({
    atividadeId: a.id,
    titulo: a.titulo,
    materia: a.materia,
    turmaId: a.turma_id,
    turmaNome: a.turma,
    kind: a.questoes?.length ? "matematica" : "redacao",
    prazo: a.prazo,
    // a lista vem da mais nova para a mais antiga: o primeiro de cada aluno e o ultimo envio dele
    alunos: a.alunos.map((al) => ({
      id: al.id,
      nome: al.nome,
      envio: linhas.find((l) => l.atividadeId === a.id && l.alunoId === al.id),
    })),
  }));
  return { linhas, grupos };
}

// "para revisar" = enviou e o professor ainda nao aprovou
export const paraRevisar = (g: GrupoAtividade) =>
  g.alunos.filter((x) => x.envio && x.envio.status !== "aprovada").length;
export const enviaram = (g: GrupoAtividade) => g.alunos.filter((x) => x.envio).length;
