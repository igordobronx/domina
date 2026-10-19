import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  CheckCheck,
  Clock3,
  Flame,
  GraduationCap,
  Plus,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import type { Activity, DemoState, Page, Role } from "../types";
import { topics, studyTasks } from "../data/demo";
import { Badge, Button, Card, Progress, SectionTitle } from "../components/ui";
import { EvolutionChart } from "../components/Chart";

export function Dashboard({
  role,
  state,
  navigate,
  openActivity,
  openStudy,
}: {
  role: Role;
  state: DemoState;
  navigate: (p: Page) => void;
  openActivity: (a: Activity) => void;
  openStudy: (id: string) => void;
}) {
  const student = role === "aluno";
  const pending = state.activities.filter((a) => a.status === "pendente");
  const approved = state.activities.filter((a) => a.status === "aprovada");
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            {student ? "CADA PASSO CONTA" : "ENSINAR É TRANSFORMAR"}
          </div>
          <h1>
            {student
              ? `Bom te ver, ${state.name.split(" ")[0]}.`
              : role === "professor"
                ? "Olá, professora Marina."
                : "Uma visão do que importa."}
            <span className="heading-dot">✳</span>
          </h1>
          <p>
            {student
              ? "Um pouco de prática hoje. Um novo domínio amanhã."
              : "Acompanhe a aprendizagem e ajude cada aluno a ir além."}
          </p>
        </div>
        <Button
          icon={student ? Plus : BookOpen}
          onPress={() => navigate(student ? "atividades" : "revisoes")}
        >
          {student ? "Enviar atividade" : "Revisar atividades"}
        </Button>
      </div>
      <div className="dashboard-top">
        <section className="hero-card">
          <div className="hero-copy">
            <div className="hero-eyebrow">
              <span className="live-dot" />
              {student
                ? "SEU APRENDIZADO EM MOVIMENTO"
                : "O OLHAR HUMANO FAZ A DIFERENÇA"}
            </div>
            <h2>
              {student ? (
                <>
                  Você está construindo
                  <br />o seu próximo <em>nível.</em>
                </>
              ) : (
                <>
                  A IA sugere.
                  <br />
                  Você faz a <em>diferença.</em>
                </>
              )}
            </h2>
            <p>
              {student
                ? "Cada dúvida resolvida vira conhecimento. Continue de onde parou — você está no caminho."
                : `${pending.length} atividade${pending.length === 1 ? "" : "s"} aguardando seu olhar. Revise, oriente e transforme erros em próximos passos.`}
            </p>
            <button
              className="hero-link"
              onClick={() => (student ? openStudy("s1") : navigate("revisoes"))}
            >
              {student ? "Continuar meu aprendizado" : "Abrir fila de revisão"}
              <ArrowRight size={18} />
            </button>
          </div>
          <div
            className="hero-art"
            aria-label="Domínio ilustrativo de 67 por cento"
          >
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <svg viewBox="0 0 180 180">
              <circle
                cx="90"
                cy="90"
                r="70"
                fill="none"
                stroke="#30384A"
                strokeWidth="13"
              />
              <circle
                className="ring-fill"
                cx="90"
                cy="90"
                r="70"
                fill="none"
                stroke="#54C697"
                strokeWidth="13"
                strokeLinecap="round"
                strokeDasharray="295 440"
                transform="rotate(-90 90 90)"
              />
            </svg>
            <div className="ring-label">
              <strong>
                67<span>%</span>
              </strong>
              <span>domínio geral</span>
            </div>
            <span className="floating-tag">
              <TrendingUp size={14} /> +12% este mês
            </span>
          </div>
        </section>
        <Card className="week-card">
          <div className="section-title">
            <h2>Um passo por dia</h2>
            <Flame size={20} color="#B97A21" />
          </div>
          <p className="muted">Pequenos hábitos, grandes conquistas.</p>
          <div className="week-days">
            {["S", "T", "Q", "Q", "S", "S", "D"].map((d, i) => (
              <div key={i}>
                <span>{d}</span>
                <div
                  className={i < 2 ? "day done" : i === 2 ? "day today" : "day"}
                >
                  {i < 2 ? <Check size={15} /> : i + 5}
                </div>
              </div>
            ))}
          </div>
          <div className="week-bottom">
            <div>
              <strong>
                {Math.min(2 + state.completed.length, state.goal)}
                <span>/{state.goal}</span>
              </strong>
              <span>práticas da semana</span>
            </div>
            <span className="small-leaf">✳</span>
          </div>
          <Progress
            value={Math.min(
              ((2 + state.completed.length) / state.goal) * 100,
              100,
            )}
            label="Meta semanal de práticas"
          />
          <p className="tiny muted">
            {state.completed.length + 2 >= state.goal
              ? "Meta alcançada. Continue no seu ritmo!"
              : "Seu ritmo importa mais que a velocidade."}
          </p>
        </Card>
      </div>
      <div className="stats-grid">
        <Stat
          icon={Target}
          value="67%"
          label="Domínio médio"
          foot="↑ 12 pontos neste mês"
        />
        <Stat
          icon={CheckCheck}
          value={String(approved.length).padStart(2, "0")}
          label="Atividades corrigidas"
          foot="Com revisão do professor"
        />
        <Stat
          icon={Clock3}
          value={String(pending.length).padStart(2, "0")}
          label="Aguardando revisão"
          foot="Você recebe o resultado aqui"
          amber
        />
        <Stat
          icon={GraduationCap}
          value="04"
          label="Temas em construção"
          foot="Um novo passo a cada prática"
        />
      </div>
      <div className="dashboard-middle">
        <Card>
          <SectionTitle
            title={
              student
                ? "Seu mapa de conhecimento"
                : "Mapa de conhecimento da turma"
            }
            action="Ver evolução"
            onAction={() => navigate("evolucao")}
          />
          <p className="muted card-subtitle">
            Não é sobre saber tudo. É sobre saber por onde começar.
          </p>
          <div className="topic-list">
            {topics.map((t) => (
              <div key={t.name} className="topic-row">
                <div className="topic-heading">
                  <div>
                    <strong>{t.name}</strong>
                    <span>
                      {t.subject} <span className="separator">/</span>{" "}
                      {t.evidence} correções aprovadas
                    </span>
                  </div>
                  <span className="topic-value">
                    {t.value}
                    <small>%</small>
                  </span>
                </div>
                <Progress value={t.value} label={`Domínio em ${t.name}`} />
              </div>
            ))}
          </div>
          <div className="card-note">
            <span className="live-dot" />
            Estimativas baseadas nas suas atividades revisadas.
          </div>
        </Card>
        <Card className="next-card">
          <SectionTitle title="Seu próximo passo" />
          <div className="recommend-label">
            <Sparkles size={14} /> RECOMENDADO PARA VOCÊ
          </div>
          <div className="study-illustration">
            <div className="paper-sheet">
              <span />
              <span />
              <span className="highlight-line" />
              <span />
              <span />
            </div>
            <div className="paper-check">
              <Check size={25} />
            </div>
            <span className="spark spark-a">✧</span>
            <span className="spark spark-b">✳</span>
          </div>
          <Badge tone="neutral">Redação · Coesão textual</Badge>
          <h3>
            Boas ideias merecem
            <br />
            boas conexões.
          </h3>
          <p>Pratique conectivos e deixe seus argumentos ainda mais claros.</p>
          <div className="study-meta">
            <Clock3 size={14} /> 10 minutos <span>·</span> Exercício guiado
          </div>
          <Button onPress={() => openStudy(studyTasks[0].id)} icon={ArrowRight}>
            {state.completed.includes("s1")
              ? "Praticar novamente"
              : "Começar a praticar"}
          </Button>
        </Card>
      </div>
      <Card>
        <SectionTitle
          title={student ? "Suas atividades recentes" : "Atividades da turma"}
          action="Ver todas"
          onAction={() => navigate(student ? "atividades" : "revisoes")}
        />
        <div className="activity-list">
          {state.activities
            .slice()
            .reverse()
            .slice(0, 3)
            .map((a) => (
              <ActivityRow
                key={a.id}
                activity={a}
                onClick={() => openActivity(a)}
              />
            ))}
        </div>
      </Card>
      {!student && (
        <Card>
          <SectionTitle title="Aprendizagem ao longo do tempo" />
          <EvolutionChart />
        </Card>
      )}
      <div className="footer-note">
        <span>domina.ai</span> Do erro ao domínio. No seu tempo.
        <span className="demo-note">Dados demonstrativos</span>
      </div>
    </>
  );
}
function Stat({
  icon: Icon,
  value,
  label,
  foot,
  amber = false,
}: {
  icon: typeof Target;
  value: string;
  label: string;
  foot: string;
  amber?: boolean;
}) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span className={`stat-icon ${amber ? "stat-amber" : ""}`}>
          <Icon size={18} />
        </span>
        <span className="stat-value">{value}</span>
      </div>
      <strong>{label}</strong>
      <span className="stat-foot">{foot}</span>
    </div>
  );
}
export function ActivityRow({
  activity: a,
  onClick,
}: {
  activity: Activity;
  onClick: () => void;
}) {
  return (
    <button className="activity-row" onClick={onClick}>
      <span
        className={`activity-icon ${a.kind === "matematica" ? "math-icon" : ""}`}
      >
        {a.kind === "redacao" ? <BookOpen size={20} /> : <span>ƒx</span>}
      </span>
      <span className="activity-info">
        <strong>{a.title}</strong>
        <span>
          {a.subject}
          {a.date && ` · ${a.date}`}
        </span>
      </span>
      <Badge
        tone={
          a.status === "aprovada"
            ? "green"
            : a.status === "pendente"
              ? "amber"
              : "neutral"
        }
      >
        {a.status === "aprovada"
          ? "Corrigida"
          : a.status === "pendente"
            ? "Em revisão"
            : "Para fazer"}
      </Badge>
      {a.status === "aprovada" && (
        <span className="row-score">
          {a.scores?.reduce((s, n) => s + n, 0)}
        </span>
      )}
      <ArrowUpRight size={18} />
    </button>
  );
}
