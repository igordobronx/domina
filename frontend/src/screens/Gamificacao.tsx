import { useEffect, useState, type ReactNode } from "react";
import {
  Award,
  Check,
  Clock3,
  Dumbbell,
  Flag,
  Flame,
  Footprints,
  Lock,
  PenLine,
  Target,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { Card, SectionTitle } from "../components/ui";
import { minhaGamificacao, type GamificacaoAPI } from "../services/api";

// icone de cada conquista (codigos vem do backend: app/gamificacao.py, CONQUISTAS)
const ICONE: Record<string, LucideIcon> = {
  PRIMEIRO_PASSO: Footprints,
  PONTUAL: Clock3,
  REDATOR: PenLine,
  NOTA_900: Award,
  MAO_NA_MASSA: Dumbbell,
  CERTEIRO: Target,
  CONSTANCIA: Flame,
  IMPARAVEL: Zap,
  META_BATIDA: Flag,
};

// mesma tabela do backend, so para o aluno saber o que vale a pena fazer
const COMO_GANHAR: [string, string][] = [
  ["Enviar uma atividade", "+10"],
  ["Enviar dentro do prazo", "+5"],
  ["Professor aprovou a correção", "+5"],
  ["Nota aprovada de 80% ou mais", "+10"],
  ["Responder um exercício", "+2"],
  ["Acertar um exercício", "+3"],
  ["Cumprir uma meta", "pontos da meta"],
  ["7 dias seguidos estudando", "+15"],
  ["Ganhar uma conquista", "+20"],
];

const dataCurta = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });

// "Minha evolucao" do aluno: nivel e sequencia no topo, o conteudo da tela (children) no meio,
// e conquistas + historico de XP por ultimo
export function PainelXP({ alunoId, children }: { alunoId: string; children?: ReactNode }) {
  const [dados, setDados] = useState<GamificacaoAPI | null>(null);
  const [erro, setErro] = useState(false);

  useEffect(() => {
    minhaGamificacao().then(setDados).catch(() => setErro(true));
  }, [alunoId]);

  if (erro) return <>{children}</>; // a evolucao continua aparecendo mesmo se o XP falhar
  if (!dados) return <><Card className="xp-carregando"><p className="tiny muted">Carregando seu nível...</p></Card>{children}</>;

  const { nivel, sequencia, conquistas, historico } = dados;
  const noMax = nivel.pontos_proximo == null;
  const faixa = noMax ? 1 : nivel.pontos_proximo! - nivel.pontos_nivel_atual;
  const pct = noMax ? 100 : Math.min(100, ((nivel.pontos - nivel.pontos_nivel_atual) / faixa) * 100);
  const ganhas = conquistas.filter((c) => c.conquistada_em).length;

  return (
    <>
      <div className="xp-topo">
        <Card className="xp-nivel">
          <div className="xp-nivel-linha">
            <div className="xp-selo" aria-hidden="true">{nivel.nivel}</div>
            <div className="xp-nivel-texto">
              <span className="eyebrow">SEU NÍVEL</span>
              <h2>Nível {nivel.nivel} · {nivel.nome}</h2>
              <strong className="xp-total">{nivel.pontos} XP</strong>
            </div>
          </div>
          <div
            className="xp-barra"
            role="progressbar"
            aria-label="XP até o próximo nível"
            aria-valuenow={Math.round(pct)}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <span style={{ width: `${pct}%` }} />
          </div>
          <p className="tiny muted">
            {noMax
              ? "Você chegou ao nível máximo. Lenda!"
              : `Faltam ${nivel.pontos_proximo! - nivel.pontos} XP para ${nivel.nome_proximo ?? `o nível ${nivel.nivel + 1}`}`}
          </p>
        </Card>
        <Card className={`xp-sequencia ${sequencia.atual ? "ativa" : ""}`}>
          <Flame size={28} aria-hidden="true" />
          <div>
            <strong className="xp-dias">
              {sequencia.atual} {sequencia.atual === 1 ? "dia seguido" : "dias seguidos"}
            </strong>
            <p className="tiny muted">Seu recorde: {sequencia.melhor} {sequencia.melhor === 1 ? "dia" : "dias"}</p>
            <p className="xp-hoje">
              {sequencia.estudou_hoje ? (
                <><Check size={13} /> Você já estudou hoje</>
              ) : (
                "Envie uma atividade ou faça um exercício hoje para manter a sequência"
              )}
            </p>
          </div>
        </Card>
      </div>

      {children}

      <Card>
        <SectionTitle title={`Conquistas · ${ganhas} de ${conquistas.length}`} />
        <div className="xp-conquistas">
          {conquistas.map((c) => {
            const Icone = c.conquistada_em ? (ICONE[c.codigo] ?? Award) : Lock;
            return (
              <div key={c.codigo} className={`xp-conquista ${c.conquistada_em ? "ganha" : ""}`}>
                <span className="xp-conquista-icone"><Icone size={20} /></span>
                <strong>{c.nome}</strong>
                <span className="tiny muted">{c.descricao}</span>
                <span className="xp-conquista-pe">
                  {c.conquistada_em ? `Conquistada em ${dataCurta(c.conquistada_em)}` : `${c.progresso} de ${c.alvo}`}
                </span>
                {!c.conquistada_em && (
                  <span className="xp-mini-barra" aria-hidden="true">
                    <span style={{ width: `${(c.progresso / c.alvo) * 100}%` }} />
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      <div className="xp-baixo">
        <Card>
          <SectionTitle title="De onde veio seu XP" />
          {historico.length ? (
            <ul className="xp-historico">
              {historico.map((h, i) => (
                <li key={`${h.data}-${i}`}>
                  <b>+{h.xp} XP</b>
                  <span>{h.motivo}</span>
                  <span className="tiny muted">{dataCurta(h.data)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="tiny muted">Envie sua primeira atividade ou responda um exercício para ganhar XP.</p>
          )}
        </Card>
        <Card>
          <SectionTitle title="Como ganhar XP" />
          <ul className="xp-regras">
            {COMO_GANHAR.map(([acao, xp]) => (
              <li key={acao}><span>{acao}</span><b>{xp}</b></li>
            ))}
          </ul>
          <p className="tiny muted">Exercícios valem até 30 XP por dia. Nota da IA não conta: só a do professor.</p>
        </Card>
      </div>
    </>
  );
}
