import { useEffect, useRef, useState } from "react";
import { Trash2 } from "lucide-react";
import { Button } from "./ui";
import {
  apagarAnotacao, criarAnotacao, editarAnotacao, listarAnotacoes, urlImagemSubmissao,
  type AnotacaoAPI, type NovaAnotacao,
} from "../services/api";

// Foto do envio com marcas por cima: as da IA (caixas verde/vermelho, só leitura) e as do PROFESSOR
// (azul). Com `editavel`, o professor arrasta sobre a foto para marcar e escreve o comentário.
// Posições em fração da folha (0 a 1): valem em qualquer tamanho de tela e zoom.
export type PontoIA = {
  tipo: "acerto" | "erro"; comentario: string; criterio: string;
  caixa: { pagina?: number; x: number; y: number; largura: number; altura: number } | null;
};
type Caixa = Pick<NovaAnotacao, "pagina" | "x" | "y" | "largura" | "altura">;

const TIPOS = [["erro", "Erro"], ["acerto", "Acerto"], ["nota", "Comentário"]] as const;
const MIN = 0.01; // arrasto menor que 1% da folha é clique, não marca
const limitar = (v: number) => Math.min(1, Math.max(0, v));
const erroDe = (e: unknown, padrao: string) => (e instanceof Error ? e.message : padrao);

export function FotoComMarcas({ submissaoId, pontos = [], editavel = false, notify }: {
  submissaoId: string; pontos?: PontoIA[]; editavel?: boolean; notify?: (m: string) => void;
}) {
  const [urls, setUrls] = useState<string[] | null>(null);
  const [semFoto, setSemFoto] = useState(false);
  const [marcas, setMarcas] = useState<AnotacaoAPI[]>([]);
  const [arrasto, setArrasto] = useState<(Caixa & { x0: number; y0: number }) | null>(null);
  const [nova, setNova] = useState<Caixa | null>(null);
  const [tipo, setTipo] = useState<AnotacaoAPI["tipo"]>("erro");
  const [texto, setTexto] = useState("");
  const [editando, setEditando] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);
  const aviso = (m: string) => (notify ? notify(m) : undefined);
  const carregarMarcas = () => listarAnotacoes(submissaoId).then(setMarcas).catch(() => setMarcas([]));

  useEffect(() => {
    let ativo = true;
    (async () => {
      const achadas: string[] = [];
      for (let n = 0; n < 6; n++) { // as folhas vêm pelo índice até a primeira que não existe
        try { achadas.push(await urlImagemSubmissao(submissaoId, n)); } catch { break; }
      }
      if (!ativo) return;
      if (achadas.length) setUrls(achadas); else setSemFoto(true);
    })();
    carregarMarcas();
    return () => { ativo = false; };
  }, [submissaoId]);

  const ponto = (e: React.PointerEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    return { x: limitar((e.clientX - r.left) / r.width), y: limitar((e.clientY - r.top) / r.height) };
  };
  const comeca = (e: React.PointerEvent<HTMLDivElement>, pagina: number) => {
    if (!editavel || e.button !== 0) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    const { x, y } = ponto(e);
    setNova(null);
    setArrasto({ pagina, x, y, x0: x, y0: y, largura: 0, altura: 0 });
  };
  const move = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!arrasto) return;
    const { x, y } = ponto(e);
    setArrasto({ ...arrasto, x: Math.min(x, arrasto.x0), y: Math.min(y, arrasto.y0),
      largura: Math.abs(x - arrasto.x0), altura: Math.abs(y - arrasto.y0) });
  };
  const termina = () => {
    if (!arrasto) return;
    const { x0, y0, ...caixa } = arrasto;
    setArrasto(null);
    if (caixa.largura >= MIN && caixa.altura >= MIN) { setNova(caixa); setTexto(""); setTipo("erro"); }
  };

  const salvar = async () => {
    if (!nova || !texto.trim()) return aviso("Escreva o comentário da marca.");
    setSalvando(true);
    try { await criarAnotacao(submissaoId, { ...nova, tipo, comentario: texto.trim() }); setNova(null); await carregarMarcas(); }
    catch (e) { aviso(erroDe(e, "Não foi possível salvar a marca.")); }
    finally { setSalvando(false); }
  };
  const salvarEdicao = async (m: AnotacaoAPI) => {
    if (!texto.trim()) return aviso("Escreva o comentário da marca.");
    try { await editarAnotacao(m.id, { comentario: texto.trim() }); setEditando(null); await carregarMarcas(); }
    catch (e) { aviso(erroDe(e, "Não foi possível salvar.")); }
  };
  const apagar = async (m: AnotacaoAPI) => {
    if (!window.confirm("Apagar esta marca?")) return;
    try { await apagarAnotacao(m.id); await carregarMarcas(); }
    catch (e) { aviso(erroDe(e, "Não foi possível apagar.")); }
  };

  if (semFoto) return <p className="tiny">Não foi possível carregar a foto original.</p>;
  if (!urls) return <p className="tiny">Carregando foto...</p>;
  const estilo = (c: Caixa) => ({ left: `${c.x * 100}%`, top: `${c.y * 100}%`, width: `${c.largura * 100}%`, height: `${c.altura * 100}%` });
  return (
    <div className="foto-marcas">
      {editavel && <p className="tiny muted">Arraste sobre a foto para marcar um trecho e escrever um comentário.</p>}
      {urls.map((url, n) => (
        <div key={n}>
          {urls.length > 1 && <p className="tiny muted">Folha {n + 1} de {urls.length}</p>}
          <div className={`imagem-com-caixas${editavel ? " marcavel" : ""}`}
            onPointerDown={(e) => comeca(e, n)} onPointerMove={move} onPointerUp={termina}>
            <img src={url} draggable={false} alt={urls.length > 1 ? `Folha ${n + 1}` : "Foto enviada"} />
            {pontos.map((p, k) => p.caixa && (p.caixa.pagina ?? 0) === n && (
              <div key={`ia${k}`} className={`caixa ponto-${p.tipo}`} style={estilo({ pagina: n, ...p.caixa })}
                title={`IA · ${p.criterio} · ${p.tipo === "acerto" ? "acerto" : "erro"}: ${p.comentario}`} />
            ))}
            {marcas.filter((m) => m.pagina === n).map((m) => (
              <div key={m.id} className={`caixa marca-prof marca-${m.tipo}`} style={estilo(m)} title={`${m.autor_nome}: ${m.comentario}`} />
            ))}
            {arrasto && arrasto.pagina === n && <div className="caixa marca-prof marca-nova" style={estilo(arrasto)} />}
            {nova && nova.pagina === n && <div className="caixa marca-prof marca-nova" style={estilo(nova)} />}
          </div>
        </div>
      ))}
      {nova && (
        <div className="marca-form">
          <div className="botoes-escolha" role="group" aria-label="Tipo da marca">
            {TIPOS.map(([v, rotulo]) => (
              <button key={v} type="button" aria-pressed={tipo === v} className={tipo === v ? "active" : ""} onClick={() => setTipo(v)}>{rotulo}</button>
            ))}
          </div>
          <textarea rows={2} value={texto} autoFocus onChange={(e) => setTexto(e.target.value)} placeholder="Escreva o comentário para o aluno" />
          <div className="form-actions">
            <Button variant="secondary" onPress={() => setNova(null)}>Cancelar</Button>
            <Button disabled={salvando} onPress={salvar}>{salvando ? "Salvando..." : "Salvar marca"}</Button>
          </div>
        </div>
      )}
      {marcas.length > 0 && (
        <ul className="marca-lista">
          {marcas.map((m) => (
            <li key={m.id} className={`marca-${m.tipo}`}>
              <strong>{m.autor_nome}</strong> · folha {m.pagina + 1} · {TIPOS.find(([v]) => v === m.tipo)?.[1]}
              {editando === m.id ? (
                <>
                  <textarea rows={2} value={texto} onChange={(e) => setTexto(e.target.value)} />
                  <div className="form-actions">
                    <Button variant="secondary" onPress={() => setEditando(null)}>Cancelar</Button>
                    <Button onPress={() => salvarEdicao(m)}>Salvar</Button>
                  </div>
                </>
              ) : (
                <p>{m.comentario}</p>
              )}
              {editavel && m.minha && editando !== m.id && (
                <span className="marca-acoes">
                  <button className="back-link" onClick={() => { setEditando(m.id); setTexto(m.comentario); }}>Editar</button>
                  <button className="back-link" aria-label="Apagar marca" onClick={() => apagar(m)}><Trash2 size={15} /></button>
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
