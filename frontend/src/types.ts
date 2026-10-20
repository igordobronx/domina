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
  title: string;
  subject: string;
  date: string;
  status: ActivityStatus;
  kind: "redacao" | "matematica";
  student: string;
  questoes?: { codigo: string; enunciado: string }[];
  text?: string;
  fileName?: string;
  aiScores?: number[];
  scores?: number[];
  feedback?: string;
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
