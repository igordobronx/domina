import { SeletorMultiplo, Escolha } from "../components/Seletor";
import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Plus, Trash2 } from "lucide-react";
import { Badge, Button, Card, Empty, Modal, SectionTitle } from "../components/ui";
import { iso, useCalendario } from "../hooks/useCalendario";
import {
  apagarEvento, criarEvento, listarEscolas, listarTurmasMinhas,
  type EscolaAPI, type EventoPayload, type ItemCalendarioAPI, type TurmaAPI, type UsuarioAtual,
} from "../services/api";
import type { Role } from "../types";

const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const SEMANA = ["D", "S", "T", "Q", "Q", "S", "S"];
const TIPOS: EventoPayload["tipo"][] = ["AVISO", "PROVA", "ENTREGA", "REUNIAO"];
const TIPOS_ALUNO: EventoPayload["tipo"][] = ["ENTREGA", "PROVA", "AVISO"]; // lembrete pessoal do aluno
const ROTULO: Record<string, string> = { AVISO: "Aviso", PROVA: "Prova", ENTREGA: "Entrega", REUNIAO: "Reunião", FERIADO: "Feriado", META: "Meta" };
const TOM = (t: string) => (t === "FERIADO" ? "neutral" : t === "PROVA" || t === "META" ? "amber" : "green") as "green" | "amber" | "neutral";
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
  const aluno = role === "aluno"; // aluno cria so lembretes pessoais (ninguem mais ve)

  useEffect(() => {
    if (precisaEscola) listarEscolas().then((e) => { setEscolas(e); setEscolaId(e[0]?.id); }).catch(() => {});
  }, [precisaEscola]);
  useEffect(() => {
    if (!aluno && (!precisaEscola || escolaId)) listarTurmasMinhas(escolaId).then(setTurmas).catch(() => {});
  }, [aluno, precisaEscola, escolaId]);

  const hoje = iso(new Date());
  const celulas = useMemo(() => {
    const vazios = Array.from({ length: primeiro.getDay() }, () => null);
    const dias = Array.from({ length: ultimo.getDate() }, (_, i) => iso(new Date(ref.getFullYear(), ref.getMonth(), i + 1)));
    return [...vazios, ...dias];
  }, [ref]); // eslint-disable-line react-hooks/exhaustive-deps
  const doDia = (d: string) => itens.filter((i) => cobre(i, d));
  const lista = dia ? doDia(dia) : itens;

  async function apagar(i: ItemCalendarioAPI) {
    try { await apagarEvento(i.id); notify(aluno ? "Lembrete apagado." : "Evento apagado."); recarregar(); }
    catch (e) { notify((e as Error).message); }
  }

  return (
    <div className="calendar-page">
      <SectionTitle title="Calendário" />
      <p className="muted">
        {aluno
          ? "Os eventos da escola e da sua turma, mais os lembretes que você adicionar (só você vê)."
          : "O mesmo calendário para toda a escola. Atualiza sozinho."}
      </p>
      {precisaEscola && (
        <label>Instituição
          <Escolha value={escolaId ?? ""} onChange={(e) => setEscolaId(e.target.value)}>
            {escolas.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
          </Escolha>
        </label>
      )}
      <Card>
        <div className="cal-head">
          <button className="icon-btn" aria-label="Mês anterior" onClick={() => setRef(new Date(ref.getFullYear(), ref.getMonth() - 1, 1))}><ChevronLeft size={18} /></button>
          <strong>{MESES[ref.getMonth()]} de {ref.getFullYear()}</strong>
          <button className="icon-btn" aria-label="Próximo mês" onClick={() => setRef(new Date(ref.getFullYear(), ref.getMonth() + 1, 1))}><ChevronRight size={18} /></button>
          <Button icon={Plus} onPress={() => setNovo(true)}>{aluno ? "Adicionar" : role === "professor" ? "Adicionar atividade" : "Novo evento"}</Button>
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
                    {br(i.inicio)}{i.fim ? ` a ${br(i.fim)}` : ""}{i.turma ? ` · ${i.turma}` : i.origem !== "evento" ? "" : aluno && i.editavel ? " · Só você vê" : " · Escola toda"}
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
  const aluno = role === "aluno";
  const [tipo, setTipo] = useState<EventoPayload["tipo"] | "">("");
  const [inicio, setInicio] = useState(dia);
  const [fim, setFim] = useState("");
  // professor so cria para as proprias turmas (uma ou varias); gestor/admin: nenhuma marcada = escola toda
  const [turmaIds, setTurmaIds] = useState<string[]>([]);
  const [salvando, setSalvando] = useState(false);

  async function salvar() {
    if (!titulo.trim()) return notify(aluno ? "Escreva o que você precisa fazer." : "Dê um título ao evento.");
    if (!tipo) return notify("Escolha o tipo.");
    if (role === "professor" && !turmaIds.length) return notify("Escolha pelo menos uma turma.");
    setSalvando(true);
    try {
      // varias turmas: cada turma recebe o seu evento (igual aos exercicios); nenhuma = escola toda / pessoal
      const base = { titulo: titulo.trim(), descricao: descricao.trim() || undefined, tipo: tipo as EventoPayload["tipo"], inicio, fim: fim || null };
      await Promise.all((turmaIds.length ? turmaIds : [null]).map((t) => criarEvento({ ...base, turma_id: t }, escolaId)));
      notify(aluno ? "Adicionado ao seu calendário."
        : turmaIds.length > 1 ? `Adicionado ao calendário de ${turmaIds.length} turmas.`
        : turmaIds.length ? "Adicionado ao calendário da turma." : "Evento criado. Já aparece para a escola.");
      recarregar(); fechar();
    } catch (e) { notify((e as Error).message); }
    finally { setSalvando(false); }
  }

  return (
    <Modal title={aluno ? "Adicionar ao meu calendário" : role === "professor" ? "Adicionar atividade ao calendário" : "Novo evento"} onClose={fechar}>
      {aluno && <p className="tiny muted">Só você vê o que adicionar aqui.</p>}
      <div className="form-grid">
      <label>{aluno ? "O que você precisa fazer" : "Título"}<input value={titulo} maxLength={200} onChange={(e) => setTitulo(e.target.value)} /></label>
      <label>Tipo
        <Escolha value={tipo} onChange={(e) => setTipo(e.target.value as EventoPayload["tipo"])}>
          <option value="">Escolha o tipo</option>
          {(aluno ? TIPOS_ALUNO : TIPOS).map((t) => <option key={t} value={t}>{aluno && t === "AVISO" ? "Lembrete" : ROTULO[t]}</option>)}
        </Escolha>
      </label>
      <label>Início<input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} /></label>
      <label>Fim (opcional)<input type="date" value={fim} min={inicio} onChange={(e) => setFim(e.target.value)} /></label>
      </div>
      {!aluno && (
        <>
          <p className="rotulo-escolha">
            {role === "professor" ? "Turmas que vão ver (pode marcar mais de uma)" : "Turmas (nenhuma marcada = escola toda)"}
          </p>
          <SeletorMultiplo rotulo="Turmas" placeholder={role === "professor" ? "Escolha as turmas" : "Escola toda"}
            opcoes={turmas.map((t) => ({ valor: t.id, rotulo: t.nome }))} valores={turmaIds} onChange={setTurmaIds} />
          {!turmas.length && <p className="tiny muted">Você ainda não tem turmas.</p>}
        </>
      )}
      <div className="form-grid" style={{ gridTemplateColumns: "1fr" }}>
        <label>Descrição (opcional)<textarea value={descricao} maxLength={2000} onChange={(e) => setDescricao(e.target.value)} /></label>
      </div>
      <div className="row">
        <Button onPress={salvar} disabled={salvando}>{salvando ? "Salvando..." : aluno ? "Adicionar" : "Criar evento"}</Button>
        <Button variant="ghost" onPress={fechar}>Cancelar</Button>
      </div>
    </Modal>
  );
}
