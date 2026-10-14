import { useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Clock3,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { topics, studyTasks } from "../data/demo";
import type { DemoState } from "../types";
import { Badge, Button, Card, Progress, SectionTitle } from "../components/ui";
import { EvolutionChart } from "../components/Chart";

export function Evolution() {
  const [subject, setSubject] = useState("Todas");
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">APRENDER É UM PROCESSO</div>
          <h1>Olha o quanto você avançou.</h1>
          <p>Compare você com você. Cada conquista tem seu valor.</p>
        </div>
        <Badge tone="neutral">Dados ilustrativos</Badge>
      </div>
      <Card>
        <SectionTitle title="Seu domínio ao longo do tempo" />
        <div className="evolution-highlight">
          <strong>
            67<span>%</span>
          </strong>
          <Badge>
            <TrendingUp size={13} /> +12 pontos no mês
          </Badge>
        </div>
        <EvolutionChart />
        <p className="tiny muted">
          Histórico demonstrativo · agosto a outubro de 2026. O cálculo real de
          domínio será fornecido pelo backend.
        </p>
      </Card>
      <Card>
        <SectionTitle title="Cada tema, uma conquista" />
        <div className="tabs input-tabs">
          {["Todas", "Redação", "Matemática"].map((s) => (
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
          {topics
            .filter((t) => subject === "Todas" || t.subject === subject)
            .map((t) => (
              <div className="topic-detail" key={t.name}>
                <Badge tone="neutral">{t.subject}</Badge>
                <h3>{t.name}</h3>
                <div className="topic-large">
                  {t.value}
                  <small>%</small>
                  <span>+{t.growth} pontos</span>
                </div>
                <Progress value={t.value} label={t.name} />
                <p className="tiny muted">
                  Com base em {t.evidence} correções aprovadas
                </p>
              </div>
            ))}
        </div>
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
}: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  selected: string | null;
  select: (s: string | null) => void;
}) {
  const task = studyTasks.find((t) => t.id === selected);
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
            Começamos pelos temas com maior espaço para evolução no seu mapa
            demonstrativo.
          </p>
        </div>
      </div>
      <div className="study-grid">
        {studyTasks.map((t, i) => (
          <Card key={t.id} className="study-task">
            <div className="section-title">
              <span className="task-number">0{i + 1}</span>
              {state.completed.includes(t.id) ? (
                <Badge>
                  <Check size={13} />
                  Concluído
                </Badge>
              ) : (
                <Badge tone="neutral">{t.type}</Badge>
              )}
            </div>
            <span className="eyebrow">{t.topic}</span>
            <h2>{t.title}</h2>
            <p>{t.description}</p>
            <div className="study-meta">
              <Clock3 size={15} />
              {t.time}
            </div>
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
        Exercícios demonstrativos com respostas predefinidas. A prática não
        altera a estimativa de domínio nesta versão.
      </p>
    </>
  );
}
function Exercise({
  task,
  onBack,
  onComplete,
}: {
  task: (typeof studyTasks)[number];
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
        <Badge tone="neutral">{task.topic} · Prática demonstrativa</Badge>
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
