import { useCallback, useEffect, useState } from "react";
import { ShieldCheck, ShieldAlert } from "lucide-react";
import { Badge, Button, Card, Empty, SectionTitle } from "../components/ui";
import {
  logsAuditoria, logsIntegridade, logsSeguranca,
  type AuditoriaAPI, type EventoSegurancaAPI, type IntegridadeAPI,
} from "../services/api";
import type { Role } from "../types";

const POR_PAGINA = 50;
const TIPOS = ["", "LOGIN_OK", "LOGIN_FALHA", "NAO_AUTENTICADO", "ACESSO_NEGADO"];
const TOM = (t: string) => (t === "LOGIN_OK" ? "green" : t === "LOGIN_FALHA" || t === "ACESSO_NEGADO" ? "amber" : "neutral") as "green" | "amber" | "neutral";
// o banco guarda em UTC; a tela mostra no horario do navegador
const hora = (iso: string) => new Date(iso.endsWith("Z") ? iso : iso + "Z").toLocaleString("pt-BR");

type Aba = "seguranca" | "auditoria";

export function Logs({ role, notify }: { role: Role; notify: (m: string) => void }) {
  const admin = role === "admin";
  const [aba, setAba] = useState<Aba>(admin ? "seguranca" : "auditoria");
  const [tipo, setTipo] = useState("");
  const [de, setDe] = useState("");
  const [ate, setAte] = useState("");
  const [pagina, setPagina] = useState(0);
  const [seg, setSeg] = useState<EventoSegurancaAPI[]>([]);
  const [aud, setAud] = useState<AuditoriaAPI[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [integridade, setIntegridade] = useState<IntegridadeAPI | null>(null);

  const carregar = useCallback(() => {
    setCarregando(true);
    const f = { de, ate, pular: pagina * POR_PAGINA };
    const req = aba === "seguranca"
      ? logsSeguranca({ ...f, tipo }).then(setSeg)
      : logsAuditoria({ ...f, acao: tipo }).then(setAud);
    req.catch((e: Error) => notify(e.message)).finally(() => setCarregando(false));
  }, [aba, tipo, de, ate, pagina, notify]);
  useEffect(carregar, [carregar]);

  async function verificar() {
    try { setIntegridade(await logsIntegridade()); }
    catch (e) { notify((e as Error).message); }
  }
  const trocar = (a: Aba) => { setAba(a); setTipo(""); setPagina(0); };
  const linhas = aba === "seguranca" ? seg : aud;

  return (
    <div>
      <SectionTitle title={admin ? "Logs do sistema" : "Auditoria da escola"} />
      <p className="muted">
        {admin ? "Registros somente de leitura, com cadeia de hash contra adulteração. Horários no seu fuso."
          : "O que foi feito sobre os dados da sua escola. Somente leitura."}
      </p>

      {admin && (
        <Card>
          <div className="row">
            <Button icon={ShieldCheck} variant="secondary" onPress={verificar}>Verificar integridade</Button>
          </div>
          {integridade && (
            <ul className="cal-list">
              {([["Segurança", integridade.seguranca_ok, integridade.seguranca], ["Auditoria", integridade.auditoria_ok, integridade.auditoria]] as const).map(([nome, ok, msg]) => (
                <li key={nome}>
                  {ok ? <ShieldCheck size={18} color="#2e9e73" /> : <ShieldAlert size={18} color="#b97a21" />}
                  <div><strong>{nome}</strong><span className="tiny muted">{msg}</span></div>
                  <Badge tone={ok ? "green" : "amber"}>{ok ? "Íntegra" : "Adulterada"}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}

      <Card>
        {admin && (
          <div className="row">
            <Button variant={aba === "seguranca" ? "primary" : "ghost"} onPress={() => trocar("seguranca")}>Segurança</Button>
            <Button variant={aba === "auditoria" ? "primary" : "ghost"} onPress={() => trocar("auditoria")}>Auditoria</Button>
          </div>
        )}
        <div className="form-grid">
          {aba === "seguranca" ? (
            <label>Tipo
              <select value={tipo} onChange={(e) => { setTipo(e.target.value); setPagina(0); }}>
                {TIPOS.map((t) => <option key={t} value={t}>{t || "Todos"}</option>)}
              </select>
            </label>
          ) : (
            <label>Ação
              <input value={tipo} placeholder="Ex.: APROVAR" onChange={(e) => { setTipo(e.target.value.toUpperCase()); setPagina(0); }} />
            </label>
          )}
          <label>De<input type="date" value={de} onChange={(e) => { setDe(e.target.value); setPagina(0); }} /></label>
          <label>Até<input type="date" value={ate} min={de} onChange={(e) => { setAte(e.target.value); setPagina(0); }} /></label>
        </div>

        {linhas.length === 0 && !carregando ? <Empty title="Nada por aqui" text="Nenhum registro neste filtro." /> : (
          <div className="table-scroll">
            <table className="log-table">
              <thead>
                {aba === "seguranca"
                  ? <tr><th>Quando</th><th>Tipo</th><th>Quem</th><th>IP</th><th>Detalhe</th></tr>
                  : <tr><th>Quando</th><th>Ação</th><th>Quem</th>{admin && <th>Escola</th>}<th>Alvo</th><th>Resultado</th>{admin && <th>IP</th>}</tr>}
              </thead>
              <tbody>
                {aba === "seguranca"
                  ? seg.map((e) => (
                    <tr key={e.request_id + e.seq + e.tipo}>
                      <td>{hora(e.criado_em)}</td><td><Badge tone={TOM(e.tipo)}>{e.tipo}</Badge></td>
                      <td>{e.usuario ?? e.email_tentado ?? "—"}</td><td>{e.ip}</td><td>{e.detalhe ?? ""}</td>
                    </tr>))
                  : aud.map((a) => (
                    <tr key={String(a.seq) + a.entidade_id + a.criado_em}>
                      <td>{hora(a.criado_em)}</td><td>{a.acao}</td><td>{a.usuario ?? "—"}</td>
                      {admin && <td>{a.escola ?? "Plataforma"}</td>}
                      <td>{a.entidade}</td><td>{a.resultado ?? "—"}</td>{admin && <td>{a.ip ?? "—"}</td>}
                    </tr>))}
              </tbody>
            </table>
          </div>
        )}
        <div className="row">
          <Button variant="ghost" disabled={pagina === 0 || carregando} onPress={() => setPagina(pagina - 1)}>Anterior</Button>
          <span className="tiny muted">Página {pagina + 1}</span>
          <Button variant="ghost" disabled={linhas.length < POR_PAGINA || carregando} onPress={() => setPagina(pagina + 1)}>Próxima</Button>
        </div>
      </Card>
    </div>
  );
}
