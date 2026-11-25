import { Seletor, SeletorMultiplo, Escolha } from "../components/Seletor";
import { SeletorAssunto } from "../components/SeletorAssunto";
import { FotoComMarcas } from "../components/FotoComMarcas";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  ArrowLeft,
  ArrowUpRight,
  BookOpen,
  Check,
  FileText,
  Pencil,
  Plus,
  Search,
  Send,
  Sparkles,
  Trash2,
  Upload,
  ShieldCheck,
} from "lucide-react";
import { TextInput } from "react-native";
import { CampoComSimbolos } from "../components/CampoComSimbolos";
import { EditorQuestao, MAX_EXEMPLOS, vazio, type Rascunho } from "../components/EditorQuestao";
import { PontosSeletor } from "../components/PontosSeletor";
import { ActivityRow } from "./Dashboard";
import { Badge, Button, Card, Empty, Modal, SectionTitle } from "../components/ui";
import { Filtros } from "../components/Filtros";
import type { Activity, DemoState, Role } from "../types";
import {
  approveActivity,
  validScores,
  visibleResult,
} from "../services/demoStore";
import {
  aprovarCorrecao,
  sugerirRespostaExemplo,
  verCorrecaoManual,
  avaliarIA,
  confirmarTexto,
  anexarFiguraQuestao,
  criarAtividadesLote,
  editarAtividade,
  excluirAtividade,
  listarAtividades,
  enviarImagem,
  enviarTexto,
  enviarObjetiva,
  listarMaterias,
  listarTurmasMinhas,
  rodarAgente,
  sugerirExercicios,
  type SugestaoExercicioAPI,
  urlFiguraQuestao,
  urlImagemSubmissao,
  verAgente,
  verCorrecao,
  verFontesIA,
  type FontesIAAPI,
  verSubmissao,
  type AgenteAPI,
  type AtividadeAPI,
  type CorrecaoAPI,
  type MateriaAPI,
  type SubmissaoAPI,
  type TurmaAPI,
} from "../services/api";
import { carregarAtividadesDoAluno } from "../services/atividades";
import { carregarRevisoes, enviaram, paraRevisar, type GrupoAtividade } from "../services/revisoes";
import type { UsuarioAtual } from "../services/api";

type Ponto = {
  trecho: string;
  tipo: "acerto" | "erro";
  comentario: string;
  caixa: { pagina?: number; x: number; y: number; largura: number; altura: number } | null;
};

// achata os pontos (acertos/erros) de todos os criterios num unico array, com o codigo do
// criterio dono pra compor o tooltip (ex.: "C1 · erro: ...")
function todosOsPontos(criterios: { codigo: string; pontos: Ponto[] }[]) {
  return criterios.flatMap((c) => c.pontos.map((p) => ({ ...p, criterio: c.codigo })));
}

// so exatas por foto tem caixa (redacao sempre aponta no texto transcrito, nunca na imagem
// crua, mesmo quando o envio original foi uma foto) -- decide pela caixa existir de verdade,
// nao pelo tipo de envio, senao a redacao por foto mostraria a imagem crua sem destaque nenhum
function temCaixa(criterios: { codigo: string; pontos: Ponto[] }[]): boolean {
  return todosOsPontos(criterios).some((p) => p.caixa);
}

// destaca, no texto completo, o trecho de cada ponto (acerto em verde, erro em vermelho).
// match exato; se a IA citou algo que nao bate 100% com o texto (ruido de OCR, paragrafo
// levemente diferente) esse ponto simplesmente nao fica destacado, sem erro
function destacarTrechos(texto: string, criterios: { codigo: string; pontos: Ponto[] }[]): ReactNode[] {
  const achados = todosOsPontos(criterios)
    .map((p, i) => ({ ...p, i, trecho: p.trecho.trim() }))
    .filter((p) => p.trecho && texto.includes(p.trecho))
    .map((p) => ({ ...p, pos: texto.indexOf(p.trecho) }))
    .sort((a, b) => a.pos - b.pos);

  const partes: ReactNode[] = [];
  let cursor = 0;
  for (const p of achados) {
    if (p.pos < cursor) continue; // trechos sobrepostos: fica so com o primeiro encontrado
    partes.push(texto.slice(cursor, p.pos));
    partes.push(
      <mark
        key={p.i}
        className={`ponto ponto-${p.tipo}`}
        title={`${p.criterio} · ${p.tipo === "acerto" ? "acerto" : "erro"}: ${p.comentario}`}
      >
        {p.trecho}
      </mark>,
    );
    cursor = p.pos + p.trecho.length;
  }
  partes.push(texto.slice(cursor));
  return partes;
}

// O que o professor/aluno ve em "Texto enviado". Envio por foto: exatas mostra a FOTO com as marcas (da IA e do
// professor) e deixa o texto lido recolhido; redacao deixa escolher entre o texto transcrito e a foto marcavel.
function VisaoDoEnvio({ submissaoId, imagem, criterios, texto, editavel, notify, vazio }: {
  submissaoId?: string; imagem: boolean; criterios: { codigo: string; pontos: Ponto[] }[] | null | undefined;
  texto: string | null | undefined; editavel: boolean; notify: (m: string) => void; vazio?: ReactNode;
}) {
  const [modo, setModo] = useState<"texto" | "foto">("texto");
  const comoTexto = texto ? (criterios ? destacarTrechos(texto, criterios) : texto) : vazio;
  if (!imagem || !submissaoId) return <>{comoTexto}</>;
  const exatas = !!criterios?.some((c) => /^Q\d/.test(c.codigo));
  const foto = <FotoComMarcas submissaoId={submissaoId} pontos={criterios ? todosOsPontos(criterios) : []} editavel={editavel} notify={notify} />;
  if (exatas) {
    return (
      <>
        {foto}
        {texto && <details><summary>Ver o texto lido da foto</summary>{comoTexto}</details>}
      </>
    );
  }
  return (
    <>
      <div className="tabs" role="group" aria-label="Como ver o envio">
        <button aria-pressed={modo === "texto"} className={modo === "texto" ? "active" : ""} onClick={() => setModo("texto")}>Texto transcrito</button>
        <button aria-pressed={modo === "foto"} className={modo === "foto" ? "active" : ""} onClick={() => setModo("foto")}>Foto com marcações</button>
      </div>
      {modo === "foto" ? foto : comoTexto}
    </>
  );
}

type Props = {
  state: DemoState;
  role: Role;
  update: (fn: (s: DemoState) => DemoState) => void;
  notify: (s: string) => void;
  selected: string | null;
  select: (id: string | null) => void;
  reviewOnly?: boolean;
  initialFilter?: string; // "todas" | "disponivel" | "pendente" | "corrigida_ia" | "aprovada"
  currentUser?: UsuarioAtual | null;
};
export function Activities({
  state,
  role,
  update,
  notify,
  selected,
  select,
  reviewOnly,
  initialFilter = "todas",
  currentUser,
}: Props) {
  const [filtros, setFiltros] = useState<string[]>(initialFilter === "todas" ? [] : [initialFilter]); // status marcados; vazio = todos
  const [search, setSearch] = useState("");
  const [turmaFiltro, setTurmaFiltro] = useState(""); // nada pre-selecionado
  const [criando, setCriando] = useState(false);
  const [editandoId, setEditandoId] = useState<string | null>(null); // atividade em edicao (professor/gestor)
  // modo real: aluno autenticado de verdade manda/ve suas proprias atividades;
  // professor/gestor autenticado de verdade ve a fila real de submissoes (so o professor corrige/aprova, RN-01)
  const real = !!currentUser && role === "aluno";
  const realProfessor = !!currentUser && role === "professor" && !!reviewOnly;
  const realReviewer = !!currentUser && (role === "professor" || role === "gestor") && !!reviewOnly;
  const [realActivities, setRealActivities] = useState<Activity[] | null>(null);
  const [grupos, setGrupos] = useState<GrupoAtividade[]>([]); // fila de revisao: uma por atividade/turma
  const [grupoSel, setGrupoSel] = useState<string | null>(null); // atividade aberta (lista de alunos)
  const [loadingReal, setLoadingReal] = useState(real || realReviewer);
  const recarregar = () => {
    if (real && currentUser) {
      setLoadingReal(true);
      carregarAtividadesDoAluno(currentUser.nome)
        .then(setRealActivities)
        .catch(() => notify("Não foi possível carregar suas atividades."))
        .finally(() => setLoadingReal(false));
    } else if (realReviewer) {
      setLoadingReal(true);
      carregarRevisoes()
        .then(({ linhas, grupos }) => { setRealActivities(linhas); setGrupos(grupos); })
        .catch(() => notify("Não foi possível carregar a fila de revisão."))
        .finally(() => setLoadingReal(false));
    }
  };
  useEffect(recarregar, [real, realReviewer, currentUser?.id]);
  const activities = real || realReviewer ? (realActivities ?? []) : state.activities;
  const activity = activities.find((a) => a.id === selected);
  if ((real || realReviewer) && loadingReal && !activity)
    return (
      <Empty title="Carregando..." text="Buscando dados no servidor." />
    );
  const modalForm = realProfessor && criando ? (
    <Modal title="Nova atividade" largo onClose={() => setCriando(false)}>
      <NovaAtividade
        onBack={() => setCriando(false)}
        onCriada={() => { setCriando(false); recarregar(); }}
        notify={notify}
      />
    </Modal>
  ) : editandoId ? (
    <Modal title="Editar atividade" largo onClose={() => setEditandoId(null)}>
      <EditarAtividade
        atividadeId={editandoId}
        onBack={() => setEditandoId(null)}
        onSalvo={() => { setEditandoId(null); select(null); recarregar(); }}
        notify={notify}
      />
    </Modal>
  ) : null;
  if (activity && realReviewer)
    return (<>
      {modalForm}
      {activity.atividadeId && (
        <BarraAtividade
          atividadeId={activity.atividadeId}
          onEditar={() => setEditandoId(activity.atividadeId!)}
          onExcluida={() => { select(null); recarregar(); }}
          notify={notify}
        />
      )}
      {activity.status === "disponivel" ? (
      <AtividadeSemEnvio key={activity.id} activity={activity} onBack={() => select(null)} />
    ) : (
      <RevisaoReal
        key={activity.id}
        activity={activity}
        onBack={() => select(null)}
        onApproved={() => { select(null); recarregar(); }}
        readOnly={role === "gestor"}
        notify={notify}
      />
    )}
    </>);
  if (activity)
    return (
      <ActivityDetail
        key={activity.id + activity.status + (activity.scores ? "c" : "")}
        activity={activity}
        state={state}
        role={role}
        update={update}
        notify={notify}
        onBack={() => select(null)}
        onSubmittedReal={real ? () => { select(null); recarregar(); } : undefined}
        onCorrigidaReal={real ? recarregar : undefined}
      />
    );
  const grupo = grupos.find((g) => g.atividadeId === grupoSel);
  if (realReviewer && grupo)
    return (<>
      <BarraAtividade
        atividadeId={grupo.atividadeId}
        onEditar={() => setEditandoId(grupo.atividadeId)}
        onExcluida={() => { setGrupoSel(null); recarregar(); }}
        notify={notify}
      />
      <EnviosDaAtividade grupo={grupo} onBack={() => setGrupoSel(null)} abrir={(id) => select(id)} />
    </>);
  // turmas que aparecem na fila (professor com varias turmas ou gestor)
  const turmasFila = reviewOnly
    ? realReviewer
      ? [...new Map(grupos.map((g) => [g.turmaId, g.turmaNome])).entries()].sort((x, y) => x[1].localeCompare(y[1]))
      : [...new Map(activities.filter((a) => a.turmaId).map((a) => [a.turmaId!, a.turmaNome!])).entries()]
          .sort((x, y) => x[1].localeCompare(y[1]))
    : [];
  // filtro salvo de uma turma que nao esta mais na fila nao pode esconder tudo
  const turmaAtiva = turmasFila.some(([id]) => id === turmaFiltro) ? turmaFiltro : "";
  const list = activities
    .filter(
    (a) =>
      (!turmaAtiva || a.turmaId === turmaAtiva) &&
      (!filtros.length || filtros.includes(a.status)) &&
      `${a.title} ${a.subject} ${a.student}`.toLowerCase().includes(search.toLowerCase()),
    )
    .sort((x, y) => (role === "aluno"
      ? (y.enviadoEm ?? "").localeCompare(x.enviadoEm ?? "") // aluno: feitas do mais novo para o mais velho (as ainda não feitas ficam depois)
      : reviewOnly ? (x.turmaNome ?? "").localeCompare(y.turmaNome ?? "") || x.student.localeCompare(y.student) : 0));
  // fila real do professor/gestor: uma linha por atividade (filtros: para revisar / concluídas; nada marcado = todas)
  const listaGrupos = grupos
    .filter((g) =>
      (!turmaAtiva || g.turmaId === turmaAtiva) &&
      (!filtros.length || (filtros.includes("pendente") && paraRevisar(g) > 0) || (filtros.includes("aprovada") && enviaram(g) > 0 && paraRevisar(g) === 0)) &&
      `${g.titulo} ${g.materia} ${g.turmaNome}`.toLowerCase().includes(search.toLowerCase()))
    .sort((x, y) => x.turmaNome.localeCompare(y.turmaNome) || x.titulo.localeCompare(y.titulo));
  return (
    <>
      {modalForm}
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            {reviewOnly ? "O SEU OLHAR IMPORTA" : "PRATICAR PARA EVOLUIR"}
          </div>
          <h1>{reviewOnly ? "Atividades" : "Minhas atividades"}</h1>
          <p>
            {reviewOnly
              ? "Confira as sugestões, ajuste os critérios e libere o resultado."
              : "Cada atividade é uma oportunidade de aprender algo novo."}
          </p>
        </div>
        {realProfessor && (
          <Button icon={Plus} onPress={() => setCriando(true)}>
            Nova atividade
          </Button>
        )}
      </div>
      <Card>
        <div className="list-toolbar">
          <Filtros grupos={[
            ...(reviewOnly && turmasFila.length > 0 ? [{
              id: "turma", titulo: "Turma", valor: turmaAtiva, onChange: setTurmaFiltro,
              opcoes: turmasFila.map(([id, nome]) => ({ valor: id, rotulo: nome })),
            }] : []),
            {
              id: "status", titulo: "Status", multiplo: true as const, valor: filtros,
              onChange: setFiltros,
              opcoes: [
                ...(realReviewer
                  ? [{ valor: "pendente", rotulo: "Para revisar" }, { valor: "aprovada", rotulo: "Concluídas" }]
                  : [
                      ...(!reviewOnly ? [{ valor: "disponivel", rotulo: "Para fazer" }] : []),
                      { valor: "pendente", rotulo: "Em revisão" },
                      { valor: "corrigida_ia", rotulo: "Corrigidas pela IA" },
                      { valor: "aprovada", rotulo: "Corrigidas" },
                    ]),
              ],
            },
          ]} />
          <label className="search-field">
            <Search size={17} />
            <input
              aria-label="Buscar atividades"
              placeholder="Buscar atividade..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        {realReviewer && listaGrupos.length ? (
          listaGrupos.map((g) => (
            <button key={g.atividadeId} className="activity-row" onClick={() => setGrupoSel(g.atividadeId)}>
              <span className={`activity-icon ${g.kind === "matematica" ? "math-icon" : ""}`}>
                {g.kind === "redacao" ? <BookOpen size={20} /> : <span>ƒx</span>}
              </span>
              <span className="activity-info">
                <strong>{g.titulo}</strong>
                <span>
                  <b>{g.turmaNome} · </b>{g.materia}
                  {g.prazo && ` · prazo ${g.prazo.split("-").reverse().join("/")}`}
                </span>
              </span>
              <span className="grupo-contagem">{enviaram(g)} de {g.alunos.length} enviaram</span>
              {paraRevisar(g) > 0
                ? <Badge tone="amber">{paraRevisar(g)} para revisar</Badge>
                : enviaram(g) > 0 ? <Badge tone="green">Tudo corrigido</Badge> : <Badge tone="neutral">Sem envios</Badge>}
              <ArrowUpRight size={18} />
            </button>
          ))
        ) : !realReviewer && list.length ? (
          list.map((a) => (
            <ActivityRow key={a.id} activity={a} onClick={() => select(a.id)} />
          ))
        ) : (
          <Empty
            title="Nenhuma atividade por aqui"
            text="Tente outro termo ou escolha um filtro diferente."
          >
            <Button
              variant="secondary"
              onPress={() => {
                setSearch("");
                setFiltros([]);
              }}
            >
              Limpar filtros
            </Button>
          </Empty>
        )}
      </Card>
    </>
  );
}
const MAX_FOTOS = 6; // mesmo limite do backend (MAX_FOLHAS)

// miniaturas das fotos escolhidas, com subir/descer/remover: a ordem da lista e a ordem das folhas
function ListaFotos({ files, onChange }: { files: File[]; onChange: (f: File[]) => void }) {
  const urls = useMemo(() => files.map((f) => URL.createObjectURL(f)), [files]);
  useEffect(() => () => urls.forEach(URL.revokeObjectURL), [urls]);
  if (!files.length) return null;
  const mover = (i: number, d: number) => {
    const c = [...files];
    [c[i], c[i + d]] = [c[i + d], c[i]];
    onChange(c);
  };
  return (
    <ol className="lista-fotos">
      {files.map((f, i) => (
        <li key={`${f.name}-${i}`}>
          {/\.pdf$/i.test(f.name) ? <FileText size={28} aria-hidden /> : <img src={urls[i]} alt={`Folha ${i + 1}`} />}
          <span>{/\.pdf$/i.test(f.name) ? "PDF" : `Folha ${i + 1}`} · {f.name}</span>
          <button className="back-link" disabled={i === 0} aria-label={`Subir folha ${i + 1}`} onClick={() => mover(i, -1)}>↑</button>
          <button className="back-link" disabled={i === files.length - 1} aria-label={`Descer folha ${i + 1}`} onClick={() => mover(i, 1)}>↓</button>
          <button className="back-link" aria-label={`Remover folha ${i + 1}`} onClick={() => onChange(files.filter((_, j) => j !== i))}><Trash2 size={14} /></button>
        </li>
      ))}
    </ol>
  );
}

function ActivityDetail({
  activity: a,
  state,
  role,
  update,
  notify,
  onBack,
  onSubmittedReal,
  onCorrigidaReal,
}: Omit<Props, "selected" | "select" | "reviewOnly" | "currentUser"> & {
  activity: Activity;
  onBack: () => void;
  onSubmittedReal?: () => void;
  onCorrigidaReal?: () => void;
}) {
  const [text, setText] = useState(state.drafts[a.id] || "");
  const [files, setFiles] = useState<File[]>([]); // varias fotos do mesmo trabalho, na ordem
  const [mode, setMode] = useState<"texto" | "arquivo">("texto");
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const objetiva = !!a.questoes?.length && a.questoes.every((q) => q.alternativas?.length);
  const [marcadas, setMarcadas] = useState<Record<string, string>>({});
  const enviarMarcadas = async () => {
    const faltam = a.questoes!.filter((q) => !marcadas[q.codigo]).length;
    if (faltam && !window.confirm(`${faltam} questão(ões) sem resposta. Enviar assim mesmo? Depois de enviar não dá para refazer.`)) return;
    setEnviando(true);
    setError("");
    try {
      await enviarObjetiva(a.id, marcadas);
      notify("Respostas enviadas. A correção já está disponível.");
      onSubmittedReal?.();
    } catch (erro) {
      setError(erro instanceof Error ? erro.message : "Não foi possível enviar. Tente de novo.");
    } finally {
      setEnviando(false);
    }
  };
  const [scores, setScores] = useState(
    a.scores ||
      a.aiScores ||
      (a.kind === "redacao" ? [160, 160, 120, 140, 160] : [8]),
  );
  const [feedback, setFeedback] = useState(a.feedback || "");
  const [confirmApproval, setConfirmApproval] = useState(false);
  const [ocrSubmissao, setOcrSubmissao] = useState<SubmissaoAPI | null>(null);
  const [ocrTexto, setOcrTexto] = useState("");
  const [confirmandoOcr, setConfirmandoOcr] = useState(false);
  const confirmarOcr = async () => {
    if (!ocrSubmissao) return;
    if (!ocrTexto.trim()) {
      setError("O texto não pode ficar vazio.");
      return;
    }
    setConfirmandoOcr(true);
    setError("");
    try {
      await confirmarTexto(ocrSubmissao.id, ocrTexto);
      notify("Atividade enviada. Agora ela aguarda a correção.");
      onSubmittedReal?.();
    } catch (erro) {
      setError(erro instanceof Error ? erro.message : "Não foi possível confirmar o texto.");
    } finally {
      setConfirmandoOcr(false);
    }
  };
  const [gerandoCorrecao, setGerandoCorrecao] = useState(false);
  const [erroCorrecao, setErroCorrecao] = useState("");
  const gerarMinhaCorrecao = async () => {
    setGerandoCorrecao(true);
    setErroCorrecao("");
    try {
      const r = await rodarAgente(a.submissaoId ?? a.id);
      if (r.correcao) onCorrigidaReal?.();
      else setErroCorrecao(r.mensagem_aluno ?? "Não foi possível gerar a correção agora. Tente de novo em instantes.");
    } catch (erro) {
      setErroCorrecao(erro instanceof Error ? erro.message : "Não foi possível gerar a correção.");
    } finally {
      setGerandoCorrecao(false);
    }
  };
  const mudarTexto = (v: string) => {
    setText(v);
    update((s) => ({ ...s, drafts: { ...s.drafts, [a.id]: v } }));
  };
  const submit = async () => {
    if (mode === "texto" && text.trim().length < 40) {
      setError("Escreva pelo menos 40 caracteres para enviar sua resposta.");
      return;
    }
    if (mode === "arquivo" && !files.length) {
      setError("Escolha um PDF ou uma imagem para continuar.");
      return;
    }
    if (!confirmed) {
      setError("Confirme que você revisou o conteúdo antes de enviar.");
      return;
    }
    if (onSubmittedReal) {
      setEnviando(true);
      setError("");
      try {
        if (mode === "arquivo") {
          const submissao = await enviarImagem(a.id, files);
          setOcrSubmissao(submissao);
          setOcrTexto(submissao.texto_ocr ?? "");
        } else {
          await enviarTexto(a.id, text);
          update((s) => ({ ...s, drafts: { ...s.drafts, [a.id]: "" } }));
          notify("Redação enviada. Agora ela aguarda a correção do professor.");
          onSubmittedReal();
        }
      } catch (erro) {
        setError(erro instanceof Error ? erro.message : "Não foi possível enviar. Tente de novo.");
      } finally {
        setEnviando(false);
      }
      return;
    }
    update((s) => ({
      ...s,
      drafts: { ...s.drafts, [a.id]: "" },
      activities: s.activities.map((item) =>
        item.id === a.id
          ? {
              ...item,
              status: "pendente",
              text: mode === "texto" ? text : undefined,
              fileName: mode === "arquivo" ? files[0]?.name : undefined,
              date: "Enviada agora",
              aiScores: a.kind === "redacao" ? [160, 160, 120, 140, 160] : [8],
            }
          : item,
      ),
    }));
    notify("Atividade enviada na demonstração. Agora ela aguarda revisão.");
  };
  const approve = () => {
    if (!validScores(scores, a.kind) || !feedback.trim()) {
      setError(
        a.kind === "redacao"
          ? "Use notas de 0 a 200, em intervalos de 20, e escreva um feedback."
          : "Use uma nota de 0 a 10 e escreva um feedback.",
      );
      return;
    }
    update((s) => ({
      ...s,
      activities: s.activities.map((item) =>
        item.id === a.id ? approveActivity(item, scores, feedback) : item,
      ),
    }));
    notify(
      "Correção aprovada. O resultado já está disponível na área do aluno.",
    );
  };
  const teacher = role === "professor";
  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar às atividades
      </button>
      <div className="page-heading">
        <div>
          <Badge tone="neutral">{a.subject}</Badge>
          <h1 className="detail-heading">{a.title}</h1>
          <p>{teacher ? `${a.student}${a.turmaNome ? ` · ${a.turmaNome}` : ""}` : a.date}</p>
        </div>
      </div>
      {a.status === "disponivel" ? (
        <div className="detail-grid">
          <Card>
            {ocrSubmissao ? (
              <>
                <SectionTitle title="Confira o texto da sua foto" />
                <p className="muted">
                  Lemos o texto abaixo da sua imagem. Revise e corrija o que precisar antes de
                  confirmar — depois de confirmado, não dá mais para editar.
                </p>
                <TextInput
                  accessibilityLabel="Texto reconhecido da foto"
                  multiline
                  value={ocrTexto}
                  onChangeText={setOcrTexto}
                  style={{
                    width: "100%",
                    minHeight: 420,
                    fontFamily: "IBM Plex Sans",
                    fontSize: 16,
                    lineHeight: 27,
                    padding: 18,
                    borderWidth: 1,
                    borderColor: "var(--ln-dcd8cc)",
                    borderRadius: 10,
                    textAlignVertical: "top",
                    color: "var(--ink)",
                  }}
                />
                {error && (
                  <p className="error" role="alert">
                    {error}
                  </p>
                )}
                <div className="form-actions">
                  <Button
                    variant="secondary"
                    onPress={() => {
                      setOcrSubmissao(null);
                      setOcrTexto("");
                      setFiles([]);
                      setError("");
                    }}
                  >
                    Cancelar e tentar outras fotos
                  </Button>
                  <Button icon={Check} disabled={confirmandoOcr} onPress={confirmarOcr}>
                    {confirmandoOcr ? "Confirmando..." : "Confirmar e enviar para revisão"}
                  </Button>
                </div>
              </>
            ) : (
              <>
            <SectionTitle title="Sua resposta" />
            {a.questoes?.length ? (
              // gabarito real desta atividade (materias de exatas) -- nunca um texto fixo de outra atividade
              <ol className="question-list">
                {a.questoes.map((q) => (
                  <li key={q.codigo} style={{ whiteSpace: "pre-wrap" }}>
                    {q.enunciado}
                    {q.tem_imagem && <FiguraQuestao atividadeId={a.id} codigo={q.codigo} />}
                    {objetiva && onSubmittedReal && (
                      <div role="radiogroup" aria-label={`Alternativas da ${q.codigo}`} className="alternativas">
                        {q.alternativas!.map((texto, k) => {
                          const letra = "ABCDE"[k];
                          return (
                            <label key={letra} className="alternativa">
                              <input
                                type="radio"
                                name={q.codigo}
                                checked={marcadas[q.codigo] === letra}
                                onChange={() => setMarcadas({ ...marcadas, [q.codigo]: letra })}
                              />
                              <b>{letra})</b> {texto}
                            </label>
                          );
                        })}
                      </div>
                    )}
                  </li>
                ))}
              </ol>
            ) : a.kind === "redacao" ? (
              <p className="muted">
                Escreva um texto dissertativo-argumentativo sobre o tema. Defenda seu ponto de vista e
                apresente uma proposta de intervenção.
              </p>
            ) : (
              <p className="muted">
                Responda a atividade conforme as instruções do seu professor.
              </p>
            )}
            {objetiva && onSubmittedReal ? (
              <>
                {error && <p className="error" role="alert">{error}</p>}
                <div className="form-actions">
                  <Button variant="secondary" onPress={onBack}>Continuar depois</Button>
                  <Button icon={Send} disabled={enviando} onPress={enviarMarcadas}>
                    {enviando ? "Enviando..." : "Enviar respostas"}
                  </Button>
                </div>
              </>
            ) : (
              <>
            <div className="tabs input-tabs">
              <button
                className={mode === "texto" ? "active" : ""}
                onClick={() => {
                  setMode("texto");
                  setError("");
                }}
              >
                Digitar texto
              </button>
              <button
                className={mode === "arquivo" ? "active" : ""}
                onClick={() => {
                  setMode("arquivo");
                  setError("");
                }}
              >
                Enviar arquivo
              </button>
            </div>
            {mode === "texto" ? (
              <>
                {a.questoes?.length ? (
                  // exatas: campo com barra de simbolos (quimica/matematica); redacao segue o campo de sempre
                  <CampoComSimbolos
                    aria-label="Texto da atividade"
                    className="text-area"
                    placeholder="Escreva suas respostas aqui (use Ω Símbolos para H₂O, √, →, π...)"
                    rows={12}
                    value={text}
                    onChange={(e) => mudarTexto(e.target.value)}
                  />
                ) : (
                <TextInput
                  accessibilityLabel="Texto da atividade"
                  placeholder="Suas ideias começam aqui..."
                  multiline
                  value={text}
                  onChangeText={mudarTexto}
                  style={{
                    minHeight: 300,
                    fontFamily: "IBM Plex Sans",
                    fontSize: 16,
                    lineHeight: 27,
                    padding: 18,
                    borderWidth: 1,
                    borderColor: "var(--ln-dcd8cc)",
                    borderRadius: 10,
                    textAlignVertical: "top",
                    color: "var(--ink)",
                  }}
                />
                )}
                <div className="field-meta">
                  <span>Rascunho salvo neste navegador</span>
                  <span>{text.length} caracteres</span>
                </div>
              </>
            ) : (
              <div className="upload-zone">
                <Upload size={30} />
                <strong>{files.length ? `${files.length} foto(s) escolhida(s)` : "Escolha sua atividade"}</strong>
                <span>
                  {onSubmittedReal
                    ? `JPG, PNG ou PDF · até 10 MB cada · até ${MAX_FOTOS} folhas do mesmo trabalho`
                    : "PDF, JPG ou PNG · até 10 MB"}
                </span>
                <input
                  aria-label="Selecionar arquivo da atividade"
                  type="file"
                  multiple={!!onSubmittedReal}
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => {
                    const novas = Array.from(e.target.files ?? []);
                    e.target.value = ""; // permite escolher a mesma foto de novo
                    const valido = (f: File) =>
                      f.size <= 10 * 1024 * 1024 &&
                      /\.(pdf|png|jpe?g)$/i.test(f.name);
                    if (novas.some((f) => !valido(f))) {
                      setError("Use PDF, JPG ou PNG com no máximo 10 MB.");
                      return;
                    }
                    const total = onSubmittedReal ? [...files, ...novas] : novas.slice(0, 1);
                    if (total.length > MAX_FOTOS) {
                      setError(`No máximo ${MAX_FOTOS} fotos por envio.`);
                      return;
                    }
                    setFiles(total);
                    setError("");
                  }}
                />
                {onSubmittedReal && <ListaFotos files={files} onChange={setFiles} />}
                <p className="tiny">
                  {onSubmittedReal
                    ? "Se o trabalho tem mais de uma folha, adicione todas e deixe na ordem certa. Lemos o texto de tudo junto: você confere e confirma antes de enviar."
                    : "Nesta demonstração, somente o nome do arquivo é salvo. A leitura do manuscrito será conectada ao backend."}
                </p>
              </div>
            )}
            <label className="checkbox-line">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
              />
              Revisei minha resposta e quero enviá-la para correção.
            </label>
            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <div className="form-actions">
              <Button variant="secondary" onPress={onBack}>
                Continuar depois
              </Button>
              <Button icon={Send} disabled={enviando} onPress={submit}>
                {enviando ? "Enviando..." : "Enviar para revisão"}
              </Button>
            </div>
              </>
            )}
              </>
            )}
          </Card>
          <Card className="aside-card">
            <ShieldCheck size={29} color="var(--tx-197451)" />
            <h3>Seu professor está com você.</h3>
            <p>
              A IA auxilia na correção. Seu professor revisa cada resultado
              antes que ele apareça aqui.
            </p>
            <hr />
            <h4>Antes de enviar</h4>
            <ul>
              <li>Confira se respondeu ao tema.</li>
              <li>Revise a organização das ideias.</li>
              <li>Se enviar uma foto, use boa iluminação.</li>
            </ul>
            <Badge tone="neutral">Ambiente de demonstração</Badge>
          </Card>
        </div>
      ) : a.status === "pendente" && !teacher && !a.scores ? (
        <Card>
          {onCorrigidaReal ? (
            <Empty
              title="Recebemos sua atividade!"
              text="Agora você já pode gerar sua correção por IA e ver o resultado na hora. Depois, seu professor confirma a nota final."
            >
              <Button icon={Sparkles} disabled={gerandoCorrecao} onPress={gerarMinhaCorrecao}>
                {gerandoCorrecao ? "Gerando correção..." : "Gerar minha correção com IA"}
              </Button>
              {erroCorrecao && (
                <p className="error" role="alert">
                  {erroCorrecao}
                </p>
              )}
              <Button variant="secondary" onPress={onBack}>
                Voltar às atividades
              </Button>
            </Empty>
          ) : (
            <Empty
              title="Recebemos sua atividade!"
              text="Seu professor vai revisar a correção. Assim que ele aprovar, você encontra a nota e as orientações nesta tela."
            >
              <Badge tone="amber">Aguardando revisão do professor</Badge>
              <Button variant="secondary" onPress={onBack}>
                Voltar às atividades
              </Button>
            </Empty>
          )}
        </Card>
      ) : (
        (visibleResult(a, role) || (role === "aluno" && !!a.scores)) && (
          <div className="detail-grid">
            <Card>
              <SectionTitle
                title={
                  a.status === "aprovada"
                    ? "Correção aprovada"
                    : "Revisão da atividade"
                }
              />
              <Badge tone={a.status === "aprovada" ? "green" : a.status === "corrigida_ia" ? "blue" : "amber"}>
                {a.status === "aprovada"
                  ? "Revisada pelo professor"
                  : onCorrigidaReal
                    ? "Sugestão da IA · aguardando confirmação do professor"
                    : "Sugestão demonstrativa da IA · confiança média"}
              </Badge>
              <div className="score-total">
                <strong>{scores.reduce((s, n) => s + n, 0)}</strong>
                <span>/ {a.valorTotal ?? scores.length * 200} pontos</span>
              </div>
              <div className="criteria-grid">
                {scores.map((n, i) => (
                  <label key={i}>
                    <span>{a.kind === "redacao" ? `C${i + 1}` : `Q${i + 1}`}</span>
                    {teacher && a.status !== "aprovada" ? (
                      <Escolha
                        aria-label={
                          a.kind === "redacao"
                            ? `Nota da competência ${i + 1}`
                            : "Nota de raciocínio"
                        }
                        value={n}
                        onChange={(e) =>
                          setScores(
                            scores.map((v, j) =>
                              j === i ? Number(e.target.value) : v,
                            ),
                          )
                        }
                      >
                        {Array.from({ length: 11 }, (_, j) =>
                          a.kind === "redacao" ? j * 20 : j,
                        ).map((v) => (
                          <option key={v}>{v}</option>
                        ))}
                      </Escolha>
                    ) : (
                      <strong>{n}</strong>
                    )}
                    <small>
                      {a.criterios?.[i]?.nome ??
                        (a.kind === "redacao"
                          ? [
                              "Norma culta",
                              "Tema",
                              "Argumentação",
                              "Coesão",
                              "Intervenção",
                            ][i]
                          : "Raciocínio")}
                    </small>
                    {a.criterios?.[i]?.justificativa && (
                      <small className="justificativa-texto">
                        {a.criterios[i].justificativa}
                      </small>
                    )}
                  </label>
                ))}
              </div>
              <h3>
                {teacher && a.status !== "aprovada"
                  ? "Orientação ao aluno"
                  : a.status === "aprovada"
                    ? "Comentário do professor"
                    : "Comentário da IA"}
              </h3>
              {teacher && a.status !== "aprovada" ? (
                <>
                  <textarea
                    aria-label="Feedback do professor"
                    className="text-area"
                    placeholder="Explique os pontos fortes e indique o que o aluno pode melhorar..."
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                  />
                  {error && (
                    <p role="alert" className="error">
                      {error}
                    </p>
                  )}
                  {confirmApproval ? (
                    <div className="confirmation">
                      <strong>Publicar esta correção?</strong>
                      <p>O aluno verá as notas e o feedback acima.</p>
                      <div className="form-actions">
                        <Button
                          variant="secondary"
                          onPress={() => setConfirmApproval(false)}
                        >
                          Voltar à revisão
                        </Button>
                        <Button icon={Check} onPress={approve}>
                          Confirmar aprovação
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      icon={Check}
                      onPress={() => {
                        if (!feedback.trim()) {
                          setError(
                            "Escreva uma orientação para o aluno antes de aprovar.",
                          );
                          return;
                        }
                        setError("");
                        setConfirmApproval(true);
                      }}
                    >
                      Aprovar e liberar resultado
                    </Button>
                  )}
                </>
              ) : (
                <p className="feedback-text">{a.feedback}</p>
              )}
              {!teacher && a.criterios && <ComentariosDaIA criterios={a.criterios} />}
              <div className="card-note">
                <ShieldCheck size={16} />
                {a.status === "aprovada"
                  ? "Correção assistida por IA e validada por um professor."
                  : onCorrigidaReal
                    ? "Essa é a nota da IA agora mesmo; seu professor ainda vai confirmar."
                    : "A sugestão só será publicada depois da sua aprovação."}
              </div>
            </Card>
            <Card>
              <SectionTitle title="Texto enviado" />
              <div className="essay">
                <VisaoDoEnvio submissaoId={a.submissaoId} imagem={a.tipoEnvio === "IMAGEM"} criterios={a.criterios}
                  texto={a.text} editavel={false} notify={notify} vazio={
                    <>
                      <FileText size={24} />
                      <p>{a.fileName}</p>
                      <p>
                        O arquivo não é armazenado neste protótipo. A visualização
                        e o OCR dependem da integração.
                      </p>
                    </>
                  } />
              </div>
            </Card>
          </div>
        )
      )}
    </>
  );
}

// niveis validos de nota por competencia do ENEM (C1-C5): o backend rejeita qualquer outro valor
const NOTAS_ENEM = [0, 40, 80, 120, 160, 200];

function RevisaoReal({
  activity: a,
  onBack,
  onApproved,
  readOnly,
  notify,
}: {
  activity: Activity;
  onBack: () => void;
  onApproved: () => void;
  readOnly?: boolean;
  notify: (s: string) => void;
}) {
  const [texto, setTexto] = useState<string | null>(null);
  const [tipoEnvio, setTipoEnvio] = useState("");
  const [correcao, setCorrecao] = useState<CorrecaoAPI | null>(null);
  const [notas, setNotas] = useState<Record<string, number>>({});
  const [feedback, setFeedback] = useState("");
  const [motivoMudanca, setMotivoMudanca] = useState("");
  const [avaliacao, setAvaliacao] = useState<"BOA" | "MEDIA" | "MA" | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [corrigindo, setCorrigindo] = useState(false);
  const [aprovando, setAprovando] = useState(false);
  const [confirmApproval, setConfirmApproval] = useState(false);
  const [error, setError] = useState("");
  const [agente, setAgente] = useState<AgenteAPI | null>(null);

  const aplicarCorrecao = (c: CorrecaoAPI) => {
    setCorrecao(c);
    setAvaliacao(c.avaliacao_ia);
    setFeedback(c.feedback ?? "");
    setNotas(Object.fromEntries(c.criterios.map((cr) => [cr.codigo, cr.nota_professor ?? cr.nota])));
  };

  useEffect(() => {
    let ativo = true;
    Promise.all([
      verSubmissao(a.id),
      // sem correcao da IA: o professor, se for ele, ja ve a ficha em branco para corrigir direto
      verCorrecao(a.id).catch(() => (readOnly ? null : verCorrecaoManual(a.id).catch(() => null))),
      verAgente(a.id).catch(() => null),
    ]).then(([s, c, ag]) => {
      if (!ativo) return;
      setTexto(s.texto_confirmado ?? s.texto_ocr ?? "");
      setTipoEnvio(s.tipo_envio);
      if (c) aplicarCorrecao(c);
      setAgente(ag);
      setCarregando(false);
    });
    return () => {
      ativo = false;
    };
  }, [a.id]);

  const gerarCorrecao = () => {
    setCorrigindo(true);
    setError("");
    rodarAgente(a.id)
      .then((r) => {
        setAgente(r);
        if (r.correcao) aplicarCorrecao(r.correcao);
      })
      .catch((erro) =>
        setError(erro instanceof Error ? erro.message : "Não foi possível gerar a correção."),
      )
      .finally(() => setCorrigindo(false));
  };

  const aprovar = () => {
    // exatas: nota livre de 0 ate o valor da questao; confere antes de mandar ao servidor
    const maxDe = (codigo: string) => correcao?.criterios.find((c) => c.codigo === codigo)?.valor
      ?? (a.valorTotal ?? 1000) / Math.max(correcao?.criterios.length ?? 1, 1);
    const invalida = Object.entries(notas).find(
      ([codigo, n]) => codigo.startsWith("Q") && !(Number.isFinite(n) && n >= 0 && n <= maxDe(codigo) + 0.01),
    );
    if (invalida) {
      setError(`A nota de ${invalida[0]} deve estar entre 0 e ${Math.round(maxDe(invalida[0]) * 100) / 100}.`);
      setConfirmApproval(false);
      return;
    }
    setAprovando(true);
    setError("");
    aprovarCorrecao(
      a.id,
      Object.entries(notas).map(([codigo, nota]) => ({ codigo, nota: Math.round(nota * 100) / 100 })),
      feedback,
      motivoMudanca,
      avaliacao,
    )
      .then(() => onApproved())
      .catch((erro) => {
        setError(erro instanceof Error ? erro.message : "Não foi possível aprovar.");
        setConfirmApproval(false);
      })
      .finally(() => setAprovando(false));
  };

  const aprovada = a.status === "aprovada";
  const semIA = correcao?.modelo_usado === "professor"; // o professor corrigiu direto, sem a IA
  // o professor mexeu em alguma nota que a IA deu? Então a IA errou ali e pode aprender o porquê
  const mudouNota = !semIA && !!correcao?.criterios.some(
    (c) => Number.isFinite(notas[c.codigo]) && Math.abs(notas[c.codigo] - c.nota) > 0.01,
  );
  const nota = Math.round(Object.values(notas).reduce((s, n) => s + (Number.isFinite(n) ? n : 0), 0) * 100) / 100;

  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar às atividades
      </button>
      <div className="page-heading">
        <div>
          <Badge tone="neutral">{a.subject}</Badge>
          <h1 className="detail-heading">{a.title}</h1>
          <p>{a.student}{a.turmaNome ? ` · ${a.turmaNome}` : ""}</p>
        </div>
      </div>
      {carregando ? (
        <Card>
          <p className="muted">Carregando submissão...</p>
        </Card>
      ) : (
        <div className="detail-grid">
          <Card>
            <SectionTitle title={aprovada ? "Correção aprovada" : "Revisão da atividade"} />
            {!correcao ? (
              <>
                <p className="muted">Esta redação ainda não tem correção.</p>
                {!readOnly && (
                  <Button icon={Sparkles} disabled={corrigindo} onPress={gerarCorrecao}>
                    {corrigindo ? "Agente trabalhando..." : "Corrigir com o agente de IA"}
                  </Button>
                )}
                {error && (
                  <p role="alert" className="error">
                    {error}
                  </p>
                )}
              </>
            ) : (
              <>
                <Badge tone={aprovada ? "green" : "amber"}>
                  {aprovada
                    ? "Revisada pelo professor"
                    : semIA
                      ? "Correção sua, sem IA"
                      : `Sugestão da IA · confiança ${Math.round(correcao.confianca * 100)}%`}
                </Badge>
                {semIA && !aprovada && !readOnly && (
                  <Button icon={Sparkles} variant="secondary" disabled={corrigindo} onPress={gerarCorrecao}>
                    {corrigindo ? "Agente trabalhando..." : "Prefiro uma sugestão da IA"}
                  </Button>
                )}
                <div className="score-total">
                  <strong>{nota}</strong>
                  <span>/ {a.valorTotal ?? 1000} pontos</span>
                </div>
                <div className="criteria-grid">
                  {correcao.criterios.map((c) => {
                    // exatas (Q1..Qn): niveis dependem do valor da atividade, dividido pelas
                    // questoes (ver app/routers/submissoes.py::aprovar_correcao). Redacao
                    // (C1..C5): sempre a escala fixa de 0 a 200 do ENEM.
                    const exatas = c.codigo.startsWith("Q");
                    const valorPorQuestao = c.valor ?? (a.valorTotal ?? 1000) / correcao.criterios.length;
                    const niveis = NOTAS_ENEM;
                    return (
                      <label key={c.codigo}>
                        <span>{c.codigo}</span>
                        {!aprovada && !readOnly && exatas ? (
                          // exatas: o professor digita QUALQUER nota de 0 ate o valor da questao
                          // (a escala de 40 em 40 e so da redacao do ENEM)
                          <input
                            key={`${c.codigo}-${c.nota}`}
                            type="number"
                            inputMode="decimal"
                            min={0}
                            max={Math.round(valorPorQuestao * 100) / 100}
                            step="0.01"
                            aria-label={`Nota de ${c.codigo} (de 0 a ${Math.round(valorPorQuestao * 100) / 100})`}
                            defaultValue={notas[c.codigo] ?? c.nota}
                            onChange={(e) =>
                              setNotas({
                                ...notas,
                                [c.codigo]: e.target.value === "" ? NaN : Number(e.target.value),
                              })
                            }
                          />
                        ) : !aprovada && !readOnly ? (
                          <Escolha
                            aria-label={`Nota de ${c.codigo}`}
                            value={notas[c.codigo] ?? c.nota}
                            onChange={(e) =>
                              setNotas({ ...notas, [c.codigo]: Number(e.target.value) })
                            }
                          >
                            {niveis.map((v) => (
                              <option key={v} value={v}>
                                {v}
                              </option>
                            ))}
                          </Escolha>
                        ) : (
                          <strong>{notas[c.codigo]}</strong>
                        )}
                        <small>{c.nome}</small>
                        {c.justificativa && <small className="justificativa-texto">{c.justificativa}</small>}
                      </label>
                    );
                  })}
                </div>
                <h3>{aprovada || readOnly ? "Orientação" : "Orientação ao aluno"}</h3>
                {!aprovada && !readOnly ? (
                  <textarea
                    aria-label="Feedback do professor"
                    className="text-area"
                    placeholder="Explique os pontos fortes e indique o que o aluno pode melhorar..."
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                  />
                ) : (
                  <p className="feedback-text">{feedback || "Ainda sem orientação registrada."}</p>
                )}
                {!readOnly && !semIA && (
                  <>
                    <p className="tiny muted">Ensine a IA com 1 clique (não muda a nota; o aluno não vê):</p>
                    <Seletor rotulo="Avaliar a correção da IA" placeholder="Avaliar a correção da IA"
                      opcoes={[{ valor: "BOA", rotulo: "Correção/explicação boa" }, { valor: "MEDIA", rotulo: "Correção/explicação razoável" }, { valor: "MA", rotulo: "Correção/explicação ruim" }]}
                      valor={avaliacao ?? ""}
                      onChange={(v) => {
                        const novo = (v || null) as "BOA" | "MEDIA" | "MA" | null;
                        if (!aprovada) return setAvaliacao(novo);
                        avaliarIA(a.id, novo).then((c) => setAvaliacao(c.avaliacao_ia))
                          .catch((erro) => setError(erro instanceof Error ? erro.message : "Não foi possível salvar."));
                      }} />
                  </>
                )}
                {!aprovada && !readOnly && (mudouNota || !!avaliacao) && (
                  <>
                    <h3>Ensine a IA: por quê?</h3>
                    <p className="muted">
                      {({
                        BOA: "Opcional: explique por que a correção/explicação está boa, para a IA repetir esse jeito.",
                        MEDIA: "Opcional: explique o que está bom e o que faltou, para a IA melhorar.",
                        MA: "Opcional: explique por que a correção/explicação está ruim, para a IA não repetir o erro.",
                      } as Record<string, string>)[avaliacao ?? ""] ?? "Opcional: explique por que mudou a nota, para a IA corrigir do seu jeito."} Só a IA lê (o aluno não vê).
                    </p>
                    <textarea
                      aria-label="Por que você avaliou assim a correção da IA"
                      className="text-area"
                      maxLength={1000}
                      placeholder="Ex.: a nota está certa, mas faltou explicar o conectivo; ou: a IA deu nota cheia, mas eu exijo a verificação final da conta."
                      value={motivoMudanca}
                      onChange={(e) => setMotivoMudanca(e.target.value)}
                    />
                  </>
                )}
                {error && (
                  <p role="alert" className="error">
                    {error}
                  </p>
                )}
                {!aprovada && !readOnly &&
                  (confirmApproval ? (
                    <div className="confirmation">
                      <strong>Publicar esta correção?</strong>
                      <p>O aluno verá as notas e o feedback acima.</p>
                      <div className="form-actions">
                        <Button variant="secondary" onPress={() => setConfirmApproval(false)}>
                          Voltar à revisão
                        </Button>
                        <Button icon={Check} disabled={aprovando} onPress={aprovar}>
                          {aprovando ? "Aprovando..." : "Confirmar aprovação"}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      icon={Check}
                      onPress={() => {
                        if (!feedback.trim()) {
                          setError("Escreva uma orientação para o aluno antes de aprovar.");
                          return;
                        }
                        setError("");
                        setConfirmApproval(true);
                      }}
                    >
                      Aprovar e liberar resultado
                    </Button>
                  ))}
              </>
            )}
          </Card>
          <div className="agente-coluna">
          {agente && <PassoAPassoAgente agente={agente} />}
          {correcao && !semIA && <FontesDaIA submissaoId={a.id} />}
          <Card>
            <SectionTitle title="Texto enviado" />
            <div className="essay">
              <VisaoDoEnvio submissaoId={a.id} imagem={tipoEnvio === "IMAGEM"} criterios={correcao?.criterios}
                texto={texto} editavel={!readOnly} notify={notify} />
            </div>
          </Card>
          </div>
        </div>
      )}
    </>
  );
}

// nomes das ferramentas do agente (backend/app/routers/agente.py) como o professor le na tela
const NOMES_FERRAMENTAS: Record<string, string> = {
  ler_envio: "Leu o envio",
  corrigir_redacao_enem: "Corrigiu a redação (C1 a C5)",
  corrigir_exatas: "Corrigiu pelo gabarito",
  consultar_historico_aluno: "Consultou o histórico do aluno",
  gerar_exercicios_reforco: "Gerou exercícios de reforço",
  sinalizar_professor: "Chamou a atenção do professor",
  pedir_nova_foto: "Pediu uma nova foto",
  finalizar: "Finalizou",
};

const ROTULO_FONTE = { material: "Material", instrucao: "Instrução", exemplo: "Correção sua parecida" } as const;

// mostra ao professor o que da memória dele a IA usou nesta correção, e avisa se ela anda errando o jeito dele
function FontesDaIA({ submissaoId }: { submissaoId: string }) {
  const [dados, setDados] = useState<FontesIAAPI | null>(null);
  useEffect(() => {
    let ativo = true;
    verFontesIA(submissaoId).then((d) => ativo && setDados(d)).catch(() => undefined);
    return () => {
      ativo = false;
    };
  }, [submissaoId]);
  if (!dados || (!dados.aviso && !dados.fontes.length)) return null;
  return (
    <div className="fontes-ia">
      {dados.aviso && <p role="alert" className="error">{dados.aviso}</p>}
      {dados.fontes.length > 0 && (
        <details>
          <summary>O que a IA usou do seu material ({dados.fontes.length})</summary>
          <ul>
            {dados.fontes.map((f, i) => (
              <li key={i}>
                <strong>{ROTULO_FONTE[f.tipo]}: {f.titulo}</strong>
                <br />
                <small>{f.trecho}</small>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

function PassoAPassoAgente({ agente }: { agente: AgenteAPI }) {
  const passos = agente.passos.filter((p) => p.tipo !== "pensamento" || p.texto);
  return (
    <Card>
      <SectionTitle title="Passo a passo do agente" />
      <ol className="agente-passos">
        {passos.map((p, i) => (
          <li key={i} className={p.erro ? "agente-passo erro" : "agente-passo"}>
            {p.tipo === "ferramenta" ? (
              <>
                <strong>{NOMES_FERRAMENTAS[p.ferramenta ?? ""] ?? p.ferramenta}</strong>
                {p.motivo && <span>{p.motivo}</span>}
                {p.erro && <small>Não deu certo; o agente mudou o caminho.</small>}
              </>
            ) : (
              <span className="agente-pensamento">{p.texto}</span>
            )}
          </li>
        ))}
      </ol>
      {agente.resumo_professor && (
        <p className="agente-resumo">
          <strong>Para o professor:</strong> {agente.resumo_professor}
        </p>
      )}
      {agente.exercicios && agente.exercicios.length > 0 && (
        <p className="agente-resumo">
          <strong>Exercícios enviados ao aluno:</strong>{" "}
          {agente.exercicios.map((e) => `${e.habilidade_codigo} · ${e.titulo}`).join("; ")}
        </p>
      )}
    </Card>
  );
}

// atividade recem-criada que nenhum aluno enviou ainda: nao ha submissao pra revisar, so
// confirma pro professor que a atividade existe e esta disponivel pra turma.
function AtividadeSemEnvio({ activity: a, onBack }: { activity: Activity; onBack: () => void }) {
  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar às atividades
      </button>
      <div className="page-heading">
        <div>
          <Badge tone="neutral">{a.subject}</Badge>
          <h1 className="detail-heading">{a.title}</h1>
          <p>{a.student}</p>
        </div>
      </div>
      <Card>
        <Empty
          title="Nenhum envio ainda"
          text="Esta atividade já está disponível para a turma. Assim que um aluno enviar, ela aparece aqui para revisão."
        />
      </Card>
    </>
  );
}

// Editar / Excluir a atividade (professor da turma e gestor; o backend confere). Com envios, excluir ARQUIVA.
function BarraAtividade({ atividadeId, onEditar, onExcluida, notify }: {
  atividadeId: string; onEditar: () => void; onExcluida: () => void; notify: (s: string) => void;
}) {
  const [ocupado, setOcupado] = useState(false);
  const excluir = async () => {
    setOcupado(true);
    try {
      const a = (await listarAtividades()).find((x) => x.id === atividadeId);
      const aviso = a?.tem_envios
        ? "Esta atividade já tem envios: ela será ARQUIVADA (some para os alunos, as notas e o histórico continuam). Continuar?"
        : "Excluir esta atividade? Isso não pode ser desfeito.";
      if (!window.confirm(aviso)) return;
      const { acao } = await excluirAtividade(atividadeId);
      notify(acao === "arquivada" ? "Atividade arquivada. As notas foram mantidas." : "Atividade excluída.");
      onExcluida();
    } catch (e) {
      notify(e instanceof Error ? e.message : "Não foi possível excluir.");
    } finally {
      setOcupado(false);
    }
  };
  return (
    <div className="form-actions left">
      <Button variant="secondary" icon={Pencil} onPress={onEditar}>Editar atividade</Button>
      <Button variant="ghost" icon={Trash2} onPress={excluir} disabled={ocupado}>Excluir atividade</Button>
    </div>
  );
}

function EditarAtividade({ atividadeId, onBack, onSalvo, notify }: {
  atividadeId: string; onBack: () => void; onSalvo: () => void; notify: (s: string) => void;
}) {
  const [a, setA] = useState<AtividadeAPI | null>(null);
  const [titulo, setTitulo] = useState("");
  const [prazo, setPrazo] = useState("");
  const [valorTotal, setValorTotal] = useState(1000);
  const [questoes, setQuestoes] = useState<{ enunciado: string; resposta_correta: string; alternativas: string[] | null; subtopico: string; valor?: number }[]>([]);
  const [salvando, setSalvando] = useState(false);
  useEffect(() => {
    listarAtividades().then((lista) => {
      const x = lista.find((y) => y.id === atividadeId);
      if (!x) return notify("Atividade não encontrada.");
      setA(x);
      setTitulo(x.titulo);
      setPrazo(x.prazo ?? "");
      setValorTotal(x.valor_total);
      setQuestoes((x.questoes ?? []).map((q) => ({ enunciado: q.enunciado, resposta_correta: q.resposta_correta ?? "", alternativas: q.alternativas ?? null, subtopico: q.subtopico ?? "", valor: q.valor ?? undefined })));
    }).catch(() => notify("Não foi possível carregar a atividade."));
  }, [atividadeId]);
  if (!a) return <Empty title="Carregando..." text="Buscando a atividade." />;
  const exatas = !!a.questoes?.length;
  const gabaritoLivre = exatas && !a.tem_envios; // com envios o gabarito fica congelado
  const salvar = async () => {
    if (!titulo.trim()) return notify("Dê um título para a atividade.");
    if (gabaritoLivre && questoes.some((q) => !q.enunciado.trim() || !q.resposta_correta.trim()))
      return notify("Preencha o enunciado e a resposta (alternativa correta ou resposta exemplo) de todas as questões.");
    const payloadQuestoes = questoes.map((q) => ({
      enunciado: q.enunciado, resposta_correta: q.resposta_correta, subtopico: q.subtopico.trim() || undefined,
      valor: valorTotal === a.valor_total ? q.valor : undefined, // mudou o total: volta a dividir igual
      alternativas: q.alternativas ? alternativasDe(q.alternativas) ?? undefined : undefined,
    }));
    if (gabaritoLivre && questoes.some((q, i) => q.alternativas && !payloadQuestoes[i].alternativas))
      return notify("Questão objetiva: preencha ao menos 2 alternativas seguidas (A, B...).");
    setSalvando(true);
    try {
      await editarAtividade(a.id, {
        titulo: titulo.trim(),
        prazo: prazo || null,
        ...(gabaritoLivre ? { valor_total: valorTotal, questoes: payloadQuestoes } : {}),
      });
      notify("Atividade atualizada.");
      onSalvo();
    } catch (e) {
      notify(e instanceof Error ? e.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  };
  return (
    <>
      <p className="muted">{a.turma} · {a.materia}</p>
      <Card>
        <div className="form-grid">
          <label>Título<input value={titulo} onChange={(e) => setTitulo(e.target.value)} /></label>
          <label>Prazo de entrega<input type="date" value={prazo} onChange={(e) => setPrazo(e.target.value)} /></label>
          {gabaritoLivre && (
            <label>Valor total (pontos)
              <input type="number" min={1} value={valorTotal} onChange={(e) => setValorTotal(Number(e.target.value))} />
            </label>
          )}
        </div>
        {exatas && a.tem_envios && (
          <p className="tiny muted">Já há envios: só o título e o prazo podem mudar. Para mudar o gabarito, crie uma nova atividade.</p>
        )}
        {gabaritoLivre && questoes.map((q, i) => (
          <div key={i} className="form-grid">
            <label>Questão {i + 1} — enunciado
              <CampoComSimbolos value={q.enunciado} onChange={(e) => setQuestoes(questoes.map((x, j) => j === i ? { ...x, enunciado: e.target.value } : x))} />
            </label>
            {q.alternativas ? (
              <CamposObjetiva
                alternativas={q.alternativas}
                gabarito={q.resposta_correta}
                onChange={(alternativas, resposta_correta) => setQuestoes(questoes.map((x, j) => j === i ? { ...x, alternativas, resposta_correta } : x))}
              />
            ) : (
              <label>Resposta exemplo
                <CampoComSimbolos value={q.resposta_correta} onChange={(e) => setQuestoes(questoes.map((x, j) => j === i ? { ...x, resposta_correta: e.target.value } : x))} />
              </label>
            )}
            <label>Submatéria (em branco: a IA identifica)
              <input value={q.subtopico} onChange={(e) => setQuestoes(questoes.map((x, j) => j === i ? { ...x, subtopico: e.target.value } : x))} />
            </label>
            {questoes.length > 1 && i === questoes.length - 1 && (
              <Button variant="ghost" icon={Trash2} onPress={() => setQuestoes(questoes.slice(0, -1))}>Remover a última questão</Button>
            )}
          </div>
        ))}
        {gabaritoLivre && (
          <Button variant="ghost" icon={Plus} onPress={() => setQuestoes([...questoes, { enunciado: "", resposta_correta: "", subtopico: "", alternativas: questoes[0]?.alternativas ? ["", ""] : null }])}>Adicionar questão</Button>
        )}
        <div className="form-actions left">
          <Button variant="secondary" onPress={onBack}>Cancelar</Button>
          <Button onPress={salvar} disabled={salvando}>{salvando ? "Salvando..." : "Salvar alterações"}</Button>
        </div>
      </Card>
    </>
  );
}

const TIPOS_ATIVIDADE: { value: string; label: string }[] = [
  { value: "EXERCICIO", label: "Exercício avaliativo" },
  { value: "PROVA", label: "Prova" },
  { value: "REDACAO", label: "Redação" },
];

// figura do enunciado (anexada pelo professor); a imagem exige o token, entao vem como blob
function FiguraQuestao({ atividadeId, codigo }: { atividadeId: string; codigo: string }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    let ativo = true;
    urlFiguraQuestao(atividadeId, codigo)
      .then((u) => ativo && setUrl(u))
      .catch(() => undefined);
    return () => {
      ativo = false;
    };
  }, [atividadeId, codigo]);
  return url ? <img src={url} alt={`Figura da questão ${codigo}`} style={{ maxWidth: "100%", display: "block", marginTop: 8 }} /> : null;
}

// alternativas preenchidas em ordem (A, B, C...); null se ha buraco no meio ou menos de 2
function alternativasDe(alts: string[]): string[] | null {
  const a = alts.map((x) => x.trim());
  const n = a.findIndex((x) => !x);
  const cheias = n < 0 ? a : a.slice(0, n);
  return cheias.length >= 2 && !a.slice(cheias.length).some(Boolean) ? cheias : null;
}

// campos de uma questao objetiva (estilo ENEM): comeca com A e B, o professor adiciona ate E; gabarito = letra
function CamposObjetiva({ alternativas, gabarito, onChange }: {
  alternativas: string[]; gabarito: string; onChange: (alternativas: string[], gabarito: string) => void;
}) {
  const alts = alternativas.length >= 2 ? alternativas : [...alternativas, "", ""].slice(0, 2);
  return (
    <fieldset className="alternativas-form">
      <legend>Alternativas (marque a correta)</legend>
      {alts.map((texto, k) => {
        const letra = "ABCDE"[k];
        return (
          <label key={letra} className="alternativa">
            <input type="radio" aria-label={`Gabarito ${letra}`} checked={gabarito === letra} disabled={!texto.trim()}
              onChange={() => onChange(alts, letra)} />
            <b>{letra})</b>
            <CampoComSimbolos linha value={texto} placeholder={`Alternativa ${letra}`}
              onChange={(e) => onChange(alts.map((x, j) => (j === k ? e.target.value : x)), gabarito === letra && !e.target.value.trim() ? "" : gabarito)} />
          </label>
        );
      })}
      <div className="form-actions left">
        {alts.length < 5 && (
          <Button variant="ghost" icon={Plus} onPress={() => onChange([...alts, ""], gabarito)}>
            Adicionar alternativa ({"ABCDE"[alts.length]})
          </Button>
        )}
        {alts.length > 2 && (
          <Button variant="ghost" icon={Trash2}
            onPress={() => onChange(alts.slice(0, -1), gabarito === "ABCDE"[alts.length - 1] ? "" : gabarito)}>
            Remover a última
          </Button>
        )}
      </div>
    </fieldset>
  );
}

type QuestaoNova = { r: Rascunho; pontos: string; subtopico: string; figura?: File };
const questaoVazia = (): QuestaoNova => ({ r: { ...vazio, alternativas: ["", "", "", ""], respostasExemplo: [""] }, pontos: "", subtopico: "" });
const PONTOS_QUESTAO = ["0,5", "1", "1,5", "2", "2,5", "3", "4", "5"].map((x) => x.replace(",", "."));

function NovaAtividade({
  onBack,
  onCriada,
  notify,
}: {
  onBack: () => void;
  onCriada: () => void;
  notify: (s: string) => void;
}) {
  const [turmas, setTurmas] = useState<TurmaAPI[] | null>(null);
  const [materias, setMaterias] = useState<MateriaAPI[] | null>(null);
  const [turmaIds, setTurmaIds] = useState<string[]>([]); // uma atividade independente por turma marcada
  const [materiaId, setMateriaId] = useState("");
  const [assuntoId, setAssuntoId] = useState("");
  const [titulo, setTitulo] = useState("");
  const [tipo, setTipo] = useState<"" | "EXERCICIO" | "PROVA" | "REDACAO">(""); // nada pre-selecionado
  const [aba, setAba] = useState<"escrever" | "ia" | null>(null);
  const [formato, setFormato] = useState<"" | "objetiva" | "discursiva">("");
  // o PontosSeletor guarda o "Outro" por dentro: trocar a key o faz recomecar junto com o valor
  const [chaveTotal, setChaveTotal] = useState(0);
  const [chaveQuestoes, setChaveQuestoes] = useState(0);
  const [totalTxt, setTotalTxt] = useState(""); // nada pre-selecionado: as questoes so aparecem depois do total
  const [questoes, setQuestoes] = useState<QuestaoNova[]>([questaoVazia()]);
  const [prazo, setPrazo] = useState("");
  const [error, setError] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [sugerindo, setSugerindo] = useState<number | null>(null);
  // pedir para a IA
  const [assunto, setAssunto] = useState("");
  const [quantidade, setQuantidade] = useState(3);
  const [instrucoes, setInstrucoes] = useState("");
  const [gerando, setGerando] = useState(false);
  const [sugestoes, setSugestoes] = useState<SugestaoExercicioAPI[]>([]);

  useEffect(() => {
    Promise.all([listarTurmasMinhas(), listarMaterias()]).then(([t, m]) => {
      setTurmas(t);
      setMaterias(m);
    });
  }, []);

  const carregando = turmas === null || materias === null;
  const exigeGabarito = !!tipo && tipo !== "REDACAO"; // o formato vem do tipo da atividade, não da matéria
  const total = Number(totalTxt) || 0;
  // a questao guarda um texto so de gabarito: varias respostas de exemplo viram um texto com as alternativas
  const respostaDe = (q: QuestaoNova) =>
    q.r.respostasExemplo.map((x) => x.trim()).filter(Boolean).join("\n\nOutra resposta possível: ");
  const setQ = (i: number, mudanca: Partial<QuestaoNova>) => setQuestoes((qs) => qs.map((x, j) => (j === i ? { ...x, ...mudanca } : x)));
  const somaDadas = questoes.reduce((t, q) => t + (Number(q.pontos) || 0), 0);

  // mudou qualquer escolha: as outras escolhas ficam, mas as questoes (e as sugestoes da IA) sao apagadas;
  // trocar e voltar para a mesma opcao tambem apaga
  const zerarQuestoes = (f: string = formato) => {
    setChaveQuestoes((k) => k + 1);
    const q = questaoVazia();
    setQuestoes([{ ...q, r: { ...q.r, tipo: f === "discursiva" ? "DISCURSIVO" : "OBJETIVO" } }]);
    setSugestoes([]);
  };
  const zerarIA = () => { setAssunto(""); setQuantidade(3); setInstrucoes(""); };
  const trocarFormato = (v: string) => {
    const novo = (v || "") as typeof formato;
    setFormato(novo);
    setTotalTxt(""); setChaveTotal((k) => k + 1);
    zerarQuestoes(novo);
    zerarIA();
  };

  const daSugestao = (s: SugestaoExercicioAPI): QuestaoNova => ({
    r: {
      tipo: s.alternativas.length ? "OBJETIVO" : "DISCURSIVO", enunciado: s.enunciado,
      alternativas: s.alternativas.length ? s.alternativas : ["", "", "", ""], correta: s.resposta_correta,
      respostasExemplo: [s.resposta_exemplo ?? ""], explicacao: s.explicacao, daIA: true, respostaIA: false,
    },
    pontos: "", subtopico: "",
  });
  const adicionar = (lista: SugestaoExercicioAPI[]) => {
    setQuestoes((qs) => [...qs.filter((q) => q.r.enunciado.trim() || q.r.alternativas.some((a) => a.trim())), ...lista.map(daSugestao)]);
    setSugestoes((x) => x.filter((s) => !lista.includes(s)));
    setAba("escrever");
    notify("Questões copiadas para “Escrever eu mesmo”. Revise, dê os pontos e salve.");
  };

  const gerar = async () => {
    if (!materiaId) return setError("Escolha a matéria.");
    if (!assunto.trim()) return setError("Escreva o tema para a IA.");
    setGerando(true); setError(""); setSugestoes([]);
    try {
      setSugestoes(await sugerirExercicios({ materia_id: materiaId, assunto: assunto.trim(),
        tipo: formato === "discursiva" ? "DISCURSIVO" : "OBJETIVO", quantidade, instrucoes: instrucoes.trim() || undefined }));
    } catch (e) { setError(e instanceof Error ? e.message : "A IA não conseguiu gerar agora. Tente de novo."); }
    finally { setGerando(false); }
  };

  const iaSugereResposta = async (i: number) => {
    const q = questoes[i];
    if (!materiaId) return setError("Escolha a matéria antes de pedir para a IA.");
    if (!q.r.enunciado.trim()) return setError("Escreva o enunciado antes de pedir a resposta para a IA.");
    setSugerindo(i); setError("");
    try {
      const { resposta_exemplo } = await sugerirRespostaExemplo({ materia_id: materiaId, enunciado: q.r.enunciado });
      // preenche a primeira vazia; se todas estao preenchidas, entra como mais uma
      const vazia = q.r.respostasExemplo.findIndex((x) => !x.trim());
      const lista = vazia >= 0 ? q.r.respostasExemplo.map((x, k) => (k === vazia ? resposta_exemplo : x))
        : [...q.r.respostasExemplo, resposta_exemplo].slice(0, MAX_EXEMPLOS);
      setQ(i, { r: { ...q.r, respostasExemplo: lista, respostaIA: true } });
    } catch (e) { setError(e instanceof Error ? e.message : "A IA não conseguiu sugerir agora."); }
    finally { setSugerindo(null); }
  };

  const salvar = () => {
    if (!titulo.trim()) return setError("Dê um título para a atividade.");
    if (!turmaIds.length || !materiaId || !tipo) return setError("Escolha ao menos uma turma, a matéria e o tipo.");
    if (exigeGabarito && !formato) return setError("Escolha o tipo das questões (objetiva ou discursiva).");
    let questoesValidas: { enunciado: string; resposta_correta: string; alternativas?: string[]; subtopico?: string; valor?: number }[] = [];
    let figuras: (File | undefined)[] = [];
    if (exigeGabarito) {
      if (!(total > 0)) return setError("Informe o total de pontos da atividade.");
      const feitas = questoes; // nenhuma questão pode ficar vazia
      if (!feitas.length) return setError("Adicione ao menos uma questão.");
      const comPontos = feitas.filter((q) => Number(q.pontos) > 0);
      if (comPontos.length && comPontos.length < feitas.length)
        return setError("Dê pontos a todas as questões, ou deixe todas em branco para dividir o total igualmente.");
      const soma = comPontos.reduce((t, q) => t + Number(q.pontos), 0);
      if (comPontos.length && Math.abs(soma - total) > 0.05)
        return setError(`A soma dos pontos das questões (${soma}) precisa ser igual ao total da atividade (${total}).`);
      for (const [i, q] of feitas.entries()) {
        const n = `Questão ${i + 1}`;
        if (!q.r.enunciado.trim()) return setError(`${n}: escreva o enunciado.`);
        if (formato === "objetiva") {
          const alts = q.r.alternativas.map((a) => a.trim());
          if (alts.length < 2 || alts.some((a) => !a)) return setError(`${n}: preencha todas as alternativas (ou remova as vazias).`);
          if (q.r.correta === null || q.r.correta >= alts.length) return setError(`${n}: marque qual alternativa é a correta.`);
        } else if (!respostaDe(q)) return setError(`${n}: escreva a resposta de exemplo ou clique em “IA sugere”.`);
      }
      questoesValidas = feitas.map((q) => formato === "objetiva"
        ? { enunciado: q.r.enunciado.trim(), resposta_correta: "ABCDE"[q.r.correta!], alternativas: q.r.alternativas.map((a) => a.trim()),
            subtopico: q.subtopico.trim() || undefined, valor: Number(q.pontos) || undefined }
        : { enunciado: q.r.enunciado.trim(), resposta_correta: respostaDe(q),
            subtopico: q.subtopico.trim() || undefined, valor: Number(q.pontos) || undefined });
      figuras = feitas.map((q) => q.figura);
    }
    setSalvando(true);
    setError("");
    criarAtividadesLote({
      materia_id: materiaId,
      turma_ids: turmaIds,
      titulo: titulo.trim(),
      tipo: tipo === "PROVA" ? (formato === "objetiva" ? "PROVA_OBJETIVA" : "PROVA_DISCURSIVA") : (tipo as AtividadeAPI["tipo"]),
      questoes: exigeGabarito ? questoesValidas : undefined,
      valor_total: exigeGabarito ? total : undefined,
      prazo: prazo || undefined,
      assunto_id: assuntoId || undefined,
    })
      .then(async (criadas) => {
        // as questoes saem como Q1, Q2... na ordem em que foram enviadas; a figura sobe em cada atividade criada
        const falhas: string[] = [];
        for (const criada of criadas) {
          for (const [i, figura] of figuras.entries()) {
            if (!figura) continue;
            await anexarFiguraQuestao(criada.id, `Q${i + 1}`, figura).catch(() => falhas.push(`Q${i + 1} (${criada.turma})`));
          }
        }
        const quantas = criadas.length === 1 ? "Atividade criada" : `${criadas.length} atividades criadas (uma por turma)`;
        notify(
          falhas.length
            ? `${quantas}, mas a figura de ${falhas.join(", ")} não subiu. Anexe de novo pela edição.`
            : `${quantas}. Os alunos já podem enviar.`,
        );
        onCriada();
      })
      .catch((erro) =>
        setError(erro instanceof Error ? erro.message : "Não foi possível criar a atividade."),
      )
      .finally(() => setSalvando(false));
  };

  return (
    <>
      <Card>
        {carregando ? (
          <p className="muted">Carregando turmas e matérias...</p>
        ) : !turmas!.length ? (
          <Empty
            title="Nenhuma turma disponível"
            text="Peça para um gestor cadastrar sua turma antes de criar atividades."
          />
        ) : (
          <>
            <div className="form-grid">
              <label>
                Título
                <input
                  value={titulo}
                  onChange={(e) => setTitulo(e.target.value)}
                  placeholder="Ex.: Redação 2 - meio ambiente"
                />
              </label>
              <label>
                Prazo de entrega (opcional, aparece no calendário)
                <input type="date" value={prazo} onChange={(e) => setPrazo(e.target.value)} />
              </label>
              <label>
                Turmas (uma atividade para cada escolhida)
                <SeletorMultiplo todos="Selecionar todos" rotulo="Turmas" placeholder="Escolha as turmas"
                  opcoes={turmas!.map((t) => ({ valor: t.id, rotulo: t.nome }))} valores={turmaIds} onChange={setTurmaIds} />
              </label>
              <label>
                Matéria
                <Escolha value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
                  <option value="">Escolha a matéria</option>
                  {materias!.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.nome}
                    </option>
                  ))}
                </Escolha>
              </label>
              <SeletorAssunto materiaId={materiaId} value={assuntoId} onChange={setAssuntoId} />
              <label>
                Tipo
                <Escolha value={tipo} onChange={(e) => { setTipo(e.target.value as typeof tipo); zerarQuestoes(); }}>
                  <option value="">Escolha o tipo</option>
                  {TIPOS_ATIVIDADE.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </Escolha>
              </label>
            </div>

            {exigeGabarito && (
              <>
                <div className="form-grid">
                  <div>
                    <p className="rotulo-escolha">Como criar</p>
                    <Seletor rotulo="Como criar" placeholder="Escolha como criar"
                      opcoes={[{ valor: "escrever", rotulo: "Escrever eu mesmo" }, { valor: "ia", rotulo: "Pedir para a IA" }]}
                      valor={aba ?? ""} onChange={(v) => { setAba((v || null) as typeof aba); setFormato(""); setTotalTxt(""); setChaveTotal((k) => k + 1); zerarQuestoes(""); zerarIA(); }} />
                  </div>
                  {aba !== null && (
                    <div>
                      <p className="rotulo-escolha">Tipo das questões</p>
                      <Seletor rotulo="Tipo das questões" placeholder="Escolha o tipo"
                        opcoes={[{ valor: "objetiva", rotulo: "Objetivo (alternativas)" }, { valor: "discursiva", rotulo: "Discursivo (o aluno escreve)" }]}
                        valor={formato} onChange={trocarFormato} />
                    </div>
                  )}
                </div>
                {aba !== null && (
                  <>
                    <p className="tiny muted">
                      {formato === "objetiva"
                        ? "O aluno marca a alternativa na tela e a correção sai na hora, comparando com o gabarito (sem IA)."
                        : formato === "discursiva"
                          ? "A IA corrige comparando a resposta do aluno com a resposta de exemplo de cada questão; você revisa e dá a nota final."
                          : ""}
                    </p>
                  </>
                )}
                {aba !== null && formato && (
                  <>
                    <p className="rotulo-escolha">Total de pontos da atividade</p>
                    <PontosSeletor key={chaveTotal} rotulo="Total de pontos" valor={totalTxt} onChange={setTotalTxt} opcoes={["10"]} placeholder="Escolha o total" />
                    <p className="tiny muted">
                      Preencha os pontos de todas as questões (a soma tem que fechar o total) ou deixe todas em branco para dividir igualmente.
                      {somaDadas > 0 ? ` Já distribuídos: ${somaDadas} de ${total || "?"}.` : ""}
                    </p>
                  </>
                )}
                {aba === "escrever" && formato && total > 0 && (
                  <>
                    {questoes.map((q, i) => (
                      <div className="meta-linha" key={`${chaveQuestoes}-${i}`}>
                        <div className="meta-topo">
                          <strong>Questão {i + 1}</strong>
                          {questoes.length > 1 && (
                            <button type="button" className="botao-pequeno perigo" onClick={() => setQuestoes(questoes.filter((_, j) => j !== i))}>
                              <Trash2 size={14} /> Remover questão
                            </button>
                          )}
                        </div>
                        <div className="form-grid ex-form">
                          <div>
                            <p className="rotulo-escolha">Pontos desta questão</p>
                            <PontosSeletor rotulo={`Pontos da questão ${i + 1}`} valor={q.pontos} onChange={(v) => setQ(i, { pontos: v })}
                              opcoes={PONTOS_QUESTAO} placeholder="Dividir o que sobrar" />
                          </div>
                          <label>
                            Submatéria (opcional)
                            <input value={q.subtopico} placeholder="Ex.: Equação do 1º grau. Em branco: a IA identifica."
                              onChange={(e) => setQ(i, { subtopico: e.target.value })} />
                          </label>
                          <label className="span-2">
                            Figura da questão (opcional)
                            <input type="file" accept="image/*" onChange={(e) => setQ(i, { figura: e.target.files?.[0] })} />
                            {q.figura && (
                              <img src={URL.createObjectURL(q.figura)} alt="Pré-visualização da figura"
                                style={{ maxWidth: "100%", maxHeight: 220, display: "block", marginTop: 8 }} />
                            )}
                          </label>
                        </div>
                        <EditorQuestao r={q.r} setR={(r) => setQ(i, { r })} comExplicacao={false}
                          sugerindoResposta={sugerindo === i} onSugerirResposta={() => iaSugereResposta(i)} />
                      </div>
                    ))}
                    <div className="form-actions left">
                      <Button variant="secondary" icon={Plus} onPress={() => setQuestoes([...questoes, questaoVazia()])}>
                        Adicionar questão
                      </Button>
                    </div>
                  </>
                )}
                {aba === "ia" && formato && total > 0 && (
                  <>
                    <div className="form-grid">
                      <label>Tema para a IA
                        <input value={assunto} onChange={(e) => setAssunto(e.target.value)} placeholder="Ex.: Função afim, Porcentagem, Coesão" />
                      </label>
                      <label>Quantas questões
                        <Escolha value={quantidade} onChange={(e) => setQuantidade(Number(e.target.value))}>
                          {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
                        </Escolha>
                      </label>
                      <label className="span-2">Pedido para a IA (opcional)
                        <textarea rows={2} value={instrucoes} onChange={(e) => setInstrucoes(e.target.value)}
                          placeholder="Ex.: nível fácil, usar situações do dia a dia, estilo ENEM" />
                      </label>
                    </div>
                    <p className="tiny muted">A IA só cria rascunhos. Nada chega ao aluno até você salvar a atividade.</p>
                    <div className="form-actions left">
                      <Button icon={Sparkles} disabled={gerando} onPress={gerar}>
                        {gerando ? "A IA está criando..." : sugestoes.length ? "Gerar de novo" : "Gerar sugestões"}
                      </Button>
                      {sugestoes.length > 1 && (
                        <Button variant="secondary" icon={Check} onPress={() => adicionar(sugestoes)}>Adicionar todas</Button>
                      )}
                    </div>
                    {sugestoes.map((s, i) => (
                      <div className="meta-linha" key={`${i}-${s.titulo}`}>
                        <div className="meta-topo">
                          <strong>{s.titulo}</strong>
                          <Badge tone="neutral">{s.alternativas.length ? "Objetivo" : "Discursivo"}</Badge>
                        </div>
                        <p className="exercicio-preview">{s.enunciado}</p>
                        {s.alternativas.length > 0 ? (
                          <ol className="lista-alternativas">
                            {s.alternativas.map((a, k) => (
                              <li key={k} className={k === s.resposta_correta ? "certa" : ""}>
                                <b>{"ABCDEF"[k]})</b> {a} {k === s.resposta_correta && <Badge>Correta</Badge>}
                              </li>
                            ))}
                          </ol>
                        ) : (
                          <p className="tiny"><b>Resposta de exemplo:</b> {s.resposta_exemplo}</p>
                        )}
                        <div className="form-actions left">
                          <Button icon={Check} onPress={() => adicionar([s])}>Adicionar à atividade</Button>
                        </div>
                      </div>
                    ))}
                  </>
                )}
              </>
            )}

            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <div className="form-actions">
              <Button variant="secondary" onPress={onBack}>Cancelar</Button>
              <Button disabled={salvando} onPress={salvar}>
                {salvando ? "Criando..." : "Criar atividade"}
              </Button>
            </div>
          </>
        )}
      </Card>
    </>
  );
}

// dentro da atividade: cada aluno da turma, com o status do envio (ou "Não enviou")
function EnviosDaAtividade({ grupo: g, onBack, abrir }: { grupo: GrupoAtividade; onBack: () => void; abrir: (submissaoId: string) => void }) {
  const [aba, setAba] = useState<"todos" | "enviaram" | "faltam">("todos");
  const faltam = g.alunos.length - enviaram(g);
  const alunos = g.alunos.filter((a) => aba === "todos" || (aba === "enviaram" ? a.envio : !a.envio));
  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar às atividades
      </button>
      <div className="page-heading">
        <div>
          <Badge tone="neutral">{g.materia}</Badge>
          <h1 className="detail-heading">{g.titulo}</h1>
          <p>
            {g.turmaNome} · {enviaram(g)} de {g.alunos.length} enviaram
            {g.prazo && ` · prazo ${g.prazo.split("-").reverse().join("/")}`}
          </p>
        </div>
      </div>
      <Card>
        <div className="list-toolbar">
          <div className="tabs" role="group" aria-label="Filtrar alunos">
            {([["todos", `Todos (${g.alunos.length})`], ["enviaram", `Enviaram (${enviaram(g)})`], ["faltam", `Não enviaram (${faltam})`]] as const).map(([id, label]) => (
              <button key={id} aria-pressed={aba === id} className={aba === id ? "active" : ""} onClick={() => setAba(id)}>
                {label}
              </button>
            ))}
          </div>
        </div>
        {alunos.length ? alunos.map((a) => {
          const e = a.envio;
          return e ? (
            <button key={a.id} className="activity-row" onClick={() => abrir(e.id)}>
              <span className="activity-info">
                <strong>{a.nome}</strong>
                <span>Enviou em {e.date}</span>
              </span>
              <Badge tone={e.status === "aprovada" ? "green" : e.status === "corrigida_ia" ? "blue" : "amber"}>
                {e.status === "aprovada" ? "Corrigida" : e.status === "corrigida_ia" ? "Corrigida pela IA" : "Enviada"}
              </Badge>
              {e.status === "aprovada" && e.scores && <span className="row-score">{e.scores[0]}</span>}
              <ArrowUpRight size={18} />
            </button>
          ) : (
            <div key={a.id} className="activity-row" style={{ cursor: "default" }}>
              <span className="activity-info">
                <strong>{a.nome}</strong>
                <span>Ainda não enviou</span>
              </span>
              <Badge tone="neutral">Não enviou</Badge>
            </div>
          );
        }) : <Empty title="Ninguém por aqui" text="Escolha outro filtro." />}
      </Card>
    </>
  );
}

// o aluno le, alem do comentario do professor, cada acerto/erro que a IA apontou (trecho + explicacao)
function ComentariosDaIA({ criterios }: { criterios: { codigo: string; nome: string; pontos: Ponto[] }[] }) {
  const com = criterios.filter((c) => c.pontos.some((p) => p.comentario));
  if (!com.length) return null;
  return (
    <div className="comentarios-ia">
      <h3>Comentários da IA</h3>
      {com.map((c) => (
        <div key={c.codigo}>
          <strong>{c.nome}</strong>
          <ul>
            {c.pontos.filter((p) => p.comentario).map((p, k) => (
              <li key={k} className={p.tipo === "acerto" ? "ia-acerto" : "ia-erro"}>
                <Badge tone={p.tipo === "acerto" ? "green" : "amber"}>{p.tipo === "acerto" ? "Acerto" : "A melhorar"}</Badge>{" "}
                {p.trecho && <em>“{p.trecho}” </em>}
                {p.comentario}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
