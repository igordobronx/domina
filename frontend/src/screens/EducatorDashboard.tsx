import {
  ArrowRight,
  BookOpen,
  ClipboardCheck,
  ShieldCheck,
  Users,
} from "lucide-react";
import {
  Card,
  Badge,
  Button,
  SectionTitle,
  Empty,
  Progress,
} from "../components/ui";
import { ActivityRow } from "./Dashboard";
import { EvolutionChart } from "../components/Chart";
import { topics } from "../data/demo";
import type { Activity, DemoState, Page, Role } from "../types";
import type { UsuarioAtual } from "../services/api";
export function EducatorDashboard({
  role,
  state,
  navigate,
  openActivity,
  currentUser,
}: {
  role: Role;
  state: DemoState;
  navigate: (p: Page) => void;
  openActivity: (a: Activity) => void;
  currentUser?: UsuarioAtual | null;
}) {
  const pending = state.activities.filter((a) => a.status === "pendente");
  const teacher = role === "professor";
  const primeiroNome = currentUser?.nome.split(" ")[0];
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">ENSINAR É TRANSFORMAR</div>
          <h1>
            {teacher
              ? `Olá, ${primeiroNome ?? "professor(a)"}.`
              : "Uma visão do que importa."}
          </h1>
          <p>
            {teacher
              ? "Seu olhar transforma uma correção em aprendizado."
              : "Acompanhe sua escola, uma jornada de cada vez."}
          </p>
        </div>
        <Button
          icon={teacher ? ClipboardCheck : Users}
          onPress={() => navigate(teacher ? "revisoes" : "turmas")}
        >
          {teacher ? "Revisar atividades" : "Acompanhar turmas"}
        </Button>
      </div>
      <section className="hero-card educator-hero">
        <div className="hero-copy">
          <div className="hero-eyebrow">
            <span className="live-dot" /> ESCOLA HORIZONTE · PRÉ-ENEM 2026
          </div>
          <h2>
            {teacher ? (
              <>
                A IA sugere.
                <br />
                Você faz a <em>diferença.</em>
              </>
            ) : (
              <>
                Um olhar para o todo.
                <br />
                Cuidado com <em>cada aluno.</em>
              </>
            )}
          </h2>
          <p>
            {teacher
              ? `${pending.length} atividade${pending.length === 1 ? "" : "s"} aguardando seu olhar. Revise com calma e mostre ao aluno o próximo passo.`
              : "Conheça as lacunas, acompanhe as correções e dê à sua equipe espaço para ensinar melhor."}
          </p>
        </div>
        <div className="educator-symbol">
          <BookOpen size={100} strokeWidth={0.8} />
          <span>Do erro ao domínio.</span>
        </div>
      </section>
      <div className="stats-grid">
        <Card>
          <span className="eyebrow">TURMAS</span>
          <div className="metric">01</div>
          <p>Pré-ENEM A</p>
        </Card>
        <Card>
          <span className="eyebrow">ALUNOS ATIVOS</span>
          <div className="metric">01</div>
          <p>No ambiente demonstrativo</p>
        </Card>
        <Card>
          <span className="eyebrow">EM REVISÃO</span>
          <div className="metric">
            {String(pending.length).padStart(2, "0")}
          </div>
          <p>Aguardando aprovação</p>
        </Card>
        <Card>
          <span className="eyebrow">CORRIGIDAS</span>
          <div className="metric">
            {String(
              state.activities.filter((a) => a.status === "aprovada").length,
            ).padStart(2, "0")}
          </div>
          <p>Resultados disponíveis</p>
        </Card>
      </div>
      {teacher && (
        <Card>
          <SectionTitle
            title="Sua fila de revisão"
            action="Ver todas"
            onAction={() => navigate("revisoes")}
          />
          {pending.length ? (
            pending.map((a) => (
              <ActivityRow
                key={a.id}
                activity={a}
                onClick={() => openActivity(a)}
              />
            ))
          ) : (
            <Empty
              title="Tudo revisado por aqui"
              text="As próximas atividades enviadas aparecem nesta fila."
            />
          )}
        </Card>
      )}
      <div className="dashboard-middle">
        <Card>
          <SectionTitle title="O que a turma está construindo" />
          <p className="card-subtitle muted">
            Pré-ENEM A · valores ilustrativos
          </p>
          <div className="topic-list">
            {topics.map((t) => (
              <div className="topic-row" key={t.name}>
                <div className="topic-heading">
                  <strong>{t.name}</strong>
                  <span className="topic-value">{t.value}%</span>
                </div>
                <Progress label={t.name} value={t.value} />
              </div>
            ))}
          </div>
          <Badge tone="neutral">Não há ranking entre alunos</Badge>
        </Card>
        <Card className="educator-note">
          <ShieldCheck size={35} />
          <h3>Confiança se constrói com cuidado.</h3>
          <p>
            Nenhuma nota sugerida é exibida ao aluno antes da revisão. A decisão
            pedagógica é sempre do professor.
          </p>
          <Button
            variant="secondary"
            icon={ArrowRight}
            onPress={() => navigate(teacher ? "materiais" : "turmas")}
          >
            {teacher ? "Ver materiais e critérios" : "Conhecer a turma"}
          </Button>
        </Card>
      </div>
      <Card>
        <SectionTitle title="Uma turma em evolução" />
        <EvolutionChart />
        <p className="tiny muted">
          Série ilustrativa. Indicadores reais dependerão da integração com o
          backend.
        </p>
      </Card>
    </>
  );
}
