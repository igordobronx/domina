import type { Page, Role } from "../types";
export const allowedPages: Record<Role, Page[]> = {
  aluno: [
    "inicio",
    "calendario",
    "metas",
    "atividades",
    "evolucao",
    "estudos",
    "ajuda",
    "configuracoes",
  ],
  professor: [
    "inicio",
    "calendario",
    "metas",
    "revisoes",
    "turmas",
    "materiais",
    "ajuda",
    "configuracoes",
  ],
  gestor: [
    "inicio",
    "calendario",
    "metas",
    "revisoes",
    "turmas",
    "equipe",
    "painel",
    "logs",
    "ajuda",
    "configuracoes",
  ],
  admin: ["inicio", "calendario", "escolas", "logs", "ajuda", "configuracoes"],
};
export function readRoute(hash: string) {
  const [rawRole, rawPage, rawId] = hash.replace(/^#\/?/, "").split("/");
  const role: Role =
    rawRole === "professor" || rawRole === "gestor" || rawRole === "admin"
      ? rawRole
      : "aluno";
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
