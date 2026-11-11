import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Plus, Trash2 } from "lucide-react";
import { Badge, Button, Card, Empty, SectionTitle } from "../components/ui";
import { iso, useCalendario } from "../hooks/useCalendario";
import {
  apagarEvento, criarEvento, listarEscolas, listarTurmasMinhas,
  type EscolaAPI, type EventoPayload, type ItemCalendarioAPI, type TurmaAPI, type UsuarioAtual,
} from "../services/api";
import type { Role } from "../types";

const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const SEMANA = ["D", "S", "T", "Q", "Q", "S", "S"];
const TIPOS: EventoPayload["tipo"][] = ["AVISO", "PROVA", "ENTREGA", "REUNIAO"];
const ROTULO: Record<string, string> = { AVISO: "Aviso", PROVA: "Prova", ENTREGA: "Entrega", REUNIAO: "Reunião", FERIADO: "Feriado" };
const TOM = (t: string) => (t === "FERIADO" ? "neutral" : t === "PROVA" ? "amber" : "green") as "green" | "amber" | "neutral";
const br = (d: string) => d.split("-").reverse().join("/");

// um item "cobre" o dia se inicio <= dia <= fim (fim nulo = so o proprio dia)
const cobre = (i: ItemCalendarioAPI, dia: string) => i.inicio <= dia && dia <= (i.fim ?? i.inicio);

export function Calendar({ role, notify }: { role: Role; notify: (m: string) => void; currentUser?: UsuarioAtual | null }) {
  const [ref, setRef] = useState(() => { const d = new Date(); d.setDate(1); return d; });
  const [escolas, setEscolas] = useState<EscolaAPI[]>([]);
  const [escolaId, setEscolaId] = useState<string>();
  const [turmas, setTurmas] = useState<TurmaAPI[]>([]);
  const [novo, setNovo] = useState(false);
  const [dia, setDia] = useState<string | null>(null);

  const primeiro = new Date(ref.getFullYear(), ref.getMonth(), 1);
  const ultimo = new Date(ref.getFullYear(), ref.getMonth() + 1, 0);
  const de = iso(primeiro), ate = iso(ultimo);
  const precisaEscola = role === "admin";
  const { itens, erro, recarregar } = useCalendario(de, ate, precisaEscola ? escolaId : undefined);
  const podeCriar = role !== "aluno";

  useEffect(() => {
    if (precisaEscola) listarEscolas().then((e) => { setEscolas(e); setEscolaId(e[0]?.id); }).catch(() => {});
  }, [precisaEscola]);
  useEffect(() => {
    if (podeCriar && (!precisaEscola || escolaId)) listarTurmasMinhas(escolaId).then(setTurmas).catch(() => {});
  }, [podeCriar, precisaEscola, escolaId]);

  const hoje = iso(new Date());
  const celulas = useMemo(() => {
    const vazios = Array.from({ length: primeiro.getDay() }, () => null);
    const dias = Array.from({ length: ultimo.getDate() }, (_, i) => iso(new Date(ref.getFullYear(), ref.getMonth(), i + 1)));
    return [...vazios, ...dias];
  }, [ref]); // eslint-disable-line react-hooks/exhaustive-deps
  const doDia = (d: string) => itens.filter((i) => cobre(i, d));
  const lista = dia ? doDia(dia) : itens;

  async function apagar(i: ItemCalendarioAPI) {
    try { await apagarEvento(i.id); notify("Evento apagado."); recarregar(); }
    catch (e) { notify((e as Error).message); }
  }

  return (
    <div className="calendar-page">
      <SectionTitle title="Calendário" />
      <p className="muted">O mesmo calendário para toda a escola. Atualiza sozinho.</p>
      {precisaEscola && (
        <label>Instituição
          <select value={escolaId ?? ""} onChange={(e) => setEscolaId(e.target.value)}>
            {escolas.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
          </select>
        </label>
      )}
      <Card>
        <div className="cal-head">
          <button className="icon-btn" aria-label="Mês anterior" onClick={() => setRef(new Date(ref.getFullYear(), ref.getMonth() - 1, 1))}><ChevronLeft size={18} /></button>
          <strong>{MESES[ref.getMonth()]} de {ref.getFullYear()}</strong>
          <button className="icon-btn" aria-label="Próximo mês" onClick={() => setRef(new Date(ref.getFullYear(), ref.getMonth() + 1, 1))}><ChevronRight size={18} /></button>
          {podeCriar && <Button icon={Plus} onPress={() => setNovo(!novo)}>Novo evento</Button>}
        </div>
        {erro && <p className="error">{erro}</p>}
        <div className="cal-grid">
          {SEMANA.map((s, i) => <span key={i} className="cal-dow">{s}</span>)}
          {celulas.map((d, i) => d === null ? <span key={i} /> : (
            <button key={d} className={`cal-day${d === hoje ? " today" : ""}${d === dia ? " sel" : ""}`}
              onClick={() => setDia(d === dia ? null : d)} aria-label={br(d)}>
              {Number(d.slice(8))}
              <span className="cal-dots">{doDia(d).slice(0, 3).map((x) => <i key={x.id} className={`dot dot-${x.tipo}`} />)}</span>
            </button>
          ))}
        </div>
      </Card>

      {novo && <NovoEvento turmas={turmas} role={role} escolaId={escolaId} dia={dia ?? hoje}
        fechar={() => setNovo(false)} notify={notify} recarregar={recarregar} />}

      <Card>
        <SectionTitle title={dia ? `Dia ${br(dia)}` : `Neste mês`} />
        {lista.length === 0 ? <Empty title="Nada por aqui" text="Nenhum evento neste período." /> : (
          <ul className="cal-list">
            {lista.map((i) => (
              <li key={i.id}>
                <div>
                  <strong>{i.titulo}</strong>
                  <span className="tiny muted">
                    {br(i.inicio)}{i.fim ? ` a ${br(i.fim)}` : ""}{i.turma ? ` · ${i.turma}` : i.origem === "evento" ? " · Escola toda" : ""}
                  </span>
                  {i.descricao && <span className="tiny">{i.descricao}</span>}
                </div>
                <Badge tone={TOM(i.tipo)}>{ROTULO[i.tipo] ?? i.tipo}</Badge>
                {i.editavel && <button className="icon-btn" aria-label={`Apagar ${i.titulo}`} onClick={() => apagar(i)}><Trash2 size={16} /></button>}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

function NovoEvento({ turmas, role, escolaId, dia, fechar, notify, recarregar }: {
  turmas: TurmaAPI[]; role: Role; escolaId?: string; dia: string;
  fechar: () => void; notify: (m: string) => void; recarregar: () => void;
}) {
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [tipo, setTipo] = useState<EventoPayload["tipo"]>("AVISO");
  const [inicio, setInicio] = useState(dia);
  const [fim, setFim] = useState("");
  // professor so cria para as proprias turmas; gestor/admin podem deixar "escola toda"
  const [turmaId, setTurmaId] = useState("");
  const [salvando, setSalvando] = useState(false);

  async function salvar() {
    if (!titulo.trim()) return notify("Dê um título ao evento.");
    if (role === "professor" && !turmaId) return notify("Escolha a turma do evento.");
    setSalvando(true);
    try {
      await criarEvento({ titulo: titulo.trim(), descricao: descricao.trim() || undefined, tipo, inicio, fim: fim || null, turma_id: turmaId || null }, escolaId);
      notify("Evento criado. Já aparece para a escola.");
      recarregar(); fechar();
    } catch (e) { notify((e as Error).message); }
    finally { setSalvando(false); }
  }

  return (
    <Card>
      <SectionTitle title="Novo evento" />
      <label>Título<input value={titulo} maxLength={200} onChange={(e) => setTitulo(e.target.value)} /></label>
      <label>Tipo
        <select value={tipo} onChange={(e) => setTipo(e.target.value as EventoPayload["tipo"])}>
          {TIPOS.map((t) => <option key={t} value={t}>{ROTULO[t]}</option>)}
        </select>
      </label>
      <label>Início<input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} /></label>
      <label>Fim (opcional)<input type="date" value={fim} min={inicio} onChange={(e) => setFim(e.target.value)} /></label>
      <label>Para quem
        <select value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
          {role !== "professor" && <option value="">Escola toda</option>}
          {role === "professor" && <option value="">Escolha a turma…</option>}
          {turmas.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
        </select>
      </label>
      <label>Descrição (opcional)<textarea value={descricao} maxLength={2000} onChange={(e) => setDescricao(e.target.value)} /></label>
      <div className="row">
        <Button onPress={salvar} disabled={salvando}>{salvando ? "Salvando..." : "Criar evento"}</Button>
        <Button variant="ghost" onPress={fechar}>Cancelar</Button>
      </div>
    </Card>
  );
}
