import type { Page, Role } from "../types";
export const allowedPages: Record<Role, Page[]> = {
  aluno: [
    "inicio",
    "atividades",
    "evolucao",
    "estudos",
    "ajuda",
    "configuracoes",
  ],
  professor: [
    "inicio",
    "revisoes",
    "turmas",
    "materiais",
    "ajuda",
    "configuracoes",
  ],
  gestor: ["inicio", "revisoes", "turmas", "ajuda", "configuracoes"],
};
export function readRoute(hash: string) {
  const [rawRole, rawPage, rawId] = hash.replace(/^#\/?/, "").split("/");
  const role: Role =
    rawRole === "professor" || rawRole === "gestor" ? rawRole : "aluno";
  const page = allowedPages[role].includes(rawPage as Page)
    ? (rawPage as Page)
    : "inicio";
  return {
    role,
    page,
    activity:
      page === "atividades" || page === "revisoes" ? rawId || null : null,
    study: page === "estudos" ? rawId || null : null,
  };
}
