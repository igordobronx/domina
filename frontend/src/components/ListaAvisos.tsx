import {
  BookOpen, CalendarDays, CheckCircle2, Clock, Flame, Inbox, NotebookPen, Sparkles, Target, Trophy, Bell,
  type LucideIcon,
} from "lucide-react";
import type { AvisoAPI } from "../services/api";

const ICONE: Record<string, LucideIcon> = {
  ATIVIDADE_NOVA: BookOpen, CORRIGIDA: CheckCircle2, EXERCICIO_NOVO: NotebookPen, NIVEL: Trophy, CONQUISTA: Trophy,
  META: Target, PRAZO: Clock, SEM_ENVIO: Clock, PARADOS: Clock, FERIADO: CalendarDays, EVENTO: CalendarDays,
  SEQUENCIA: Flame, ENVIO: Inbox, IA_CORRIGIU: Sparkles,
};

const quando = (iso: string) => new Date(iso + "Z");
const hojeStr = () => new Date().toDateString();

// avisos agrupados em "Hoje" e "Antes"; os que ainda eram novos ao abrir ficam destacados; clicar abre a tela do aviso
export function ListaAvisos({ itens, novos, onAbrir }: {
  itens: AvisoAPI[]; novos: Set<string>; onAbrir: (destino: string | null) => void;
}) {
  if (!itens.length) return <p className="muted">Nenhuma notificação por enquanto.</p>;
  const grupos = [
    ["Hoje", itens.filter((a) => quando(a.criado_em).toDateString() === hojeStr())],
    ["Antes", itens.filter((a) => quando(a.criado_em).toDateString() !== hojeStr())],
  ] as const;
  return (
    <div className="aviso-lista">
      {grupos.filter(([, l]) => l.length).map(([nome, lista]) => (
        <section key={nome}>
          <h4>{nome}</h4>
          {lista.map((a) => {
            const Icone = ICONE[a.tipo] ?? Bell;
            return (
              <button key={a.id} className={`aviso-item ${novos.has(a.id) ? "novo" : ""}`} onClick={() => onAbrir(a.destino)}>
                <span className="aviso-icone"><Icone size={18} /></span>
                <span className="aviso-texto">
                  <span>{a.texto}</span>
                  <small>{quando(a.criado_em).toLocaleString("pt-BR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</small>
                </span>
              </button>
            );
          })}
        </section>
      ))}
    </div>
  );
}
