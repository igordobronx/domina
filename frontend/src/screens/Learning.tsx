import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  X,
  RotateCcw,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { studyTasks } from "../data/demo";
import type { DemoState } from "../types";
import { Badge, Button, Card, Empty, Progress, SectionTitle } from "../components/ui";
import { RealSparkline } from "../components/Chart";
import {
  dominioMeu,
  evolucaoMinha,
  exerciciosDaTurma,
  meusExercicios,
  responderExercicio,
  type DominioAPI,
  type ExercicioAlunoAPI,
  type EvolucaoMateriaAPI,
  type ExercicioAPI,
  type UsuarioAtual,
} from "../services/api";

const HABILIDADE_NOME: Record<string, string> = {
  C1: "Norma culta",
  C2: "Compreensão do tema",
  C3: "Argumentação",
  C4: "Coesão textual",
  C5: "Proposta de intervenção",
};

// formato comum pro card/exercicio, seja ele gerado pelo backend ou (so no fallback sem
// conta real) um dos exercicios de demonstracao fixos em data/demo.ts
interface ExercicioComum {
  id: string;
  topic: string;
  type: string;
  title: string;
  description: string;
  question: string;
  options: string[];
  answer: number;
  explanation: string;
}

function doBackend(e: ExercicioAPI, i: number): ExercicioComum {
  return {
    id: `real-${i}`,
    topic: HABILIDADE_NOME[e.habilidade_codigo] ?? e.habilidade_codigo,
    type: "Gerado para você",
    title: e.titulo,
    description: `Baseado no seu desempenho real em ${e.habilidade_codigo}.`,
    question: e.enunciado,
    options: e.opcoes,
    answer: e.resposta_correta,
    explanation: e.explicacao,
  };
}
function doDemo(t: (typeof studyTasks)[number]): ExercicioComum {
  return {
    id: t.id,
    topic: t.topic,
    type: t.type,
    title: t.title,
    description: t.description,
    question: t.question,
    options: t.options,
    answer: t.answer,
    explanation: t.explanation,
  };
}

export function Evolution({ currentUser }: { currentUser?: UsuarioAtual | null }) {
  const [subject, setSubject] = useState("Todas");
  const [porMateria, setPorMateria] = useState<EvolucaoMateriaAPI[] | null>(null);
  const [dominio, setDominio] = useState<DominioAPI[] | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!currentUser) return;
    setCarregando(true);
    setErro("");
    Promise.all([evolucaoMinha(), dominioMeu()])
      .then(([ev, dom]) => {
        setPorMateria(ev);
        setDominio(dom);
      })
      .catch((e) => setErro(e instanceof Error ? e.message : "Não foi possível carregar sua evolução."))
      .finally(() => setCarregando(false));
  }, [currentUser?.id]);

  if (carregando) return <Empty title="Carregando sua evolução..." text="Isso leva só um instante." />;
  if (erro) return <Empty title="Ainda não dá para ver sua evolução" text={erro} />;

  const materias = porMateria ?? [];
  if (!materias.length) {
    return (
      <Empty
        title="Sua evolução aparece aqui em breve"
        text="Assim que o professor aprovar a primeira correção de uma atividade sua, o histórico desta matéria passa a aparecer aqui."
      />
    );
  }

  const subjects = ["Todas", ...materias.map((m) => m.materia)];
  const visiveis = subject === "Todas" ? materias : materias.filter((m) => m.materia === subject);
  const totalAtividades = visiveis.reduce((acc, m) => acc + m.num_atividades, 0);
  const mediaGeral = totalAtividades
    ? Math.round(
        visiveis.reduce((acc, m) => acc + m.media_percentual * m.num_atividades, 0) / totalAtividades,
      )
    : 0;
  const historico = visiveis
    .flatMap((m) => m.historico)
    .sort((a, b) => a.data.localeCompare(b.data));
  const crescimento =
    historico.length > 1 ? Math.round(historico[historico.length - 1].percentual - historico[0].percentual) : 0;
  // C1-C5 so fazem sentido para redacao: exatas nao alimenta o dominio por tema (ver backend).
  // o nome exato da materia varia (ex.: "Redação ENEM"), entao basta comecar com "Redação".
  const mostraCompetencias = subject === "Todas" || subject.toLowerCase().startsWith("redação");
  const competenciasRedacao = mostraCompetencias ? (dominio ?? []).filter((d) => d.num_evidencias > 0) : [];

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">APRENDER É UM PROCESSO</div>
          <h1>Olha o quanto você avançou.</h1>
          <p>Compare você com você. Cada conquista tem seu valor.</p>
        </div>
      </div>
      <Card>
        <SectionTitle title="Seu domínio ao longo do tempo" />
        <div className="evolution-highlight">
          <strong>
            {mediaGeral}
            <span>%</span>
          </strong>
          {historico.length > 1 && (
            <Badge>
              <TrendingUp size={13} />
              {crescimento >= 0 ? ` +${crescimento}` : ` ${crescimento}`} pontos desde a primeira correção
            </Badge>
          )}
        </div>
        <RealSparkline pontos={historico} />
        <p className="tiny muted">
          Baseado em {totalAtividades} atividade(s) corrigida(s) e aprovada(s) pelo professor
          {subject !== "Todas" ? ` em ${subject}` : ""}.
        </p>
      </Card>
      <Card>
        <SectionTitle title="Cada matéria, uma conquista" />
        <div className="tabs input-tabs">
          {subjects.map((s) => (
            <button
              key={s}
              aria-pressed={subject === s}
              className={subject === s ? "active" : ""}
              onClick={() => setSubject(s)}
            >
              {s}
            </button>
          ))}
        </div>
        <div className="topic-cards">
          {visiveis.map((m) => (
            <div className="topic-detail" key={m.materia_id}>
              <Badge tone="neutral">{m.materia}</Badge>
              <h3>{m.materia}</h3>
              <div className="topic-large">
                {Math.round(m.media_percentual)}
                <small>%</small>
              </div>
              <Progress value={m.media_percentual} label={m.materia} />
              <p className="tiny muted">Com base em {m.num_atividades} atividade(s) corrigida(s)</p>
            </div>
          ))}
        </div>
        {competenciasRedacao.length > 0 && (
          <>
            <SectionTitle title="Competências da redação (C1 a C5)" />
            <div className="topic-cards">
              {competenciasRedacao.map((d) => (
                <div className="topic-detail" key={d.tema_id}>
                  <Badge tone="neutral">{d.habilidade_codigo}</Badge>
                  <h3>{HABILIDADE_NOME[d.habilidade_codigo] ?? d.tema}</h3>
                  <div className="topic-large">
                    {Math.round(d.percentual_dominio)}
                    <small>%</small>
                  </div>
                  <Progress value={d.percentual_dominio} label={d.tema} />
                  <p className="tiny muted">Com base em {d.num_evidencias} correções aprovadas</p>
                </div>
              ))}
            </div>
          </>
        )}
        <div className="card-note">
          O domínio é uma estimativa de aprendizagem, não uma nota oficial nem
          previsão de resultado no ENEM.
        </div>
      </Card>
    </>
  );
}
// Aba Exercicios do aluno: "Para voce (IA)" = gerados na hora pelos pontos fracos dele;
// "Do professor" = publicados pelo professor da turma (mesmo que a IA tenha ajudado a criar).
// resultado discreto: bolinha colorida com icone + frase (no lugar do selo colorido)
function ResultadoMini({ resultado }: { resultado: "CERTA" | "ERRADA" | "PARCIAL" | null }) {
  const [classe, icone, texto] =
    resultado === "CERTA" ? ["certo", <Check size={12} key="i" />, "Você acertou"]
    : resultado === "ERRADA" ? ["errado", <X size={12} key="i" />, "Você errou"]
    : resultado === "PARCIAL" ? ["parcial", <Check size={12} key="i" />, "Parcialmente certo"]
    : ["espera", <Check size={12} key="i" />, "Esperando o professor"];
  return <p className="resultado-mini"><span className={`ponto ${classe}`}>{icone}</span>{texto}</p>;
}

// resposta do aluno nos exercicios da IA (so um envio): guardada no navegador, por aluno
type RespostaIA = { escolha: number; certo: boolean };
function useRespostasIA(userId?: string) {
  const chave = `domina-ia-respostas:${userId ?? "demo"}`;
  const ler = (): Record<string, RespostaIA> => {
    try { return JSON.parse(localStorage.getItem(chave) ?? "{}"); } catch { return {}; }
  };
  const [mapa, setMapa] = useState<Record<string, RespostaIA>>(ler);
  const salvar = (pergunta: string, r: RespostaIA) => {
    const novo = { ...ler(), [pergunta]: r };
    try { localStorage.setItem(chave, JSON.stringify(novo)); } catch { /* sem armazenamento: vale so ate sair da tela */ }
    setMapa(novo);
  };
  return [mapa, salvar] as const;
}

export function Studies(props: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  selected: string | null;
  select: (s: string | null) => void;
  currentUser?: UsuarioAtual | null;
}) {
  const [aba, setAba] = useState<"ia" | "professor">("ia");
  const [abertoProf, setAbertoProf] = useState(false);
  const emExercicio = !!props.selected || abertoProf;
  return (
    <>
      {!emExercicio && (
        <>
          <div className="page-heading">
            <div>
              <div className="eyebrow">UM PLANO QUE FAZ SENTIDO PARA VOCÊ</div>
              <h1>Exercícios</h1>
              <p>Práticas curtas para treinar. Não valem nota.</p>
            </div>
          </div>
          <div className="botoes-escolha" role="group" aria-label="Origem dos exercícios">
            <button aria-pressed={aba === "ia"} className={aba === "ia" ? "active" : ""} onClick={() => setAba("ia")}>
              <Sparkles size={14} /> Para você (IA)
            </button>
            <button aria-pressed={aba === "professor"} className={aba === "professor" ? "active" : ""}
              onClick={() => setAba("professor")}>Do professor</button>
          </div>
        </>
      )}
      {aba === "ia" ? <PlanoIA {...props} /> : (
        <DoProfessor real={!!props.currentUser} aberto={abertoProf} setAberto={setAbertoProf} />
      )}
    </>
  );
}

function PlanoIA({
  state,
  update,
  selected,
  select,
  currentUser,
}: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  selected: string | null;
  select: (s: string | null) => void;
  currentUser?: UsuarioAtual | null;
}) {
  const real = !!currentUser;
  const [respostasIA, salvarRespostaIA] = useRespostasIA(currentUser?.id);
  const [exerciciosReais, setExerciciosReais] = useState<ExercicioAPI[] | null>(null);
  const [carregando, setCarregando] = useState(real);
  const [recarregando, setRecarregando] = useState(false);
  const [erro, setErro] = useState("");
  const carregar = (recarregar = false) => {
    if (!real) return;
    (recarregar ? setRecarregando : setCarregando)(true);
    setErro("");
    meusExercicios(recarregar)
      .then(setExerciciosReais)
      .catch((e) =>
        setErro(e instanceof Error ? e.message : "Não foi possível montar seu plano de estudo."),
      )
      .finally(() => (recarregar ? setRecarregando : setCarregando)(false));
  };
  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [real, currentUser?.id]);

  const tarefas: ExercicioComum[] = real
    ? (exerciciosReais ?? []).map(doBackend)
    : studyTasks.map(doDemo);
  const task = tarefas.find((t) => t.id === selected);
  if (task)
    return (
      <Exercise
        key={task.id}
        task={task}
        anterior={respostasIA[task.question] ?? null}
        onBack={() => select(null)}
        onComplete={(escolha, certo) => {
          salvarRespostaIA(task.question, { escolha, certo });
          update((s) => ({
            ...s,
            completed: [...new Set([...s.completed, task.id])],
          }));
        }}
      />
    );
  if (real && carregando)
    return (
      <Empty
        title="Montando seu plano de estudo..."
        text="Isso pode levar uns 20 a 30 segundos na primeira vez: estamos gerando exercícios específicos para o seu desempenho real."
      />
    );
  if (real && erro)
    return <Empty title="Ainda não dá para montar seu plano" text={erro} />;
  return (
    <>
      <div className="info-banner">
        <Sparkles size={22} />
        <div>
          <strong>Por que esses exercícios?</strong>
          <p>
            {tarefas[0]
              ? `Você começa por ${tarefas[0].topic}: é onde seu desempenho real mostra mais espaço para evoluir.`
              : "Começamos pelos temas com maior espaço para evolução no seu mapa demonstrativo."}
          </p>
        </div>
      </div>
      {real && (
        <div className="form-actions left">
          <Button
            variant="secondary"
            icon={RotateCcw}
            disabled={recarregando}
            onPress={() => carregar(true)}
          >
            {recarregando ? "Carregando..." : "Carregar exercícios (usar pouco)"}
          </Button>
        </div>
      )}
      <div className="study-grid">
        {tarefas.map((t, i) => {
          const feito = respostasIA[t.question] ?? null;
          // o botao verde (principal) e sempre o primeiro que ainda nao foi feito
          const proximo = tarefas.findIndex((x) => !respostasIA[x.question]) === i;
          return (
          <Card key={t.id} className="study-task">
            <div className="section-title">
              <span className="task-number">0{i + 1}</span>
              {feito ? (
                <Badge tone="neutral">Feito</Badge>
              ) : proximo ? (
                <Badge>Recomendado para você</Badge>
              ) : (
                <Badge tone="neutral">{t.type}</Badge>
              )}
            </div>
            {feito && <ResultadoMini resultado={feito.certo ? "CERTA" : "ERRADA"} />}
            <span className="eyebrow">{t.topic}</span>
            <h2>{t.title}</h2>
            <p>{t.description}</p>
            <Button
              variant={proximo ? "primary" : "secondary"}
              icon={ArrowRight}
              onPress={() => select(t.id)}
            >
              {feito ? "Ver resposta" : "Começar prática"}
            </Button>
          </Card>
          );
        })}
      </div>
      <p className="tiny muted">
        {real
          ? "Exercícios gerados por IA a partir do seu desempenho real. A prática não altera a estimativa de domínio nesta versão."
          : "Exercícios demonstrativos com respostas predefinidas. A prática não altera a estimativa de domínio nesta versão."}
      </p>
    </>
  );
}
function Exercise({
  task,
  anterior,
  onBack,
  onComplete,
}: {
  task: ExercicioComum;
  anterior: RespostaIA | null;
  onBack: () => void;
  onComplete: (escolha: number, certo: boolean) => void;
}) {
  // so uma resposta: se ja foi feito, abre mostrando o resultado
  const [answer, setAnswer] = useState<number | null>(anterior?.escolha ?? null);
  const [checked, setChecked] = useState(anterior !== null);
  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar aos exercícios
      </button>
      <Card className="exercise-card">
        <Badge tone="neutral">{task.topic} · {task.type}</Badge>
        <div className="exercise-step">EXERCÍCIO 01 / 01</div>
        <h1>{task.question}</h1>
        <fieldset className="options">
          <legend className="sr-only">Escolha uma resposta</legend>
          {task.options.map((o, i) => (
            <label
              key={o}
              className={`option ${answer === i ? "chosen" : ""} ${checked && i === task.answer ? "correct" : ""} ${checked && answer === i && i !== task.answer ? "wrong" : ""}`}
            >
              <input
                type="radio"
                name="answer"
                checked={answer === i}
                disabled={checked}
                onChange={() => setAnswer(i)}
              />
              <span className="option-letter">
                {String.fromCharCode(65 + i)}
              </span>
              {o}
            </label>
          ))}
        </fieldset>
        {checked ? (
          <>
            <div
              className={`exercise-feedback ${answer === task.answer ? "" : "retry"}`}
            >
              <h3>
                {answer === task.answer ? "Você acertou." : "Você errou."}
              </h3>
              <p>{task.explanation}</p>
            </div>
            <Button onPress={onBack}>Concluir prática</Button>
          </>
        ) : (
          <Button
            disabled={answer === null}
            onPress={() => {
              setChecked(true);
              onComplete(answer as number, answer === task.answer);
            }}
          >
            Conferir resposta
          </Button>
        )}
      </Card>
    </>
  );
}

/* ---------------- aba "Do professor" ---------------- */

const LETRAS_EX = "ABCDEF";

function DoProfessor({ real, aberto, setAberto }: { real: boolean; aberto: boolean; setAberto: (v: boolean) => void }) {
  const [lista, setLista] = useState<ExercicioAlunoAPI[] | null>(real ? null : []);
  const [erro, setErro] = useState("");
  const [atual, setAtual] = useState<ExercicioAlunoAPI | null>(null);
  useEffect(() => {
    if (!real) return;
    exerciciosDaTurma().then(setLista).catch((e) => setErro(e instanceof Error ? e.message : "Não foi possível carregar."));
  }, [real]);
  const abrir = (ex: ExercicioAlunoAPI | null) => { setAtual(ex); setAberto(!!ex); window.scrollTo(0, 0); };
  if (aberto && atual)
    return (
      <ExercicioDoProfessor
        key={atual.id}
        ex={atual}
        onBack={() => abrir(null)}
        onRespondido={(novo) => { setAtual(novo); setLista((l) => l?.map((x) => (x.id === novo.id ? novo : x)) ?? l); }}
      />
    );
  if (erro) return <Empty title="Não deu para carregar" text={erro} />;
  if (lista === null) return <Empty title="Carregando..." text="Buscando os exercícios dos seus professores." />;
  if (!lista.length)
    return <Empty title="Nenhum exercício do professor ainda" text="Quando seu professor publicar um exercício para a sua turma, ele aparece aqui." />;
  const feitos = lista.filter((e) => e.minha_resposta !== null).length;
  return (
    <>
      <p className="tiny muted">{feitos} de {lista.length} feito(s)</p>
      <div className="study-grid">
        {lista.map((ex) => (
          <Card key={ex.id} className="study-task ex-prof">
            <div className="section-title">
              <Badge tone="neutral">{ex.tipo === "OBJETIVO" ? "Objetivo" : "Discursivo"}</Badge>
              {ex.minha_resposta !== null ? (
                <Badge tone="neutral">Feito</Badge>
              ) : ex.gerado_por_ia ? <Badge tone="neutral"><Sparkles size={13} /> Com ajuda da IA</Badge> : null}
            </div>
            {ex.minha_resposta !== null && <ResultadoMini resultado={ex.tipo === "OBJETIVO" && !ex.resultado ? (ex.correta ? "CERTA" : "ERRADA") : (ex.resultado as "CERTA" | "ERRADA" | "PARCIAL" | null)} />}
            {ex.comentario && <Badge tone="amber">O professor comentou</Badge>}
            <span className="eyebrow">{ex.materia_nome} · {ex.assunto}</span>
            <h2>{ex.titulo}</h2>
            <p className="tiny muted">Prof. {ex.professor_nome}</p>
            <Button variant={ex.minha_resposta === null ? "primary" : "secondary"} icon={ArrowRight} onPress={() => abrir(ex)}>
              {ex.minha_resposta === null ? "Começar" : "Ver de novo"}
            </Button>
          </Card>
        ))}
      </div>
    </>
  );
}

function ExercicioDoProfessor({ ex, onBack, onRespondido }: {
  ex: ExercicioAlunoAPI; onBack: () => void; onRespondido: (ex: ExercicioAlunoAPI) => void;
}) {
  const objetivo = ex.tipo === "OBJETIVO";
  const [escolha, setEscolha] = useState<number | null>(null);
  const [texto, setTexto] = useState("");
  const [visto, setVisto] = useState(ex.minha_resposta !== null); // ja respondido: mostra o resultado
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const marcada = visto && objetivo && ex.minha_resposta !== null ? Number(ex.minha_resposta) : escolha;
  const enviar = async () => {
    setEnviando(true); setErro("");
    try {
      onRespondido(await responderExercicio(ex.id, objetivo ? String(escolha) : texto.trim()));
      setVisto(true);
    } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível enviar."); }
    finally { setEnviando(false); }
  };
  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar aos exercícios
      </button>
      <Card className="exercise-card">
        <Badge tone="neutral">{ex.materia_nome} · {ex.assunto} · {objetivo ? "Objetivo" : "Discursivo"}</Badge>
        <div className="exercise-step">{ex.titulo.toUpperCase()} · PROF. {ex.professor_nome.toUpperCase()}</div>
        <h1 className="enunciado-ex">{ex.enunciado}</h1>
        {objetivo ? (
          <fieldset className="options">
            <legend className="sr-only">Escolha uma resposta</legend>
            {(ex.alternativas ?? []).map((o, i) => (
              <label key={i}
                className={`option ${marcada === i ? "chosen" : ""} ${visto && i === ex.resposta_correta ? "correct" : ""} ${visto && marcada === i && i !== ex.resposta_correta ? "wrong" : ""}`}>
                <input type="radio" name="resposta-prof" checked={marcada === i} disabled={visto} onChange={() => setEscolha(i)} />
                <span className="option-letter">{LETRAS_EX[i]}</span>
                {o}
              </label>
            ))}
          </fieldset>
        ) : visto ? (
          <div className="comparar-respostas">
            <div><h3>Sua resposta</h3><p>{ex.minha_resposta}</p></div>
            <div>
              <h3>{ex.respostas_exemplo.length > 1 ? "Respostas de exemplo do professor" : "Resposta de exemplo do professor"}</h3>
              {(ex.respostas_exemplo.length ? ex.respostas_exemplo : [ex.resposta_exemplo ?? ""]).map((e, i, todas) => (
                <p key={i} className={i ? "exemplo-extra" : ""}>{todas.length > 1 && <b>{i + 1}. </b>}{e}</p>
              ))}
            </div>
          </div>
        ) : (
          <div className="campo-resposta">
            <label htmlFor="resposta-discursiva">Responder</label>
            <textarea id="resposta-discursiva" rows={7} value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Escreva aqui" />
          </div>
        )}
        {erro && <p className="error" role="alert">{erro}</p>}
        {visto ? (
          <>
            <div className={`exercise-feedback ${ex.resultado && ex.resultado !== "CERTA" ? "retry" : ""}`}>
              <h3>
                {objetivo
                  ? ex.correta ? "Você acertou." : "Você errou."
                  : ex.resultado === "CERTA" ? "O professor marcou sua resposta como certa."
                  : ex.resultado === "PARCIAL" ? "O professor marcou sua resposta como parcialmente certa. Compare com a do exemplo."
                  : ex.resultado === "ERRADA" ? "O professor marcou sua resposta como errada. Compare com a do exemplo."
                  : "Compare sua resposta com a do professor. Ele ainda vai corrigir."}
              </h3>
              {ex.explicacao && <p>{ex.explicacao}</p>}
              {ex.comentario && <p className="comentario-prof"><b>Comentário do professor:</b> {ex.comentario}</p>}
            </div>
            <div className="form-actions left">
              <Button onPress={onBack}>Concluir</Button>
            </div>
          </>
        ) : (
          <Button disabled={enviando || (objetivo ? escolha === null : !texto.trim())} onPress={enviar}>
            {enviando ? "Enviando..." : objetivo ? "Conferir resposta" : "Enviar"}
          </Button>
        )}
      </Card>
    </>
  );
}
