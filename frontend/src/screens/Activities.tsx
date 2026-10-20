import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Check,
  FileText,
  Plus,
  Search,
  Send,
  Sparkles,
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
  // professor autenticado de verdade revisa a fila real de submissoes
  const real = !!currentUser && role === "aluno";
  const realProfessor = !!currentUser && role === "professor" && !!reviewOnly;
  const [realActivities, setRealActivities] = useState<Activity[] | null>(null);
  const [loadingReal, setLoadingReal] = useState(real || realProfessor);
  const recarregar = () => {
    if (real && currentUser) {
      setLoadingReal(true);
      carregarAtividadesDoAluno(currentUser.nome)
        .then(setRealActivities)
        .catch(() => notify("Não foi possível carregar suas atividades."))
        .finally(() => setLoadingReal(false));
    } else if (realProfessor) {
      setLoadingReal(true);
      carregarRevisoes()
        .then(setRealActivities)
        .catch(() => notify("Não foi possível carregar a fila de revisão."))
        .finally(() => setLoadingReal(false));
    }
  };
  useEffect(recarregar, [real, realProfessor, currentUser?.id]);
  const activities = real || realProfessor ? (realActivities ?? []) : state.activities;
  const activity = activities.find((a) => a.id === selected);
  if ((real || realProfessor) && loadingReal && !activity)
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
  if (activity && realProfessor)
    return (
      <RevisaoReal
        key={activity.id}
        activity={activity}
        onBack={() => select(null)}
        onApproved={() => { select(null); recarregar(); }}
      />
    );
  if (activity)
    return (
      <ActivityDetail
        key={activity.id + activity.status}
        activity={activity}
        state={state}
        role={role}
        update={update}
        notify={notify}
        onBack={() => select(null)}
        onSubmittedReal={real ? () => { select(null); recarregar(); } : undefined}
      />
    );
  const list = activities.filter(
    (a) =>
      (!reviewOnly || a.status !== "disponivel") &&
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
}: Omit<Props, "selected" | "select" | "reviewOnly" | "currentUser"> & {
  activity: Activity;
  onBack: () => void;
  onSubmittedReal?: () => void;
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
            <p className="muted">
              {a.kind === "redacao"
                ? "Escreva um texto dissertativo-argumentativo sobre o tema. Defenda seu ponto de vista e apresente uma proposta de intervenção."
                : "Explique como a função f(x) = 2x + 5 representa o preço de uma corrida. Calcule o preço para 4 km e descreva seu raciocínio."}
            </p>
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
      ) : a.status === "pendente" && !teacher ? (
        <Card>
          <Empty
            title="Recebemos sua atividade!"
            text="Seu professor vai revisar a correção. Assim que ele aprovar, você encontra a nota e as orientações nesta tela."
          >
            <Badge tone="amber">Aguardando revisão do professor</Badge>
            <Button variant="secondary" onPress={onBack}>
              Voltar às atividades
            </Button>
          </Empty>
        </Card>
      ) : (
        visibleResult(a, role) && (
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
                  ? "Revisada pela professora Marina"
                  : "Sugestão demonstrativa da IA · confiança média"}
              </Badge>
              <div className="score-total">
                <strong>{scores.reduce((s, n) => s + n, 0)}</strong>
                <span>/ {a.kind === "redacao" ? "1000" : "10"} pontos</span>
              </div>
              <div className="criteria-grid">
                {scores.map((n, i) => (
                  <label key={i}>
                    <span>{a.kind === "redacao" ? `C${i + 1}` : "Nota"}</span>
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
}: {
  activity: Activity;
  onBack: () => void;
  onApproved: () => void;
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
                <Button icon={Sparkles} disabled={corrigindo} onPress={gerarCorrecao}>
                  {corrigindo ? "Gerando correção..." : "Gerar correção com IA"}
                </Button>
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
                  <span>/ 1000 pontos</span>
                </div>
                <div className="criteria-grid">
                  {correcao.criterios.map((c) => (
                    <label key={c.codigo}>
                      <span>{c.codigo}</span>
                      {!aprovada ? (
                        <select
                          aria-label={`Nota da competência ${c.codigo}`}
                          value={notas[c.codigo] ?? c.nota}
                          onChange={(e) =>
                            setNotas({ ...notas, [c.codigo]: Number(e.target.value) })
                          }
                        >
                          {NOTAS_ENEM.map((v) => (
                            <option key={v}>{v}</option>
                          ))}
                        </select>
                      ) : (
                        <strong>{notas[c.codigo]}</strong>
                      )}
                      <small>{c.nome}</small>
                    </label>
                  ))}
                </div>
                <h3>{aprovada ? "Orientação enviada" : "Orientação ao aluno"}</h3>
                {!aprovada ? (
                  <textarea
                    aria-label="Feedback do professor"
                    className="text-area"
                    placeholder="Explique os pontos fortes e indique o que o aluno pode melhorar..."
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                  />
                ) : (
                  <p className="feedback-text">{feedback}</p>
                )}
                {error && (
                  <p role="alert" className="error">
                    {error}
                  </p>
                )}
                {!aprovada &&
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

const TIPOS_ATIVIDADE: { value: string; label: string }[] = [
  { value: "REDACAO", label: "Redação" },
  { value: "PROVA_DISCURSIVA", label: "Prova discursiva" },
  { value: "PROVA_OBJETIVA", label: "Prova objetiva" },
  { value: "EXERCICIO", label: "Exercício" },
];

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
  const [error, setError] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    Promise.all([listarTurmasMinhas(), listarMaterias()]).then(([t, m]) => {
      setTurmas(t);
      setMaterias(m);
      setTurmaId(t[0]?.id ?? "");
      setMateriaId(m[0]?.id ?? "");
    });
  }, []);

  const carregando = turmas === null || materias === null;

  const salvar = () => {
    if (!titulo.trim()) {
      setError("Dê um título para a atividade.");
      return;
    }
    if (!turmaId || !materiaId) {
      setError("Escolha uma turma e uma matéria.");
      return;
    }
    setSalvando(true);
    setError("");
    criarAtividade({
      materia_id: materiaId,
      turma_id: turmaId,
      titulo: titulo.trim(),
      tipo: tipo as AtividadeAPI["tipo"],
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
        ) : !turmas!.length || !materias!.length ? (
          <Empty
            title="Nenhuma turma ou matéria disponível"
            text="Peça para um gestor cadastrar sua turma e a matéria da escola antes de criar atividades."
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
