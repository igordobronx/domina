export type Role = "aluno" | "professor" | "gestor";
export type Page =
  | "inicio"
  | "atividades"
  | "evolucao"
  | "estudos"
  | "revisoes"
  | "turmas"
  | "materiais"
  | "configuracoes"
  | "ajuda";
export type ActivityStatus = "disponivel" | "pendente" | "aprovada";
export interface Activity {
  id: string;
  // so quando ja existe submissao real (lado do aluno): id da submissao, distinto do id da
  // atividade (a.id) -- /submissoes/{id}/corrigir precisa do id da submissao, nao da atividade
  submissaoId?: string;
  title: string;
  subject: string;
  date: string;
  status: ActivityStatus;
  kind: "redacao" | "matematica";
  student: string;
  questoes?: { codigo: string; enunciado: string }[];
  valorTotal?: number;
  text?: string;
  fileName?: string;
  aiScores?: number[];
  scores?: number[];
  feedback?: string;
  // por criterio (competencia/questao): "pontos" sao os acertos/erros concretos que a IA
  // aponta, cada um com o trecho (ou caixa na foto, so exatas por imagem) a destacar na tela
  criterios?: {
    codigo: string;
    nome: string;
    justificativa: string;
    pontos: {
      trecho: string;
      tipo: "acerto" | "erro";
      comentario: string;
      caixa: { x: number; y: number; largura: number; altura: number } | null;
    }[];
  }[];
  // "TEXTO" | "IMAGEM": se "IMAGEM", a foto original pode ser buscada por submissaoId
  tipoEnvio?: string;
}
export interface Topic {
  name: string;
  subject: string;
  value: number;
  evidence: number;
  growth: number;
}
export interface Material {
  id: string;
  name: string;
  subject: string;
  approved: boolean;
  fileName: string;
}
export interface DemoState {
  activities: Activity[];
  materials: Material[];
  completed: string[];
  name: string;
  goal: number;
  drafts: Record<string, string>;
}
