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
    throw new ApiError(mensagemDeErro(body?.detail));
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

// 422 do FastAPI vem como lista de {loc, type, ctx}; vira uma frase dizendo QUAL campo falhou
const CAMPOS: Record<string, string> = {
  enunciado: "enunciado", resposta_correta: "resposta correta", titulo: "título", nome: "nome",
  email: "email", senha: "senha", texto: "texto", cnpj: "CNPJ",
};
function mensagemDeErro(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]) {
    const { loc = [], type = "", ctx = {} } = detail[0] as { loc?: (string | number)[]; type?: string; ctx?: { max_length?: number; min_length?: number } };
    const nums = loc.filter((p): p is number => typeof p === "number");
    const campo = CAMPOS[String(loc[loc.length - 1])] ?? String(loc[loc.length - 1] ?? "campo");
    const onde = nums.length ? `Questão ${nums[0] + 1}: ` : "";
    if (type === "string_too_long") return `${onde}${campo} longo demais (máximo ${ctx.max_length} caracteres).`;
    if (type === "string_too_short") return `${onde}${campo} é obrigatório.`;
    const msg = (detail[0] as { msg?: string }).msg;
    if (type === "value_error" && msg) return msg.replace(/^Value error, /, "");
    return `${onde}${campo} está inválido.`;
  }
  return "Não foi possível completar a ação.";
}

export interface UsuarioAtual {
  id: string;
  nome: string;
  email: string;
  perfil: "ALUNO" | "PROFESSOR" | "GESTOR" | "ADMIN";
  escola_nome: string;
  ativo?: boolean;
  turmas?: string[]; // nomes das turmas (lista de pessoas)
}

// uma turma da pessoa; no professor, as materias que ele leciona NESTA turma
export interface VinculoTurmaAPI {
  turma_id: string;
  materia_ids: string[];
}

export function perfilParaRole(perfil: UsuarioAtual["perfil"]): Role {
  if (perfil === "PROFESSOR") return "professor";
  if (perfil === "GESTOR") return "gestor";
  if (perfil === "ADMIN") return "admin";
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
  tem_imagem?: boolean; // figura do enunciado anexada pelo professor
  alternativas?: string[] | null; // objetiva (estilo ENEM): textos de A, B, C...; o gabarito e so a letra
  resposta_correta?: string | null; // so professor/gestor recebem o gabarito
}

export interface AtividadeAPI {
  id: string;
  titulo: string;
  turma: string;
  turma_id: string;
  materia: string;
  tipo: "REDACAO" | "PROVA_DISCURSIVA" | "PROVA_OBJETIVA" | "EXERCICIO";
  alunos: { id: string; nome: string }[];
  // so vem preenchido para materias de exatas (gabarito fica so com o professor)
  questoes: QuestaoAtividadeAPI[] | null;
  // pontuacao total da atividade; em exatas e dividida igualmente entre as questoes. Sempre
  // 1000 na redacao (5 competencias x 0..200).
  valor_total: number;
  prazo: string | null; // AAAA-MM-DD
  na_minha_revisao: boolean; // professor: so as que ele propos (ou antigas, sem autor)
  tem_envios: boolean; // com envios: so titulo e prazo mudam, e excluir vira arquivar
}

export interface CaixaAPI {
  pagina?: number; // qual foto (0 = primeira), quando o aluno enviou varias
  x: number;
  y: number;
  largura: number;
  altura: number;
}

export interface PontoAPI {
  trecho: string;
  tipo: "acerto" | "erro";
  comentario: string;
  caixa: CaixaAPI | null;
}

export interface CriterioAPI {
  codigo: string;
  nome: string;
  nota: number;
  nota_professor: number | null;
  justificativa: string;
  pontos: PontoAPI[];
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

// escolaId: so o administrador informa (gestor e professor veem as proprias turmas)
export function listarTurmasMinhas(escolaId?: string): Promise<TurmaAPI[]> {
  return request<TurmaAPI[]>(`/turmas/minhas${escolaId ? `?escola_id=${escolaId}` : ""}`);
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

// escolaId: so o administrador informa (gestor e professor sempre veem a propria escola)
export function listarUsuarios(escolaId?: string): Promise<UsuarioAtual[]> {
  return request<UsuarioAtual[]>(`/usuarios${escolaId ? `?escola_id=${escolaId}` : ""}`);
}

export function editarUsuario(id: string, nome: string, email: string): Promise<UsuarioAtual> {
  return request<UsuarioAtual>(`/usuarios/${id}`, { method: "PUT", body: JSON.stringify({ nome, email }) });
}

// o gestor define a senha nova e passa para a pessoa; confirma a propria senha (cabecalho, nunca na URL)
export function trocarSenhaUsuario(id: string, senha: string, minhaSenha: string): Promise<void> {
  return request<void>(`/usuarios/${id}/senha`, {
    method: "PUT", body: JSON.stringify({ senha }), headers: { "X-Confirmar-Senha": minhaSenha },
  });
}

export function ativarUsuario(id: string, ativo: boolean): Promise<UsuarioAtual> {
  return request<UsuarioAtual>(`/usuarios/${id}/ativo`, { method: "PUT", body: JSON.stringify({ ativo }) });
}

export function vinculosDoUsuario(id: string): Promise<{ turmas: VinculoTurmaAPI[] }> {
  return request<{ turmas: VinculoTurmaAPI[] }>(`/usuarios/${id}/vinculos`);
}

export function definirVinculos(id: string, turmas: VinculoTurmaAPI[]): Promise<{ turmas: VinculoTurmaAPI[] }> {
  return request<{ turmas: VinculoTurmaAPI[] }>(`/usuarios/${id}/vinculos`, { method: "PUT", body: JSON.stringify({ turmas }) });
}

export function criarUsuario(payload: {
  nome: string;
  email: string;
  senha: string;
  perfil: "ALUNO" | "PROFESSOR" | "GESTOR";
  escola_id?: string;
  turma_id?: string; // ja matricula na turma ao criar
  turmas?: VinculoTurmaAPI[]; // varias turmas (e materias por turma, no professor)
}, confirmarSenha?: string): Promise<UsuarioAtual> {
  // criar GESTOR exige a senha de novo (reautenticacao), enviada em cabecalho e nunca na URL
  return request<UsuarioAtual>("/usuarios", {
    method: "POST", body: JSON.stringify(payload),
    headers: confirmarSenha ? { "X-Confirmar-Senha": confirmarSenha } : undefined,
  });
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

// varias turmas de uma vez: o backend cria uma atividade independente por turma (tudo ou nada)
export function criarAtividadesLote(payload: {
  materia_id: string;
  turma_ids: string[];
  titulo: string;
  tipo: AtividadeAPI["tipo"];
  questoes?: { enunciado: string; resposta_correta: string; alternativas?: string[] }[];
  valor_total?: number;
  prazo?: string;
}): Promise<AtividadeAPI[]> {
  return request<AtividadeAPI[]>("/atividades/lote", { method: "POST", body: JSON.stringify(payload) });
}

export function editarAtividade(id: string, payload: {
  titulo?: string;
  prazo?: string | null; // null limpa o prazo
  valor_total?: number;
  questoes?: { enunciado: string; resposta_correta: string; alternativas?: string[] }[];
}): Promise<AtividadeAPI> {
  return request<AtividadeAPI>(`/atividades/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

// "excluida" (sem envios) ou "arquivada" (com envios: some da lista, notas continuam)
export function excluirAtividade(id: string): Promise<{ acao: "excluida" | "arquivada" }> {
  return request(`/atividades/${id}`, { method: "DELETE" });
}

export function criarAtividade(payload: {
  materia_id: string;
  turma_id: string;
  titulo: string;
  tipo: AtividadeAPI["tipo"];
  questoes?: { enunciado: string; resposta_correta: string }[];
  valor_total?: number;
  prazo?: string;
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

// prova/exercicio objetivo: o aluno marca a letra e a correcao sai na hora (sem IA)
export function enviarObjetiva(atividadeId: string, respostas: Record<string, string>): Promise<unknown> {
  return request("/submissoes/objetiva", {
    method: "POST",
    body: JSON.stringify({ atividade_id: atividadeId, respostas }),
  });
}

export interface SubmissaoRevisaoAPI {
  id: string;
  atividade_id: string;
  atividade_titulo: string;
  materia: string;
  aluno_id: string;
  aluno_nome: string;
  turma_id: string;
  turma_nome: string;
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
export async function urlImagemSubmissao(id: string, pagina = 0): Promise<string> {
  const token = getToken();
  const response = await fetch(`${API_URL}/submissoes/${id}/imagem?pagina=${pagina}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new ApiError("Não foi possível carregar a foto.");
  return URL.createObjectURL(await response.blob());
}

// figura de uma questao (ex.: estruturas quimicas): o professor anexa; aluno e professor veem
export function anexarFiguraQuestao(atividadeId: string, codigo: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);
  return request<void>(`/atividades/${atividadeId}/questoes/${codigo}/imagem`, { method: "POST", body: formData });
}

export async function urlFiguraQuestao(atividadeId: string, codigo: string): Promise<string> {
  const token = getToken();
  const response = await fetch(`${API_URL}/atividades/${atividadeId}/questoes/${codigo}/imagem`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new ApiError("Não foi possível carregar a figura.");
  return URL.createObjectURL(await response.blob());
}

// varias fotos do mesmo trabalho, na ordem: o backend le todas numa chamada so e junta o texto
export function enviarImagem(atividadeId: string, files: File[]): Promise<SubmissaoAPI> {
  const formData = new FormData();
  formData.append("atividade_id", atividadeId);
  files.forEach((f) => formData.append("files", f));
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
  avaliacao_ia: "BOA" | "MA" | null; // BOA = exemplo modelo; MA = explicação ruim (só a IA usa)
}

// o que da memória do professor a IA usou numa correção (só professor/gestor veem)
export interface FontesIAAPI {
  fontes: { tipo: "material" | "instrucao" | "exemplo"; titulo: string; trecho: string }[];
  aviso: string | null; // a IA tem concordado pouco com este professor nesta matéria
}

export function verFontesIA(submissaoId: string): Promise<FontesIAAPI> {
  return request<FontesIAAPI>(`/submissoes/${submissaoId}/fontes-ia`);
}

export function corrigirSubmissao(id: string, tema?: string): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/corrigir`, {
    method: "POST",
    body: JSON.stringify({ tema: tema ?? null }),
  });
}

export interface PassoAgenteAPI {
  tipo: "pensamento" | "ferramenta" | "aviso";
  texto?: string;
  ferramenta?: string;
  motivo?: string;
  resultado?: string;
  erro?: boolean;
}

export interface AgenteAPI {
  passos: PassoAgenteAPI[];
  mensagem_aluno: string | null;
  resumo_professor: string | null;
  exercicios: { habilidade_codigo: string; titulo: string }[] | null;
  modelo_usado: string;
  correcao: CorrecaoAPI | null;
}

// agente de correcao (backend/app/agente.py): o Claude decide os passos e usa as IAs como ferramentas
export function rodarAgente(id: string, tema?: string): Promise<AgenteAPI> {
  return request<AgenteAPI>(`/submissoes/${id}/agente`, {
    method: "POST",
    body: JSON.stringify({ tema: tema ?? null }),
  });
}

export function verAgente(id: string): Promise<AgenteAPI> {
  return request<AgenteAPI>(`/submissoes/${id}/agente`);
}

export function verCorrecao(id: string): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/correcao`);
}

export function aprovarCorrecao(
  id: string,
  notas: { codigo: string; nota: number }[],
  feedback: string,
  motivoMudanca?: string, // por que o professor mudou a nota da IA (só a IA usa, para aprender)
  avaliacaoIA: "BOA" | "MA" | null = null, // 1 clique: boa correção (modelo) ou explicação ruim, sem mudar a nota
): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/aprovar`, {
    method: "PUT",
    body: JSON.stringify({ notas, feedback, motivo_mudanca: motivoMudanca?.trim() || null, explicacao_ruim: avaliacaoIA === "MA", boa_correcao: avaliacaoIA === "BOA" }),
  });
}

export function avaliarIA(id: string, avaliacao: "BOA" | "MA" | null): Promise<CorrecaoAPI> {
  return request<CorrecaoAPI>(`/submissoes/${id}/avaliacao-ia`, { method: "PUT", body: JSON.stringify({ avaliacao }) });
}

export interface DominioAPI {
  tema_id: string;
  tema: string;
  materia: string;
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

// professor: so as materias que ele leciona nas turmas do aluno; gestor: todas
export function evolucaoDoAluno(alunoId: string): Promise<EvolucaoMateriaAPI[]> {
  return request<EvolucaoMateriaAPI[]>(`/alunos/${alunoId}/evolucao`);
}

export interface ProfessorMateriaAPI {
  professor_id: string;
  materia_id: string;
}

// quem leciona qual materia na turma (o gestor define; o professor ve so as dele)
export function materiasDosProfessores(turmaId: string): Promise<ProfessorMateriaAPI[]> {
  return request<ProfessorMateriaAPI[]>(`/turmas/${turmaId}/materias-dos-professores`);
}

export function definirMateriasDoProfessor(turmaId: string, professorId: string, materiaIds: string[]): Promise<ProfessorMateriaAPI[]> {
  return request<ProfessorMateriaAPI[]>(`/turmas/${turmaId}/professores/${professorId}/materias`, {
    method: "PUT", body: JSON.stringify({ materia_ids: materiaIds }),
  });
}

// exercicio de pratica SEM gabarito: o servidor confere quando o aluno responde
export interface ExercicioAPI {
  id: string;
  habilidade_codigo: string; // vazio nos de exatas
  materia?: string | null;
  motivo?: string | null; // exatas: o erro da correcao que originou o exercicio
  titulo: string;
  enunciado: string;
  opcoes: string[];
  // so vem depois que o aluno respondeu (antes disso o servidor nao manda o gabarito)
  respondida?: number;
  correta?: boolean;
  resposta_correta?: number;
  explicacao?: string;
}

export interface ResultadoRespostaAPI {
  correta: boolean;
  resposta_correta: number;
  explicacao: string;
}

// devolve os exercicios ainda nao respondidos; o servidor so gera novos quando acabam
export function meusExercicios(): Promise<ExercicioAPI[]> {
  return request<ExercicioAPI[]>("/estudos/meu");
}

// unica chamada que usa a IA: so quando o aluno clica em gerar
export function gerarMeusExercicios(): Promise<ExercicioAPI[]> {
  return request<ExercicioAPI[]>("/estudos/meu/gerar", { method: "POST" });
}

export function responderPratica(id: string, opcao: number): Promise<ResultadoRespostaAPI> {
  return request<ResultadoRespostaAPI>(`/estudos/exercicios/${id}/responder`, { method: "POST", body: JSON.stringify({ opcao }) });
}

export interface PraticaAPI {
  habilidade_codigo: string;
  respondidos: number;
  acertos: number;
}

export function minhaPratica(): Promise<PraticaAPI[]> {
  return request<PraticaAPI[]>("/estudos/minha-pratica");
}

// ---- exercicios de pratica do professor (a mao ou com ajuda da IA); nao valem nota ----
export type TipoExercicioAPI = "OBJETIVO" | "DISCURSIVO";

export interface ExercicioPayload {
  titulo: string;
  assunto: string;
  materia_id: string;
  turma_id: string;
  aluno_ids?: string[] | null; // so estes alunos da turma; nulo = turma toda
  tipo: TipoExercicioAPI;
  enunciado: string;
  alternativas?: string[] | null;
  resposta_correta?: number | null;
  resposta_exemplo?: string | null;
  respostas_exemplo?: string[] | null;
  explicacao?: string | null;
  gerado_por_ia: boolean;
}

export interface ExercicioProfessorAPI extends Required<Omit<ExercicioPayload, "alternativas" | "resposta_correta" | "resposta_exemplo" | "respostas_exemplo" | "explicacao" | "aluno_ids">> {
  respostas_exemplo: string[];
  aluno_ids: string[] | null;
  alunos_nomes: string[];
  id: string;
  materia_nome: string;
  turma_nome: string;
  alternativas: string[] | null;
  resposta_correta: number | null;
  resposta_exemplo: string | null;
  explicacao: string | null;
  criado_em: string | null;
  respostas: number;
  acertos: number;
  alunos_alvo: number;
}

export interface ExercicioAlunoAPI {
  id: string;
  titulo: string;
  assunto: string;
  materia_nome: string;
  professor_nome: string;
  tipo: TipoExercicioAPI;
  enunciado: string;
  alternativas: string[] | null;
  gerado_por_ia: boolean;
  criado_em: string | null;
  minha_resposta: string | null;
  correta: boolean | null;
  resultado: ResultadoAPI | null;
  comentario: string | null;
  resposta_correta: number | null;
  resposta_exemplo: string | null;
  respostas_exemplo: string[];
  explicacao: string | null;
}

export interface SugestaoExercicioAPI {
  titulo: string;
  enunciado: string;
  alternativas: string[];
  resposta_correta: number | null;
  resposta_exemplo: string | null;
  explicacao: string;
}

export function listarExerciciosProfessor(): Promise<ExercicioProfessorAPI[]> {
  return request<ExercicioProfessorAPI[]>("/exercicios");
}
export function criarExercicio(p: ExercicioPayload): Promise<ExercicioProfessorAPI> {
  return request<ExercicioProfessorAPI>("/exercicios", { method: "POST", body: JSON.stringify(p) });
}
export function criarExerciciosLote(p: ExercicioPayload & { turma_ids: string[] }): Promise<ExercicioProfessorAPI[]> {
  return request<ExercicioProfessorAPI[]>("/exercicios/lote", { method: "POST", body: JSON.stringify(p) });
}
export type ResultadoAPI = "CERTA" | "PARCIAL" | "ERRADA";
export interface RespostaAlunoAPI {
  aluno_id: string;
  nome: string;
  fez: boolean;
  resposta: string | null;
  correta: boolean | null;
  resultado: ResultadoAPI | null;
  comentario: string | null;
  respondido_em: string | null;
}
export interface ResumoAlunoAPI {
  aluno_id: string;
  nome: string;
  total: number;
  feitos: number;
  acertos: number;
  parciais: number;
  corrigidos: number;
}
export function respostasDoExercicio(id: string): Promise<RespostaAlunoAPI[]> {
  return request<RespostaAlunoAPI[]>(`/exercicios/${id}/respostas`);
}
export function avaliarRespostaExercicio(id: string, alunoId: string, p: { resultado?: ResultadoAPI | null; comentario?: string | null }): Promise<RespostaAlunoAPI> {
  return request<RespostaAlunoAPI>(`/exercicios/${id}/respostas/${alunoId}`, { method: "PUT", body: JSON.stringify(p) });
}
export function resumoExerciciosTurma(turmaId: string): Promise<ResumoAlunoAPI[]> {
  return request<ResumoAlunoAPI[]>(`/exercicios/resumo?turma_id=${turmaId}`);
}
export function editarExercicio(id: string, p: ExercicioPayload): Promise<ExercicioProfessorAPI> {
  return request<ExercicioProfessorAPI>(`/exercicios/${id}`, { method: "PUT", body: JSON.stringify(p) });
}
export function excluirExercicio(id: string): Promise<void> {
  return request<void>(`/exercicios/${id}`, { method: "DELETE" });
}
export function sugerirExercicios(p: {
  materia_id: string; assunto: string; tipo: TipoExercicioAPI; quantidade: number; instrucoes?: string;
}): Promise<SugestaoExercicioAPI[]> {
  return request<SugestaoExercicioAPI[]>("/exercicios/sugerir", { method: "POST", body: JSON.stringify(p) });
}
export function sugerirRespostaExemplo(p: {
  materia_id: string; assunto?: string; enunciado: string;
}): Promise<{ resposta_exemplo: string }> {
  return request<{ resposta_exemplo: string }>("/exercicios/sugerir-resposta", { method: "POST", body: JSON.stringify(p) });
}
export function exerciciosDaTurma(): Promise<ExercicioAlunoAPI[]> {
  return request<ExercicioAlunoAPI[]>("/exercicios/turma");
}
export function responderExercicio(id: string, resposta: string): Promise<ExercicioAlunoAPI> {
  return request<ExercicioAlunoAPI>(`/exercicios/${id}/responder`, { method: "POST", body: JSON.stringify({ resposta }) });
}

export function dominioDoAluno(alunoId: string): Promise<DominioAPI[]> {
  return request<DominioAPI[]>(`/alunos/${alunoId}/dominio`);
}

export interface DocumentoAPI {
  id: string;
  materia_id: string;
  materia_nome: string;
  nome_arquivo: string;
  tipo: "APOSTILA" | "RUBRICA" | "PLANO_DE_AULA" | "GABARITO";
  status_processamento: "PENDENTE" | "PROCESSADO" | "ERRO" | "FALHOU";
  detalhe?: string | null; // motivo quando a IA não conseguiu ler o arquivo
  tamanho_bytes: number | null;
  enviado_por_nome: string;
  pode_baixar: boolean;
  criado_em: string;
}

// professor: so os que ele enviou; gestor: os da escola toda
export function listarDocumentos(): Promise<DocumentoAPI[]> {
  return request<DocumentoAPI[]>("/documentos");
}

export function excluirDocumento(id: string): Promise<void> {
  return request<void>(`/documentos/${id}`, { method: "DELETE" });
}

// o arquivo exige o token, entao baixamos como blob e disparamos o download local
export async function baixarDocumento(id: string, nome: string): Promise<void> {
  const token = getToken();
  const response = await fetch(`${API_URL}/documentos/${id}/arquivo`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new ApiError("O arquivo deste material não está disponível.");
  const url = URL.createObjectURL(await response.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  a.click();
  URL.revokeObjectURL(url);
}

// quanto a IA já aprendeu com este professor numa matéria
export interface MemoriaIAAPI {
  trechos_de_material: number;
  correcoes_aprendidas: number;
  instrucoes: number;
  revisadas: number;
  iguais: number;
  proximas: number;
  longe: number;
  concordancia: number | null; // % de notas iguais ou próximas às suas
  concordancia_recente: number | null; // só das últimas 20
  exercicios_aprendidos: number;
  vies: number | null; // média de (sua nota - nota da IA) em %; negativo = você é mais rigoroso que a IA
  nivel: "SEM_TREINO" | "APRENDENDO" | "QUASE" | "PRONTA";
  falta: string[]; // o que ainda falta para a IA ficar pronta
  evolucao: { ate: number; concordancia: number }[]; // concordância a cada 10 revisadas, da mais antiga à mais nova
}

// onde a IA mais errou segundo o professor
export interface ErroDaIAAPI {
  submissao_id: string;
  atividade: string;
  nota_ia: number;
  nota_professor: number | null;
  motivo: string | null;
  explicacao_ruim: boolean;
}

export function listarErrosDaIA(materiaId: string): Promise<ErroDaIAAPI[]> {
  return request<ErroDaIAAPI[]>(`/materias/${materiaId}/erros-da-ia`);
}

// instruções escritas pelo professor para a IA ("sempre faça tal coisa"); valem sempre naquela matéria
export interface InstrucaoAPI {
  id: string;
  materia_id: string;
  texto: string;
  criado_em: string;
}

export function listarInstrucoes(materiaId: string): Promise<InstrucaoAPI[]> {
  return request<InstrucaoAPI[]>(`/materias/${materiaId}/instrucoes`);
}

export function criarInstrucao(materiaId: string, texto: string): Promise<InstrucaoAPI> {
  return request<InstrucaoAPI>(`/materias/${materiaId}/instrucoes`, { method: "POST", body: JSON.stringify({ texto }) });
}

export function excluirInstrucao(materiaId: string, id: string): Promise<void> {
  return request<void>(`/materias/${materiaId}/instrucoes/${id}`, { method: "DELETE" });
}

// a IA sugere virar instrução um motivo que o professor deu várias vezes ao mudar a nota
export interface SugestaoInstrucaoAPI {
  texto: string;
  vezes: number;
  correcao_ids: string[];
}

export function listarSugestoesInstrucao(materiaId: string): Promise<SugestaoInstrucaoAPI[]> {
  return request<SugestaoInstrucaoAPI[]>(`/materias/${materiaId}/sugestoes-instrucoes`);
}

export function dispensarSugestaoInstrucao(materiaId: string, correcaoIds: string[]): Promise<void> {
  return request<void>(`/materias/${materiaId}/sugestoes-instrucoes/dispensar`, {
    method: "POST",
    body: JSON.stringify({ correcao_ids: correcaoIds }),
  });
}

export function verMemoriaIA(materiaId: string): Promise<MemoriaIAAPI> {
  return request<MemoriaIAAPI>(`/materias/${materiaId}/ia`);
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

export interface EscolaAPI {
  id: string;
  nome: string;
  cnpj: string;
  ativa: boolean;
  plano_fixo: number;
  valor_por_aluno: number;
  criado_em: string;
}

export function listarEscolas(): Promise<EscolaAPI[]> {
  return request<EscolaAPI[]>("/escolas");
}

export function criarEscola(payload: {
  nome: string;
  cnpj: string;
  plano_fixo: number;
  valor_por_aluno: number;
}): Promise<EscolaAPI> {
  return request<EscolaAPI>("/escolas", { method: "POST", body: JSON.stringify(payload) });
}

export function editarEscola(
  id: string,
  payload: Partial<Pick<EscolaAPI, "nome" | "cnpj" | "plano_fixo" | "valor_por_aluno" | "ativa">>,
  confirmarSenha?: string, // desativar/reativar exige a senha de novo
): Promise<EscolaAPI> {
  return request<EscolaAPI>(`/escolas/${id}`, {
    method: "PUT", body: JSON.stringify(payload),
    headers: confirmarSenha ? { "X-Confirmar-Senha": confirmarSenha } : undefined,
  });
}

export interface ResumoEscolaAPI {
  escola_id: string;
  escola_nome: string;
  ativa: boolean;
  mes: string;
  alunos_cadastrados: number;
  professores: number;
  turmas: number;
  alunos_ativos: number;
  submissoes: number;
  execucoes_agente: number;
  tokens_llm: number;
  chamadas_ocr: number;
  armazenamento_bytes: number;
  receita: number;
  custo_ia: number;
  margem: number;
}

export interface ResumoPlataformaAPI {
  mes: string;
  escolas_ativas: number;
  totais: Record<string, number>;
  escolas: ResumoEscolaAPI[];
}

// gestor: sem escolaId (o backend usa a escola dele). admin: escolaId obrigatorio.
export function painelEscola(mes: string, escolaId?: string): Promise<ResumoEscolaAPI> {
  const q = new URLSearchParams({ mes });
  if (escolaId) q.set("escola_id", escolaId);
  return request<ResumoEscolaAPI>(`/painel/escola?${q}`);
}

export function painelPlataforma(mes: string): Promise<ResumoPlataformaAPI> {
  return request<ResumoPlataformaAPI>(`/painel/plataforma?mes=${mes}`);
}

// ---- calendario (um so por escola; o backend filtra pelo perfil) ----
export interface ItemCalendarioAPI {
  id: string; // "evento:<uuid>" | "prazo:<uuid>" | "meta:<uuid>" | "feriado:<data>"
  origem: "evento" | "prazo" | "meta" | "feriado";
  titulo: string;
  descricao: string | null;
  tipo: string;
  inicio: string; // AAAA-MM-DD
  fim: string | null;
  turma_id: string | null;
  turma: string | null;
  editavel: boolean;
}
export interface EventoPayload {
  titulo: string;
  descricao?: string;
  tipo: "PROVA" | "ENTREGA" | "REUNIAO" | "AVISO";
  inicio: string;
  fim?: string | null;
  turma_id?: string | null;
}

export function listarCalendario(de: string, ate: string, escolaId?: string): Promise<ItemCalendarioAPI[]> {
  const q = new URLSearchParams({ de, ate, ...(escolaId ? { escola_id: escolaId } : {}) });
  return request<ItemCalendarioAPI[]>(`/calendario?${q}`);
}
export function criarEvento(p: EventoPayload, escolaId?: string): Promise<ItemCalendarioAPI> {
  return request<ItemCalendarioAPI>(`/eventos${escolaId ? `?escola_id=${escolaId}` : ""}`, { method: "POST", body: JSON.stringify(p) });
}
export function editarEvento(id: string, p: EventoPayload): Promise<ItemCalendarioAPI> {
  return request<ItemCalendarioAPI>(`/eventos/${id.replace("evento:", "")}`, { method: "PUT", body: JSON.stringify(p) });
}
export function apagarEvento(id: string): Promise<void> {
  return request<void>(`/eventos/${id.replace("evento:", "")}`, { method: "DELETE" });
}

// ---- logs (admin: tudo; gestor: so a auditoria da propria escola) ----
export interface EventoSegurancaAPI {
  seq: number | null; criado_em: string; tipo: string; usuario: string | null;
  email_tentado: string | null; ip: string; request_id: string; detalhe: string | null;
}
export interface AuditoriaAPI {
  seq: number | null; criado_em: string; usuario: string | null; escola: string | null; acao: string;
  entidade: string; entidade_id: string; resultado: string | null; ip: string | null; request_id: string | null;
}
export interface IntegridadeAPI { seguranca_ok: boolean; seguranca: string; auditoria_ok: boolean; auditoria: string }
export interface FiltroLog { tipo?: string; acao?: string; ip?: string; de?: string; ate?: string; pular?: number }

const consulta = (f: FiltroLog) =>
  new URLSearchParams(Object.entries({ limite: 50, ...f }).filter(([, v]) => v !== undefined && v !== "") as [string, string][]);
export const logsSeguranca = (f: FiltroLog) => request<EventoSegurancaAPI[]>(`/logs/seguranca?${consulta(f)}`);
export const logsAuditoria = (f: FiltroLog) => request<AuditoriaAPI[]>(`/logs/auditoria?${consulta(f)}`);
export const logsIntegridade = () => request<IntegridadeAPI>("/logs/integridade");


// ---- niveis e metas ----
export type TipoMetaAPI = "ENTREGAS" | "ENTREGAS_NO_PRAZO" | "NOTA_ATIVIDADE" | "MEDIA_MATERIA" | "DOMINIO_COMPETENCIA"
  | "PRATICA_RESPONDIDOS" | "PRATICA_ACERTOS";

export interface MetaPayload {
  titulo: string;
  descricao?: string;
  tipo: TipoMetaAPI;
  alvo: number;
  materia_id?: string;
  competencia?: string;
  pontos: number;
  inicio?: string;
  fim?: string;
  turma_id?: string; // aluno_id = individual; turma_id = turma; nenhum = escola toda (so gestor)
  aluno_id?: string;
}

export interface MetaAPI extends Omit<MetaPayload, "turma_id" | "aluno_id" | "inicio" | "fim" | "descricao"> {
  id: string;
  descricao: string | null;
  inicio: string;
  fim: string | null;
  escopo: "ESCOLA" | "TURMA" | "ALUNO";
  escopo_nome: string;
  alunos_alvo: number;
  concluidos: number;
  pode_editar: boolean;
}

export interface NivelAPI {
  nivel: number;
  nome: string;
  pontos: number;
  pontos_nivel_atual: number;
  pontos_proximo: number | null;
}

export interface MetaAlunoAPI {
  id: string;
  titulo: string;
  descricao: string | null;
  tipo: TipoMetaAPI;
  alvo: number;
  progresso: number;
  pontos: number;
  inicio: string;
  fim: string | null;
  status: "FUTURA" | "EM_ANDAMENTO" | "CONCLUIDA" | "ENCERRADA";
  concluida_em: string | null;
}

export interface RankingItemAPI {
  aluno_id: string;
  nome: string;
  pontos: number;
  nivel: number;
  nome_nivel: string;
  metas_concluidas: number;
}

export const criarMeta = (p: MetaPayload) => request<MetaAPI>("/metas", { method: "POST", body: JSON.stringify(p) });
export const listarMetas = () => request<MetaAPI[]>("/metas");
// alvo/pontos so mudam enquanto ninguem concluiu a meta (o servidor responde 409 depois); fim null tira o fim
export const editarMeta = (id: string, p: { titulo?: string; descricao?: string | null; fim?: string | null; alvo?: number; pontos?: number }) =>
  request<MetaAPI>(`/metas/${id}`, { method: "PUT", body: JSON.stringify(p) });
export const arquivarMeta = (id: string) => request<void>(`/metas/${id}`, { method: "DELETE" });
export const minhasMetas = () => request<{ nivel: NivelAPI; metas: MetaAlunoAPI[] }>("/metas/minhas");
export const rankingMetas = (turmaId?: string) =>
  request<RankingItemAPI[]>(`/metas/ranking${turmaId ? `?turma_id=${turmaId}` : ""}`);

// o que a IA aprendeu com o professor; "esquecer" = tirar de uso (nada é apagado)
export interface ItemAprendidoAPI {
  tipo: "CORRECAO" | "EXERCICIO";
  id: string;
  titulo: string;
  trecho: string;
  em_uso: boolean;
  erro: number;
}

export function listarAprendido(materiaId: string): Promise<ItemAprendidoAPI[]> {
  return request<ItemAprendidoAPI[]>(`/materias/${materiaId}/aprendido`);
}

export function usoDoItem(materiaId: string, item: ItemAprendidoAPI, emUso: boolean): Promise<void> {
  return request<void>(`/materias/${materiaId}/aprendido/${item.tipo}/${item.id}`, {
    method: "PUT",
    body: JSON.stringify({ em_uso: emUso }),
  });
}
