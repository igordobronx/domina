import type { Role } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "domina.token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setToken(token: string) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // sem storage disponivel (ex.: navegador privado): segue so em memoria pela sessao
  }
}

export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // nada a fazer
  }
}

export class ApiError extends Error {}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : "Não foi possível completar a ação.";
    throw new ApiError(detail);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export interface UsuarioAtual {
  id: string;
  nome: string;
  email: string;
  perfil: "ALUNO" | "PROFESSOR" | "GESTOR" | "ADMIN";
}

export function perfilParaRole(perfil: UsuarioAtual["perfil"]): Role {
  if (perfil === "PROFESSOR") return "professor";
  if (perfil === "GESTOR" || perfil === "ADMIN") return "gestor";
  return "aluno";
}

export async function login(email: string, senha: string): Promise<UsuarioAtual> {
  const { access_token } = await request<{ access_token: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, senha }),
  });
  setToken(access_token);
  try {
    return await me();
  } catch (erro) {
    clearToken();
    throw erro;
  }
}

export function logout() {
  clearToken();
}

export function me(): Promise<UsuarioAtual> {
  return request<UsuarioAtual>("/usuarios/me");
}

export interface AtividadeAPI {
  id: string;
  titulo: string;
  turma: string;
  materia: string;
  tipo: "REDACAO" | "PROVA_DISCURSIVA" | "PROVA_OBJETIVA" | "EXERCICIO";
  alunos: { id: string; nome: string }[];
}

export interface CriterioAPI {
  codigo: string;
  nome: string;
  nota: number;
  nota_professor: number | null;
  justificativa: string;
}

export interface MinhaSubmissaoAPI {
  id: string;
  atividade_id: string;
  atividade_titulo: string;
  status: string;
  criado_em: string;
  nota: number | null;
  feedback: string | null;
  criterios: CriterioAPI[] | null;
}

export function listarAtividades(): Promise<AtividadeAPI[]> {
  return request<AtividadeAPI[]>("/atividades");
}

export function minhasSubmissoes(): Promise<MinhaSubmissaoAPI[]> {
  return request<MinhaSubmissaoAPI[]>("/submissoes/minhas");
}

export function enviarTexto(atividadeId: string, texto: string): Promise<unknown> {
  return request("/submissoes/texto", {
    method: "POST",
    body: JSON.stringify({ atividade_id: atividadeId, texto }),
  });
}
