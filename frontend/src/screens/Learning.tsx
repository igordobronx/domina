import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
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
  meusExercicios,
  type DominioAPI,
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
export function Studies({
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
  const [exerciciosReais, setExerciciosReais] = useState<ExercicioAPI[] | null>(null);
  const [carregando, setCarregando] = useState(real);
  const [erro, setErro] = useState("");
  useEffect(() => {
    if (!real) return;
    setCarregando(true);
    setErro("");
    meusExercicios()
      .then(setExerciciosReais)
      .catch((e) =>
        setErro(e instanceof Error ? e.message : "Não foi possível montar seu plano de estudo."),
      )
      .finally(() => setCarregando(false));
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
        onBack={() => select(null)}
        onComplete={() =>
          update((s) => ({
            ...s,
            completed: [...new Set([...s.completed, task.id])],
          }))
        }
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
      <div className="page-heading">
        <div>
          <div className="eyebrow">UM PLANO QUE FAZ SENTIDO PARA VOCÊ</div>
          <h1>Seu próximo passo começa aqui.</h1>
          <p>Práticas curtas, direcionadas ao que você está construindo.</p>
        </div>
      </div>
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
      <div className="study-grid">
        {tarefas.map((t, i) => (
          <Card key={t.id} className="study-task">
            <div className="section-title">
              <span className="task-number">0{i + 1}</span>
              {state.completed.includes(t.id) ? (
                <Badge>
                  <Check size={13} />
                  Concluído
                </Badge>
              ) : i === 0 ? (
                <Badge>Recomendado para você</Badge>
              ) : (
                <Badge tone="neutral">{t.type}</Badge>
              )}
            </div>
            <span className="eyebrow">{t.topic}</span>
            <h2>{t.title}</h2>
            <p>{t.description}</p>
            <Button
              variant={i === 0 ? "primary" : "secondary"}
              icon={ArrowRight}
              onPress={() => select(t.id)}
            >
              {state.completed.includes(t.id)
                ? "Praticar novamente"
                : "Começar prática"}
            </Button>
          </Card>
        ))}
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
  onBack,
  onComplete,
}: {
  task: ExercicioComum;
  onBack: () => void;
  onComplete: () => void;
}) {
  const [answer, setAnswer] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  return (
    <>
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} />
        Voltar ao plano de estudo
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
              className={`option ${answer === i ? "chosen" : ""} ${checked && i === task.answer ? "correct" : ""}`}
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
                {answer === task.answer
                  ? "Isso mesmo. Mais um passo!"
                  : "É errando que a gente constrói domínio."}
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
              onComplete();
            }}
          >
            Conferir resposta
          </Button>
        )}
      </Card>
    </>
  );
}
