import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Check,
  FileText,
  Plus,
  Search,
  Send,
  Sparkles,
  Trash2,
  Upload,
  ShieldCheck,
} from "lucide-react";
import { TextInput } from "react-native";
import { ActivityRow } from "./Dashboard";
import { Badge, Button, Card, Empty, SectionTitle } from "../components/ui";
import type { Activity, DemoState, Role } from "../types";
import {
  approveActivity,
  validScores,
  visibleResult,
} from "../services/demoStore";
import {
  aprovarCorrecao,
  corrigirSubmissao,
  criarAtividade,
  criarMateria,
  enviarTexto,
  listarMaterias,
  listarTurmasMinhas,
  verCorrecao,
  verSubmissao,
  type AtividadeAPI,
  type CorrecaoAPI,
  type MateriaAPI,
  type TurmaAPI,
} from "../services/api";
import { carregarAtividadesDoAluno } from "../services/atividades";
import { carregarRevisoes } from "../services/revisoes";
import type { UsuarioAtual } from "../services/api";

type Props = {
  state: DemoState;
  role: Role;
  update: (fn: (s: DemoState) => DemoState) => void;
  notify: (s: string) => void;
  selected: string | null;
  select: (id: string | null) => void;
  reviewOnly?: boolean;
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
  currentUser,
}: Props) {
  const [filter, setFilter] = useState("todas");
  const [search, setSearch] = useState("");
  const [criando, setCriando] = useState(false);
  // modo real: aluno autenticado de verdade manda/ve suas proprias atividades;
  // professor/gestor autenticado de verdade ve a fila real de submissoes (so o professor corrige/aprova, RN-01)
  const real = !!currentUser && role === "aluno";
  const realProfessor = !!currentUser && role === "professor" && !!reviewOnly;
  const realReviewer = !!currentUser && (role === "professor" || role === "gestor") && !!reviewOnly;
  const [realActivities, setRealActivities] = useState<Activity[] | null>(null);
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
        .then(setRealActivities)
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
  if (realProfessor && criando)
    return (
      <NovaAtividade
        onBack={() => setCriando(false)}
        onCriada={() => { setCriando(false); recarregar(); }}
        notify={notify}
      />
    );
  if (activity && realReviewer)
    return activity.status === "disponivel" ? (
      <AtividadeSemEnvio key={activity.id} activity={activity} onBack={() => select(null)} />
    ) : (
      <RevisaoReal
        key={activity.id}
        activity={activity}
        onBack={() => select(null)}
        onApproved={() => { select(null); recarregar(); }}
        readOnly={role === "gestor"}
      />
    );
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
  const list = activities.filter(
    (a) =>
      (filter === "todas" || a.status === filter) &&
      `${a.title} ${a.subject}`.toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            {reviewOnly ? "O SEU OLHAR IMPORTA" : "PRATICAR PARA EVOLUIR"}
          </div>
          <h1>{reviewOnly ? "Revisões" : "Minhas atividades"}</h1>
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
          <div className="tabs" role="group" aria-label="Filtrar atividades">
            {[
              ["todas", "Todas"],
              ...(!reviewOnly ? [["disponivel", "Para fazer"]] : []),
              ["pendente", "Em revisão"],
              ["aprovada", "Corrigidas"],
            ].map(([id, label]) => (
              <button
                key={id}
                aria-pressed={filter === id}
                className={filter === id ? "active" : ""}
                onClick={() => setFilter(id)}
              >
                {label}
              </button>
            ))}
          </div>
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
        {list.length ? (
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
                setFilter("todas");
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
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<"texto" | "arquivo">("texto");
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [scores, setScores] = useState(
    a.scores ||
      a.aiScores ||
      (a.kind === "redacao" ? [160, 160, 120, 140, 160] : [8]),
  );
  const [feedback, setFeedback] = useState(a.feedback || "");
  const [confirmApproval, setConfirmApproval] = useState(false);
  const [gerandoCorrecao, setGerandoCorrecao] = useState(false);
  const [erroCorrecao, setErroCorrecao] = useState("");
  const gerarMinhaCorrecao = async () => {
    setGerandoCorrecao(true);
    setErroCorrecao("");
    try {
      await corrigirSubmissao(a.id);
      onCorrigidaReal?.();
    } catch (erro) {
      setErroCorrecao(erro instanceof Error ? erro.message : "Não foi possível gerar a correção.");
    } finally {
      setGerandoCorrecao(false);
    }
  };
  const submit = async () => {
    if (mode === "texto" && text.trim().length < 40) {
      setError("Escreva pelo menos 40 caracteres para enviar sua resposta.");
      return;
    }
    if (mode === "arquivo" && !file) {
      setError("Escolha um PDF ou uma imagem para continuar.");
      return;
    }
    if (!confirmed) {
      setError("Confirme que você revisou o conteúdo antes de enviar.");
      return;
    }
    if (onSubmittedReal) {
      if (mode === "arquivo") {
        setError("Envio de foto/PDF ainda não está conectado ao backend. Use o modo texto.");
        return;
      }
      setEnviando(true);
      try {
        await enviarTexto(a.id, text);
        update((s) => ({ ...s, drafts: { ...s.drafts, [a.id]: "" } }));
        notify("Redação enviada. Agora ela aguarda a correção do professor.");
        onSubmittedReal();
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
              fileName: mode === "arquivo" ? file?.name : undefined,
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
          <p>{teacher ? `${a.student} · Turma Pré-ENEM A` : a.date}</p>
        </div>
      </div>
      {a.status === "disponivel" ? (
        <div className="detail-grid">
          <Card>
            <SectionTitle title="Sua resposta" />
            {a.questoes?.length ? (
              // gabarito real desta atividade (materias de exatas) -- nunca um texto fixo de outra atividade
              <ol className="question-list">
                {a.questoes.map((q) => (
                  <li key={q.codigo}>{q.enunciado}</li>
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
                <TextInput
                  accessibilityLabel="Texto da atividade"
                  placeholder="Suas ideias começam aqui..."
                  multiline
                  value={text}
                  onChangeText={(v) => {
                    setText(v);
                    update((s) => ({
                      ...s,
                      drafts: { ...s.drafts, [a.id]: v },
                    }));
                  }}
                  style={{
                    minHeight: 300,
                    fontFamily: "IBM Plex Sans",
                    fontSize: 16,
                    lineHeight: 27,
                    padding: 18,
                    borderWidth: 1,
                    borderColor: "#DCD8CC",
                    borderRadius: 10,
                    textAlignVertical: "top",
                    color: "#141A2E",
                  }}
                />
                <div className="field-meta">
                  <span>Rascunho salvo neste navegador</span>
                  <span>{text.length} caracteres</span>
                </div>
              </>
            ) : (
              <div className="upload-zone">
                <Upload size={30} />
                <strong>{file?.name || "Escolha sua atividade"}</strong>
                <span>PDF, JPG ou PNG · até 10 MB</span>
                <input
                  aria-label="Selecionar arquivo da atividade"
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (
                      f &&
                      (f.size > 10 * 1024 * 1024 ||
                        !/\.(pdf|png|jpe?g)$/i.test(f.name))
                    ) {
                      setError("Use PDF, JPG ou PNG com no máximo 10 MB.");
                      setFile(null);
                      e.target.value = "";
                    } else {
                      setFile(f || null);
                      setError("");
                    }
                  }}
                />
                <p className="tiny">
                  Nesta demonstração, somente o nome do arquivo é salvo. A
                  leitura do manuscrito será conectada ao backend.
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
          </Card>
          <Card className="aside-card">
            <ShieldCheck size={29} color="#197451" />
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
              <Badge tone={a.status === "aprovada" ? "green" : "amber"}>
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
                      <select
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
                      </select>
                    ) : (
                      <strong>{n}</strong>
                    )}
                    <small>
                      {a.kind === "redacao"
                        ? [
                            "Norma culta",
                            "Tema",
                            "Argumentação",
                            "Coesão",
                            "Intervenção",
                          ][i]
                        : "Raciocínio"}
                    </small>
                  </label>
                ))}
              </div>
              <h3>
                {teacher && a.status !== "aprovada"
                  ? "Orientação ao aluno"
                  : "O próximo passo na sua escrita"}
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
                {a.text || (
                  <>
                    <FileText size={24} />
                    <p>{a.fileName}</p>
                    <p>
                      O arquivo não é armazenado neste protótipo. A visualização
                      e o OCR dependem da integração.
                    </p>
                  </>
                )}
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
}: {
  activity: Activity;
  onBack: () => void;
  onApproved: () => void;
  readOnly?: boolean;
}) {
  const [texto, setTexto] = useState<string | null>(null);
  const [correcao, setCorrecao] = useState<CorrecaoAPI | null>(null);
  const [notas, setNotas] = useState<Record<string, number>>({});
  const [feedback, setFeedback] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [corrigindo, setCorrigindo] = useState(false);
  const [aprovando, setAprovando] = useState(false);
  const [confirmApproval, setConfirmApproval] = useState(false);
  const [error, setError] = useState("");

  const aplicarCorrecao = (c: CorrecaoAPI) => {
    setCorrecao(c);
    setFeedback(c.feedback ?? "");
    setNotas(Object.fromEntries(c.criterios.map((cr) => [cr.codigo, cr.nota_professor ?? cr.nota])));
  };

  useEffect(() => {
    let ativo = true;
    Promise.all([verSubmissao(a.id), verCorrecao(a.id).catch(() => null)]).then(([s, c]) => {
      if (!ativo) return;
      setTexto(s.texto_confirmado ?? s.texto_ocr ?? "");
      if (c) aplicarCorrecao(c);
      setCarregando(false);
    });
    return () => {
      ativo = false;
    };
  }, [a.id]);

  const gerarCorrecao = () => {
    setCorrigindo(true);
    setError("");
    corrigirSubmissao(a.id)
      .then(aplicarCorrecao)
      .catch((erro) =>
        setError(erro instanceof Error ? erro.message : "Não foi possível gerar a correção."),
      )
      .finally(() => setCorrigindo(false));
  };

  const aprovar = () => {
    setAprovando(true);
    setError("");
    aprovarCorrecao(
      a.id,
      Object.entries(notas).map(([codigo, nota]) => ({ codigo, nota })),
      feedback,
    )
      .then(() => onApproved())
      .catch((erro) => {
        setError(erro instanceof Error ? erro.message : "Não foi possível aprovar.");
        setConfirmApproval(false);
      })
      .finally(() => setAprovando(false));
  };

  const aprovada = a.status === "aprovada";
  const nota = Object.values(notas).reduce((s, n) => s + n, 0);

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
                <p className="muted">Esta redação ainda não tem correção da IA.</p>
                {!readOnly && (
                  <Button icon={Sparkles} disabled={corrigindo} onPress={gerarCorrecao}>
                    {corrigindo ? "Gerando correção..." : "Gerar correção com IA"}
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
                    : `Sugestão da IA · confiança ${Math.round(correcao.confianca * 100)}%`}
                </Badge>
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
                    const valorPorQuestao = (a.valorTotal ?? 1000) / correcao.criterios.length;
                    const niveis = exatas
                      ? [0, 0.2, 0.4, 0.6, 0.8, 1].map((f) => Math.round(f * valorPorQuestao * 100) / 100)
                      : NOTAS_ENEM;
                    return (
                      <label key={c.codigo}>
                        <span>{c.codigo}</span>
                        {!aprovada && !readOnly ? (
                          <select
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
                          </select>
                        ) : (
                          <strong>{notas[c.codigo]}</strong>
                        )}
                        <small>{c.nome}</small>
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
          <Card>
            <SectionTitle title="Texto enviado" />
            <div className="essay">{texto}</div>
          </Card>
        </div>
      )}
    </>
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

const TIPOS_ATIVIDADE: { value: string; label: string }[] = [
  { value: "REDACAO", label: "Redação" },
  { value: "PROVA_DISCURSIVA", label: "Prova discursiva" },
  { value: "PROVA_OBJETIVA", label: "Prova objetiva" },
  { value: "EXERCICIO", label: "Exercício" },
];

const TIPOS_MATERIA: { value: MateriaAPI["tipo"]; label: string }[] = [
  { value: "MATERIA_OBJETIVA", label: "Exatas (matemática, física, química...)" },
  { value: "REDACAO_ENEM", label: "Redação ENEM" },
  { value: "REDACAO_OUTRO_VESTIBULAR", label: "Redação (outro vestibular)" },
  { value: "MATERIA_DISCURSIVA", label: "Outra matéria discursiva" },
];

// correcao por gabarito (nao e a rubrica de redacao): a atividade precisa das questoes e da
// resposta correta de cada uma
const MATERIAS_COM_GABARITO: MateriaAPI["tipo"][] = ["MATERIA_OBJETIVA", "MATERIA_DISCURSIVA"];

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
  const [turmaId, setTurmaId] = useState("");
  const [materiaId, setMateriaId] = useState("");
  const [titulo, setTitulo] = useState("");
  const [tipo, setTipo] = useState(TIPOS_ATIVIDADE[0].value);
  const [questoes, setQuestoes] = useState([{ enunciado: "", resposta_correta: "" }]);
  const [valorTotal, setValorTotal] = useState(1000);
  const [error, setError] = useState("");
  const [salvando, setSalvando] = useState(false);

  const [criandoMateria, setCriandoMateria] = useState(false);
  const [novaMateriaNome, setNovaMateriaNome] = useState("");
  const [novaMateriaTipo, setNovaMateriaTipo] = useState(TIPOS_MATERIA[0].value);
  const [salvandoMateria, setSalvandoMateria] = useState(false);

  const recarregarMaterias = () =>
    listarMaterias().then((m) => {
      setMaterias(m);
      return m;
    });

  useEffect(() => {
    Promise.all([listarTurmasMinhas(), listarMaterias()]).then(([t, m]) => {
      setTurmas(t);
      setMaterias(m);
      setTurmaId(t[0]?.id ?? "");
      setMateriaId(m[0]?.id ?? "");
    });
  }, []);

  const carregando = turmas === null || materias === null;
  const materiaSelecionada = materias?.find((m) => m.id === materiaId);
  const exigeGabarito = !!materiaSelecionada && MATERIAS_COM_GABARITO.includes(materiaSelecionada.tipo);
  // "Redação" como tipo da atividade nao faz sentido numa materia de exatas; troca so se o
  // professor ainda nao tiver escolhido outro tipo manualmente (evita rotular errado por engano)
  useEffect(() => {
    if (exigeGabarito && tipo === "REDACAO") setTipo("EXERCICIO");
  }, [exigeGabarito]);

  const criarNovaMateria = () => {
    if (!novaMateriaNome.trim()) {
      setError("Dê um nome para a matéria.");
      return;
    }
    setSalvandoMateria(true);
    setError("");
    criarMateria({ nome: novaMateriaNome.trim(), tipo: novaMateriaTipo })
      .then((nova) => recarregarMaterias().then(() => {
        setMateriaId(nova.id);
        setCriandoMateria(false);
        setNovaMateriaNome("");
      }))
      .catch((erro) => setError(erro instanceof Error ? erro.message : "Não foi possível criar a matéria."))
      .finally(() => setSalvandoMateria(false));
  };

  const salvar = () => {
    if (!titulo.trim()) {
      setError("Dê um título para a atividade.");
      return;
    }
    if (!turmaId || !materiaId) {
      setError("Escolha uma turma e uma matéria.");
      return;
    }
    const questoesValidas = questoes
      .map((q) => ({ enunciado: q.enunciado.trim(), resposta_correta: q.resposta_correta.trim() }))
      .filter((q) => q.enunciado && q.resposta_correta);
    if (exigeGabarito && !questoesValidas.length) {
      setError("Adicione ao menos uma questão com enunciado e resposta correta.");
      return;
    }
    if (exigeGabarito && (!valorTotal || valorTotal <= 0)) {
      setError("Informe o valor total da atividade.");
      return;
    }
    setSalvando(true);
    setError("");
    criarAtividade({
      materia_id: materiaId,
      turma_id: turmaId,
      titulo: titulo.trim(),
      tipo: tipo as AtividadeAPI["tipo"],
      questoes: exigeGabarito ? questoesValidas : undefined,
      valor_total: exigeGabarito ? valorTotal : undefined,
    })
      .then(() => {
        notify("Atividade criada. Os alunos da turma já podem enviar.");
        onCriada();
      })
      .catch((erro) =>
        setError(erro instanceof Error ? erro.message : "Não foi possível criar a atividade."),
      )
      .finally(() => setSalvando(false));
  };

  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar às revisões
      </button>
      <div className="page-heading">
        <div>
          <div className="eyebrow">PROPONHA O PRÓXIMO PASSO</div>
          <h1>Nova atividade</h1>
          <p>Crie uma atividade para a turma enviar.</p>
        </div>
      </div>
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
                Turma
                <select value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
                  {turmas!.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.nome}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Matéria
                <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
                  {materias!.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.nome}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Tipo
                <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
                  {TIPOS_ATIVIDADE.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {!criandoMateria ? (
              <Button variant="secondary" icon={Plus} onPress={() => setCriandoMateria(true)}>
                Nova matéria
              </Button>
            ) : (
              <Card>
                <SectionTitle title="Nova matéria" />
                <div className="form-grid">
                  <label>
                    Nome
                    <input
                      value={novaMateriaNome}
                      onChange={(e) => setNovaMateriaNome(e.target.value)}
                      placeholder="Ex.: Matemática"
                    />
                  </label>
                  <label>
                    Tipo
                    <select
                      value={novaMateriaTipo}
                      onChange={(e) => setNovaMateriaTipo(e.target.value as MateriaAPI["tipo"])}
                    >
                      {TIPOS_MATERIA.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="form-actions">
                  <Button variant="secondary" onPress={() => setCriandoMateria(false)}>
                    Cancelar
                  </Button>
                  <Button disabled={salvandoMateria} onPress={criarNovaMateria}>
                    {salvandoMateria ? "Salvando..." : "Criar matéria"}
                  </Button>
                </div>
              </Card>
            )}

            {exigeGabarito && (
              <Card>
                <SectionTitle title="Questões e gabarito" />
                <p className="tiny muted">
                  A IA corrige comparando a resposta do aluno com a resposta correta de cada
                  questão — não é uma avaliação subjetiva, é uma conferência lógica.
                </p>
                <label>
                  Valor total da atividade (pontos)
                  <input
                    type="number"
                    min={1}
                    value={valorTotal}
                    onChange={(e) => setValorTotal(Number(e.target.value))}
                  />
                </label>
                <p className="tiny muted">
                  Dividido igualmente entre as {questoes.length} questão(ões): {" "}
                  {(valorTotal / Math.max(questoes.length, 1)).toFixed(1)} pontos cada.
                </p>
                {questoes.map((q, i) => (
                  <div className="form-grid" key={i}>
                    <label>
                      {`Questão ${i + 1}`}
                      <input
                        value={q.enunciado}
                        onChange={(e) => {
                          const copia = [...questoes];
                          copia[i] = { ...copia[i], enunciado: e.target.value };
                          setQuestoes(copia);
                        }}
                        placeholder="Ex.: Resolva 2x + 3 = 7"
                      />
                    </label>
                    <label>
                      Resposta correta
                      <input
                        value={q.resposta_correta}
                        onChange={(e) => {
                          const copia = [...questoes];
                          copia[i] = { ...copia[i], resposta_correta: e.target.value };
                          setQuestoes(copia);
                        }}
                        placeholder="Ex.: x = 2"
                      />
                    </label>
                    {questoes.length > 1 && (
                      <button
                        className="back-link"
                        onClick={() => setQuestoes(questoes.filter((_, j) => j !== i))}
                      >
                        <Trash2 size={14} />
                        Remover questão
                      </button>
                    )}
                  </div>
                ))}
                <Button
                  variant="secondary"
                  icon={Plus}
                  onPress={() => setQuestoes([...questoes, { enunciado: "", resposta_correta: "" }])}
                >
                  Adicionar questão
                </Button>
              </Card>
            )}

            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <Button disabled={salvando} onPress={salvar}>
              {salvando ? "Criando..." : "Criar atividade"}
            </Button>
          </>
        )}
      </Card>
    </>
  );
}
