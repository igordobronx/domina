import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Check,
  FileText,
  Search,
  Send,
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
import { enviarTexto } from "../services/api";
import { carregarAtividadesDoAluno } from "../services/atividades";
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
  // modo real: aluno autenticado de verdade, dados vem do backend em vez do demoStore
  const real = !!currentUser && role === "aluno";
  const [realActivities, setRealActivities] = useState<Activity[] | null>(null);
  const [loadingReal, setLoadingReal] = useState(real);
  const recarregar = () => {
    if (!real || !currentUser) return;
    setLoadingReal(true);
    carregarAtividadesDoAluno(currentUser.nome)
      .then(setRealActivities)
      .catch(() => notify("Não foi possível carregar suas atividades."))
      .finally(() => setLoadingReal(false));
  };
  useEffect(recarregar, [real, currentUser?.id]);
  const activities = real ? (realActivities ?? []) : state.activities;
  const activity = activities.find((a) => a.id === selected);
  if (real && loadingReal && !activity)
    return (
      <Empty title="Carregando..." text="Buscando suas atividades no servidor." />
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
