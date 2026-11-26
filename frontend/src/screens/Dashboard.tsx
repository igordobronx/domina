import { useEffect, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  CheckCheck,
  Clock3,
  Flame,
  ListTodo,
  Plus,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import type { Activity, ActivityStatus, DemoState, Page, Role } from "../types";
import { topics, studyTasks } from "../data/demo";
import { Badge, Button, Card, Progress, SectionTitle } from "../components/ui";
import { EvolutionChart } from "../components/Chart";
import type { UsuarioAtual } from "../services/api";
import { carregarDominioReal, type Recomendacao } from "../services/dominio";
import { dominioMeu, evolucaoMinha, minhasMetas, minhasSubmissoes, type DominioAPI, type NivelAPI } from "../services/api";
import { atividadesCorrigidas, montarMapa, tituloSubtopicos, type MapaConhecimento } from "../services/mapaConhecimento";
import { carregarAtividadesDoAluno } from "../services/atividades";
import { iso } from "../hooks/useCalendario";

export function Dashboard({
  role,
  state,
  navigate,
  openActivity,
  openStudy,
  currentUser,
}: {
  role: Role;
  state: DemoState;
  navigate: (p: Page, filtro?: ActivityStatus) => void;
  openActivity: (a: Activity) => void;
  openStudy: (id: string) => void;
  currentUser?: UsuarioAtual | null;
}) {
  const student = role === "aluno";
  // mapa de dominio real: so para aluno autenticado de verdade; enquanto nao carrega, mantem os dados de demonstracao
  const real = student && !!currentUser;
  // aluno de verdade: as MESMAS atividades de "Minhas atividades" (mesma funcao), nunca as de demonstracao
  const [reais, setReais] = useState<Activity[] | null>(null);
  useEffect(() => {
    if (real && currentUser) carregarAtividadesDoAluno(currentUser.nome).then(setReais).catch(() => setReais([]));
  }, [real, currentUser?.id]);
  const atividades = real ? (reais ?? []) : state.activities;
  const pending = atividades.filter((a) => a.status === "pendente");
  const corrigidasIA = atividades.filter((a) => a.status === "corrigida_ia");
  const approved = atividades.filter((a) => a.status === "aprovada");
  const paraFazer = atividades.filter((a) => a.status === "disponivel");
  // recentes: ultimo envio primeiro; as que ainda nao tem envio ficam por ultimo
  const recentes = real
    ? atividades.slice().sort((x, y) => (y.enviadoEm ?? "").localeCompare(x.enviadoEm ?? "")).slice(0, 3)
    : atividades.slice().reverse().slice(0, 3);
  const conta = (n: number) => (real && reais === null ? "--" : String(n).padStart(2, "0"));
  const [dominioReal, setDominioReal] = useState<DominioAPI[] | null>(null);
  const [recomendacao, setRecomendacao] = useState<Recomendacao | null>(null);
  // dias (AAAA-MM-DD) em que o aluno enviou algo: alimenta "Um passo por dia" com dado real
  const [diasEnviados, setDiasEnviados] = useState<string[]>([]);
  const [nivel, setNivel] = useState<NivelAPI | null>(null);
  useEffect(() => {
    if (student && currentUser) minhasMetas().then((r) => setNivel(r.nivel)).catch(() => {});
  }, [student, currentUser?.id]);
  useEffect(() => {
    if (student && currentUser) minhasSubmissoes().then((r) => setDiasEnviados(r.map((x) => iso(new Date(x.criado_em))))).catch(() => {});
  }, [student, currentUser]);
  const semana = (() => {  // segunda a domingo da semana de hoje
    const hoje = new Date();
    const seg = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate() - ((hoje.getDay() + 6) % 7));
    return Array.from({ length: 7 }, (_, i) => new Date(seg.getFullYear(), seg.getMonth(), seg.getDate() + i));
  })();
  const praticas = semana.filter((d) => diasEnviados.includes(iso(d))).length;
  useEffect(() => {
    if (!real) return;
    carregarDominioReal().then(({ dominio, recomendacao }) => {
      setDominioReal(dominio);
      setRecomendacao(recomendacao);
    });
  }, [real, currentUser?.id]);
  // mapa por materia (% e subtopicos): mesma base da tela Minha evolucao
  const [mapa, setMapa] = useState<MapaConhecimento | null>(null);
  const [materiaSub, setMateriaSub] = useState<string | null>(null); // aba do cartao de subtopicos
  useEffect(() => {
    if (!real) return;
    Promise.all([evolucaoMinha(), dominioMeu()])
      .then(([ev, dom]) => setMapa(montarMapa(ev, dom)))
      .catch(() => setMapa(montarMapa([], [])));
  }, [real, currentUser?.id]);
  const abaSub = materiaSub && mapa?.subtopicos[materiaSub] ? materiaSub : mapa?.inicial ?? null;
  const mediaReal = dominioReal?.length
    ? Math.round(dominioReal.reduce((s, d) => s + d.percentual_dominio, 0) / dominioReal.length)
    : null;
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            {student ? "CADA PASSO CONTA" : "ENSINAR É TRANSFORMAR"}
          </div>
          <h1>
            {student
              ? `Bom te ver, ${(currentUser?.nome ?? state.name).split(" ")[0]}.`
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
            {semana.map((d, i) => {
              const feito = diasEnviados.includes(iso(d));
              const hoje = iso(d) === iso(new Date());
              return (
                <div key={i}>
                  <span>{["S", "T", "Q", "Q", "S", "S", "D"][i]}</span>
                  <div className={feito ? "day done" : hoje ? "day today" : "day"}>
                    {feito ? <Check size={15} /> : d.getDate()}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="week-bottom">
            <div>
              <strong>
                {Math.min(praticas, state.goal)}
                <span>/{state.goal}</span>
              </strong>
              <span>práticas da semana</span>
            </div>
            <span className="small-leaf">✳</span>
          </div>
          <Progress
            value={Math.min(
              (praticas / state.goal) * 100,
              100,
            )}
            label="Meta semanal de práticas"
          />
          <p className="tiny muted">
            {praticas >= state.goal
              ? "Meta alcançada. Continue no seu ritmo!"
              : "Seu ritmo importa mais que a velocidade."}
          </p>
        </Card>
      </div>
      {real && nivel && (
        <Card>
          <div className="nivel-card">
            <div className="nivel-numero">{nivel.nivel}</div>
            <div style={{ flex: 1 }}>
              <strong>Nível {nivel.nivel} · {nivel.nome}</strong>
              <p className="tiny muted">
                {nivel.pontos} XP{nivel.pontos_proximo != null ? ` · faltam ${nivel.pontos_proximo - nivel.pontos} XP para o próximo nível` : ""}
              </p>
            </div>
            <Button variant="secondary" onPress={() => navigate("metas")}>Ver metas</Button>
          </div>
        </Card>
      )}
      <div className={`stats-grid ${student ? "stats-5" : ""}`}>
        <Stat
          icon={ListTodo}
          value={conta(paraFazer.length)}
          label="Para fazer"
          gray
          foot="Esperando o seu envio"
          onClick={() => navigate("atividades", "disponivel")}
        />
        <Stat
          icon={Clock3}
          value={conta(pending.length)}
          label={student ? "Enviadas" : "Aguardando revisão"}
          foot={student ? "Você pode pedir a correção da IA" : "Você recebe o resultado aqui"}
          amber
          onClick={() => navigate("atividades", "pendente")}
        />
        {student && (
          <Stat
            icon={Sparkles}
            value={conta(corrigidasIA.length)}
            label="Corrigidas pela IA"
            foot="Nota provisória, falta o professor"
            blue
            onClick={() => navigate("atividades", "corrigida_ia")}
          />
        )}
        <Stat
          icon={CheckCheck}
          value={conta(approved.length)}
          label="Atividades corrigidas"
          foot="Com revisão do professor"
          onClick={() => navigate("atividades", "aprovada")}
        />
        <Stat
          icon={Target}
          value={real ? (mediaReal != null ? `${mediaReal}%` : "--") : "67%"}
          label="Domínio médio"
          foot={real ? "Baseado nas suas correções aprovadas" : "↑ 12 pontos neste mês"}
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
            {real
              ? (mapa?.materias ?? []).map((m) => (
                  <div key={m.nome} className="topic-row">
                    <div className="topic-heading">
                      <div>
                        <strong>{m.nome}</strong>
                        <span>{atividadesCorrigidas(m.atividades)}</span>
                      </div>
                      <span className="topic-value">
                        {m.percentual}
                        <small>%</small>
                      </span>
                    </div>
                    <Progress value={m.percentual} label={`Domínio em ${m.nome}`} />
                  </div>
                ))
              : topics.map((t) => (
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
            {real && mapa !== null && !mapa.materias.length && (
              <p className="tiny muted">
                Ainda não há correções aprovadas para estimar seu domínio.
              </p>
            )}
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
          {real ? (
            recomendacao ? (
              <>
                <Badge tone="neutral">
                  Redação · {recomendacao.tema}
                </Badge>
                <h3>Seu ponto de maior oportunidade agora.</h3>
                <p>
                  Seu domínio em {recomendacao.habilidadeCodigo} ({recomendacao.tema}) está em{" "}
                  {recomendacao.percentual}%. Pratique esse critério na próxima redação.
                </p>
              </>
            ) : (
              <>
                <Badge tone="neutral">Redação</Badge>
                <h3>Envie sua primeira redação.</h3>
                <p>
                  Depois que uma correção for aprovada, mostramos aqui onde focar primeiro.
                </p>
              </>
            )
          ) : (
            <>
              <Badge tone="neutral">Redação · Coesão textual</Badge>
              <h3>
                Boas ideias merecem
                <br />
                boas conexões.
              </h3>
              <p>Pratique conectivos e deixe seus argumentos ainda mais claros.</p>
            </>
          )}
          <div className="study-meta">
            <Clock3 size={14} /> 10 minutos <span>·</span> Exercício guiado
          </div>
          <Button
            onPress={() =>
              real ? navigate("estudos") : openStudy(studyTasks[0].id)
            }
            icon={ArrowRight}
          >
            {real
              ? "Ver plano de estudo"
              : state.completed.includes("s1")
                ? "Praticar novamente"
                : "Começar a praticar"}
          </Button>
        </Card>
      </div>
      {real && mapa && mapa.materias.length > 0 && abaSub && (
        <Card>
          <SectionTitle title="Subtópicos" action="Ver evolução" onAction={() => navigate("evolucao")} />
          <p className="muted card-subtitle">Veja em que parte de cada matéria focar.</p>
          <div className="tabs" role="group" aria-label="Escolher matéria">
            {[...mapa.materias].reverse().map((m) => (
              <button
                key={m.nome}
                aria-pressed={abaSub === m.nome}
                className={abaSub === m.nome ? "active" : ""}
                onClick={() => setMateriaSub(m.nome)}
              >
                {m.nome}
              </button>
            ))}
          </div>
          {/* o cartao ja se chama "Subtopicos": o titulo de dentro so aparece na redacao (C1 a C5) */}
          {tituloSubtopicos(abaSub) !== "Subtópicos" && <h4 className="subtopicos-titulo">{tituloSubtopicos(abaSub)}</h4>}
          <div className="topic-list">
            {mapa.subtopicos[abaSub].length ? (
              mapa.subtopicos[abaSub].map((s) => (
                <div key={s.nome} className="topic-row">
                  <div className="topic-heading">
                    <div>
                      <strong>{s.nome}</strong>
                    </div>
                    <span className="topic-value">
                      {s.percentual}
                      <small>%</small>
                    </span>
                  </div>
                  <Progress value={s.percentual} label={`Domínio em ${s.nome}`} />
                </div>
              ))
            ) : (
              <p className="tiny muted">Ainda não há subtópicos nesta matéria.</p>
            )}
          </div>
        </Card>
      )}
      <Card>
        <SectionTitle
          title={student ? "Suas atividades recentes" : "Atividades da turma"}
          action="Ver todas"
          onAction={() => navigate(student ? "atividades" : "revisoes")}
        />
        <div className="activity-list">
          {recentes.map((a) => (
            <ActivityRow
              key={a.id}
              activity={a}
              onClick={() => openActivity(a)}
            />
          ))}
          {real && reais !== null && !recentes.length && (
            <p className="tiny muted">Você ainda não tem atividades.</p>
          )}
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
  blue = false,
  gray = false,
  onClick,
}: {
  icon: typeof Target;
  value: string;
  label: string;
  foot: string;
  amber?: boolean;
  blue?: boolean;
  gray?: boolean; // cinza = ainda sem fazer (mesma cor do selo "Para fazer")
  onClick?: () => void; // com onClick o cartao vira botao (leva para a lista ja filtrada)
}) {
  const conteudo = (
    <>
      <div className="stat-top">
        <span className={`stat-icon ${amber ? "stat-amber" : ""} ${blue ? "stat-blue" : ""} ${gray ? "stat-gray" : ""}`}>
          <Icon size={18} />
        </span>
        <span className="stat-value">{value}</span>
      </div>
      <strong>{label}</strong>
      <span className="stat-foot">{foot}</span>
    </>
  );
  return onClick ? (
    <button type="button" className="stat-card stat-link" onClick={onClick}>{conteudo}</button>
  ) : (
    <div className="stat-card">{conteudo}</div>
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
          {a.turmaNome && <b>{a.student} · {a.turmaNome} · </b>}
          {a.subject}
          {a.date && ` · ${a.date}`}
        </span>
      </span>
      <Badge
        tone={
          a.status === "aprovada"
            ? "green"
            : a.status === "corrigida_ia"
              ? "blue"
              : a.status === "pendente"
                ? "amber"
                : "neutral"
        }
      >
        {a.status === "aprovada"
          ? "Corrigida"
          : a.status === "corrigida_ia"
            ? "Corrigida pela IA"
            : a.status === "pendente"
              ? "Enviada"
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
