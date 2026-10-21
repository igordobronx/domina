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
      // FormData define seu proprio Content-Type (multipart + boundary); fixar aqui quebraria o upload
      ...(options.body && !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
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
  escola_nome: string;
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

export interface QuestaoAtividadeAPI {
  codigo: string;
  enunciado: string;
}

export interface AtividadeAPI {
  id: string;
  titulo: string;
  turma: string;
  materia: string;
  tipo: "REDACAO" | "PROVA_DISCURSIVA" | "PROVA_OBJETIVA" | "EXERCICIO";
  alunos: { id: string; nome: string }[];
  // so vem preenchido para materias de exatas (gabarito fica so com o professor)
  questoes: QuestaoAtividadeAPI[] | null;
  // pontuacao total da atividade; em exatas e dividida igualmente entre as questoes. Sempre
  // 1000 na redacao (5 competencias x 0..200).
  valor_total: number;
}

export interface CaixaAPI {
  x: number;
  y: number;
  largura: number;
  altura: number;
}

export interface CriterioAPI {
  codigo: string;
  nome: string;
  nota: number;
  nota_professor: number | null;
  justificativa: string;
  trecho: string | null;
  caixa: CaixaAPI | null;
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
  texto: string | null;
  tipo_envio: string;
}

export function listarAtividades(): Promise<AtividadeAPI[]> {
  return request<AtividadeAPI[]>("/atividades");
}

export interface TurmaAPI {
  id: string;
  nome: string;
  ano: number;
}

export function listarTurmasMinhas(): Promise<TurmaAPI[]> {
  return request<TurmaAPI[]>("/turmas/minhas");
}

export function criarTurma(payload: { nome: string; ano: number }): Promise<TurmaAPI> {
  return request<TurmaAPI>("/turmas", { method: "POST", body: JSON.stringify(payload) });
}

export interface MembroTurmaAPI {
  id: string;
  nome: string;
  email: string;
  papel: "ALUNO" | "PROFESSOR";
}

export function membrosTurma(turmaId: string): Promise<MembroTurmaAPI[]> {
  return request<MembroTurmaAPI[]>(`/turmas/${turmaId}/membros`);
}

export function matricular(
  turmaId: string,
  payload: { usuario_id: string; papel: "ALUNO" | "PROFESSOR" },
): Promise<TurmaAPI> {
  return request<TurmaAPI>(`/turmas/${turmaId}/matricular`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listarUsuarios(): Promise<UsuarioAtual[]> {
  return request<UsuarioAtual[]>("/usuarios");
}

export function criarUsuario(payload: {
  nome: string;
  email: string;
  senha: string;
  perfil: "ALUNO" | "PROFESSOR";
}): Promise<UsuarioAtual> {
  return request<UsuarioAtual>("/usuarios", { method: "POST", body: JSON.stringify(payload) });
}

export interface MateriaAPI {
  id: string;
  nome: string;
  tipo: "REDACAO_ENEM" | "REDACAO_OUTRO_VESTIBULAR" | "MATERIA_OBJETIVA" | "MATERIA_DISCURSIVA";
}

export function listarMaterias(): Promise<MateriaAPI[]> {
  return request<MateriaAPI[]>("/materias");
}

export function criarMateria(payload: {
  nome: string;
  tipo: MateriaAPI["tipo"];
}): Promise<MateriaAPI> {
  return request<MateriaAPI>("/materias", { method: "POST", body: JSON.stringify(payload) });
}

export function criarAtividade(payload: {
  materia_id: string;
  turma_id: string;
  titulo: string;
  tipo: AtividadeAPI["tipo"];
  questoes?: { enunciado: string; resposta_correta: string }[];
  valor_total?: number;
}): Promise<AtividadeAPI> {
  return request<AtividadeAPI>("/atividades", {
    method: "POST",
    body: JSON.stringify(payload),
  });
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

export interface SubmissaoRevisaoAPI {
  id: string;
  atividade_id: string;
  atividade_titulo: string;
  materia: string;
  aluno_id: string;
  aluno_nome: string;
  status: string;
  criado_em: string;
  nota: number | null;
  valor_total: number;
}

export function listarSubmissoesRevisao(): Promise<SubmissaoRevisaoAPI[]> {
  return request<SubmissaoRevisaoAPI[]>("/submissoes");
}

export interface SubmissaoAPI {
  id: string;
  atividade_id: string;
  aluno_id: string;
  tipo_envio: string;
  texto_ocr: string | null;
  texto_confirmado: string | null;
  criado_em: string;
}

export function verSubmissao(id: string): Promise<SubmissaoAPI> {
  return request<SubmissaoAPI>(`/submissoes/${id}`);
}

// a rota exige o Bearer token, entao nao da pra usar a URL direto num <img src>: busca como
// blob e devolve uma URL local (revogada pelo chamador quando nao precisar mais)
export async function urlImagemSubmissao(id: string): Promise<string> {
  const token = getToken();
  const response = await fetch(`${API_URL}/submissoes/${id}/imagem`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new ApiError("Não foi possível carregar a foto.");
  return URL.createObjectURL(await response.blob());
}

export function enviarImagem(atividadeId: string, file: File): Promise<SubmissaoAPI> {
  const formData = new FormData();
  formData.append("atividade_id", atividadeId);
  formData.append("file", file);
  return request<SubmissaoAPI>("/submissoes/imagem", { method: "POST", body: formData });
}

export function confirmarTexto(submissaoId: string, texto: string): Promise<SubmissaoAPI> {
  return request<SubmissaoAPI>(`/submissoes/${submissaoId}/confirmar`, {
    method: "PUT",
    body: JSON.stringify({ texto }),
  });
}

export interface CorrecaoAPI {
  id: string;
  submissao_id: string;
  nota_ia: number;
  nota_professor: number | null;
  confianca: number;
  status: string;
  feedback: string | null;
  criterios: CriterioAPI[];
}

export function corrigirSubmissao(id: string, tema?: string): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/corrigir`, {
    method: "POST",
    body: JSON.stringify({ tema: tema ?? null }),
  });
}

export function verCorrecao(id: string): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/correcao`);
}

export function aprovarCorrecao(
  id: string,
  notas: { codigo: string; nota: number }[],
  feedback: string,
): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/aprovar`, {
    method: "PUT",
    body: JSON.stringify({ notas, feedback }),
  });
}

export interface DominioAPI {
  tema_id: string;
  tema: string;
  habilidade_codigo: string;
  percentual_dominio: number;
  num_evidencias: number;
}

export function dominioMeu(): Promise<DominioAPI[]> {
  return request<DominioAPI[]>("/dominio/meu");
}

export interface EvolucaoPontoAPI {
  atividade_titulo: string;
  percentual: number;
  data: string;
}

export interface EvolucaoMateriaAPI {
  materia_id: string;
  materia: string;
  media_percentual: number;
  num_atividades: number;
  historico: EvolucaoPontoAPI[];
}

export function evolucaoMinha(): Promise<EvolucaoMateriaAPI[]> {
  return request<EvolucaoMateriaAPI[]>("/evolucao/minha");
}

export interface ExercicioAPI {
  habilidade_codigo: string;
  titulo: string;
  enunciado: string;
  opcoes: string[];
  resposta_correta: number;
  explicacao: string;
}

export function meusExercicios(recarregar = false): Promise<ExercicioAPI[]> {
  return request<ExercicioAPI[]>(`/estudos/meu${recarregar ? "?recarregar=true" : ""}`);
}

export function dominioDoAluno(alunoId: string): Promise<DominioAPI[]> {
  return request<DominioAPI[]>(`/alunos/${alunoId}/dominio`);
}

export interface DocumentoAPI {
  id: string;
  materia_id: string;
  nome_arquivo: string;
  tipo: "APOSTILA" | "RUBRICA" | "PLANO_DE_AULA" | "GABARITO";
  status_processamento: "PENDENTE" | "PROCESSADO" | "FALHOU";
}

export function listarDocumentos(materiaId: string): Promise<DocumentoAPI[]> {
  return request<DocumentoAPI[]>(`/materias/${materiaId}/documentos`);
}

export function enviarDocumento(
  materiaId: string,
  file: File,
  tipo: DocumentoAPI["tipo"],
): Promise<DocumentoAPI> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("tipo", tipo);
  return request<DocumentoAPI>(`/materias/${materiaId}/documentos`, { method: "POST", body: formData });
}

export interface ConsentimentoAPI {
  aluno_id: string;
  responsavel_nome: string;
  responsavel_email: string;
  aceito_em: string;
}

export function meuConsentimento(): Promise<ConsentimentoAPI> {
  return request<ConsentimentoAPI>("/consentimento/meu");
}

export function registrarConsentimento(payload: {
  responsavel_nome: string;
  responsavel_email: string;
}): Promise<ConsentimentoAPI> {
  return request<ConsentimentoAPI>("/consentimento", { method: "POST", body: JSON.stringify(payload) });
}

export interface CustoUsoAPI {
  mes_referencia: string;
  tokens_llm: number;
  chamadas_ocr: number;
  custo_estimado: number;
}

export function custoUso(): Promise<CustoUsoAPI> {
  return request<CustoUsoAPI>("/custo-uso");
}

export interface AuditLogAPI {
  id: string;
  usuario_id: string;
  acao: string;
  entidade: string;
  entidade_id: string;
  criado_em: string;
}

export function auditLog(): Promise<AuditLogAPI[]> {
  return request<AuditLogAPI[]>("/audit-log");
}
