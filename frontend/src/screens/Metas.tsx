import { Escolha } from "../components/Seletor";
import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { Badge, Button, Card, Empty, Modal, Progress, SectionTitle } from "../components/ui";
import {
  arquivarMeta, criarMeta, editarMeta, listarMaterias, listarMetas, listarTurmasMinhas, minhasMetas, rankingMetas,
  type MateriaAPI, type MetaAlunoAPI, type MetaAPI, type NivelAPI, type RankingItemAPI, type TipoMetaAPI,
  type TurmaAPI, type UsuarioAtual,
} from "../services/api";
import type { Role } from "../types";

const TIPOS: { value: TipoMetaAPI; label: string; unidade: "entregas" | "%" }[] = [
  { value: "ENTREGAS", label: "Entregar atividades", unidade: "entregas" },
  { value: "ENTREGAS_NO_PRAZO", label: "Entregar atividades no prazo", unidade: "entregas" },
  { value: "NOTA_ATIVIDADE", label: "Tirar pelo menos X% numa atividade", unidade: "%" },
  { value: "MEDIA_MATERIA", label: "Média de X% numa matéria", unidade: "%" },
  { value: "DOMINIO_COMPETENCIA", label: "Domínio de X% numa competência da redação", unidade: "%" },
  { value: "PRATICA_RESPONDIDOS", label: "Resolver exercícios do plano de estudo", unidade: "entregas" },
  { value: "PRATICA_ACERTOS", label: "Acertar exercícios do plano de estudo", unidade: "entregas" },
];
const br = (d: string) => d.split("-").reverse().join("/");
const unidade = (t: TipoMetaAPI) => (TIPOS.find((x) => x.value === t)?.unidade === "%" ? "%" : "");

export function Metas({ role, notify, currentUser }: { role: Role; notify: (m: string) => void; currentUser?: UsuarioAtual | null }) {
  if (role === "aluno") return <MetasAluno notify={notify} currentUser={currentUser} />;
  return <MetasEquipe role={role} notify={notify} />;
}

/* ---------------- aluno: nivel + metas ---------------- */

function MetasAluno({ notify, currentUser }: { notify: (m: string) => void; currentUser?: UsuarioAtual | null }) {
  const [dados, setDados] = useState<{ nivel: NivelAPI; metas: MetaAlunoAPI[] } | null>(null);
  useEffect(() => {
    minhasMetas().then((d) => {
      setDados(d);
      // comemora quando o nivel e maior que o da ultima visita (so um aviso, o nivel e sempre calculado no servidor)
      const chave = `domina.nivel.${currentUser?.id ?? ""}`;
      try {
        const antes = Number(localStorage.getItem(chave) ?? 0);
        if (antes && d.nivel.nivel > antes) notify(`Você subiu para o nível ${d.nivel.nivel} — ${d.nivel.nome}!`);
        localStorage.setItem(chave, String(d.nivel.nivel));
      } catch { /* sem storage */ }
    }).catch(() => notify("Não foi possível carregar suas metas."));
  }, []);
  if (!dados) return <Empty title="Carregando..." text="Buscando suas metas." />;
  const { nivel, metas } = dados;
  const falta = nivel.pontos_proximo != null ? nivel.pontos_proximo - nivel.pontos : null;
  const pct = nivel.pontos_proximo == null ? 100
    : ((nivel.pontos - nivel.pontos_nivel_atual) / (nivel.pontos_proximo - nivel.pontos_nivel_atual)) * 100;
  const andamento = metas.filter((m) => m.status === "EM_ANDAMENTO" || m.status === "FUTURA");
  const outras = metas.filter((m) => m.status === "CONCLUIDA" || m.status === "ENCERRADA");
  return (
    <>
      <div className="page-heading"><div><h1>Metas e níveis</h1><p>Cumpra metas e ganhe XP para subir de nível. Seus envios e exercícios também dão XP.</p></div></div>
      <Card>
        <div className="nivel-card">
          <div className="nivel-numero">{nivel.nivel}</div>
          <div>
            <strong>{nivel.nome}</strong>
            <p className="tiny muted">
              {nivel.pontos} XP{falta != null ? ` · faltam ${falta} XP para o próximo nível` : " · nível máximo!"}
            </p>
          </div>
        </div>
        <Progress value={Math.round(pct)} label="Progresso até o próximo nível" />
      </Card>
      <Card>
        <SectionTitle title="Em andamento" />
        {andamento.length ? andamento.map((m) => <MetaLinha key={m.id} m={m} />) : (
          <p className="muted">Nenhuma meta ativa agora. Quando seu professor criar uma, ela aparece aqui.</p>
        )}
      </Card>
      {outras.length > 0 && (
        <Card>
          <SectionTitle title="Concluídas e encerradas" />
          {outras.map((m) => <MetaLinha key={m.id} m={m} />)}
        </Card>
      )}
    </>
  );
}

function MetaLinha({ m }: { m: MetaAlunoAPI }) {
  const u = unidade(m.tipo);
  const tom = m.status === "CONCLUIDA" ? "green" : m.status === "ENCERRADA" ? "neutral" : "amber";
  const rotulo = { CONCLUIDA: "Concluída", ENCERRADA: "Encerrada", FUTURA: `Começa em ${br(m.inicio)}`, EM_ANDAMENTO: "Em andamento" }[m.status];
  return (
    <div className="meta-linha">
      <div className="meta-topo">
        <strong>{m.titulo}</strong>
        <span><Badge tone={tom}>{rotulo}</Badge> <b>+{m.pontos} XP</b></span>
      </div>
      {m.descricao && <p className="tiny muted">{m.descricao}</p>}
      <Progress value={Math.round((m.progresso / m.alvo) * 100)} label={m.titulo} />
      <p className="tiny muted">
        {m.progresso}{u} de {m.alvo}{u}{m.fim ? ` · até ${br(m.fim)}` : ""}
      </p>
    </div>
  );
}

/* ---------------- professor / gestor: criar, acompanhar, ranking ---------------- */

function MetasEquipe({ role, notify }: { role: Role; notify: (m: string) => void }) {
  const [metas, setMetas] = useState<MetaAPI[] | null>(null);
  const [turmas, setTurmas] = useState<TurmaAPI[]>([]);
  const [materias, setMaterias] = useState<MateriaAPI[]>([]);
  const [criando, setCriando] = useState(false);
  const [editando, setEditando] = useState<MetaAPI | null>(null);
  const recarregar = () => listarMetas().then(setMetas).catch(() => notify("Não foi possível carregar as metas."));
  useEffect(() => {
    recarregar();
    listarTurmasMinhas().then(setTurmas).catch(() => {});
    listarMaterias().then(setMaterias).catch(() => {});
  }, []);
  const arquivar = async (m: MetaAPI) => {
    if (!window.confirm(`Arquivar a meta "${m.titulo}"? O XP de quem já cumpriu continua.`)) return;
    try { await arquivarMeta(m.id); notify("Meta arquivada."); recarregar(); }
    catch (e) { notify(e instanceof Error ? e.message : "Não foi possível arquivar."); }
  };
  return (
    <>
      <div className="page-heading">
        <div><h1>Metas e níveis</h1><p>Crie metas para os alunos cumprirem e acompanhe o ranking de XP.</p></div>
        <Button icon={Plus} onPress={() => { setEditando(null); setCriando(true); }}>Nova meta</Button>
      </div>
      {editando && (
        <Modal title="Editar meta" largo onClose={() => setEditando(null)}>
          <EditarMeta meta={editando} notify={notify} onFechar={() => setEditando(null)}
            onSalva={() => { setEditando(null); recarregar(); }} />
        </Modal>
      )}
      {criando && (
        <Modal title="Nova meta" largo onClose={() => setCriando(false)}>
          <NovaMeta role={role} turmas={turmas} materias={materias} notify={notify}
            onFechar={() => setCriando(false)} onCriada={() => { setCriando(false); recarregar(); }} />
        </Modal>
      )}
      <Card>
        <SectionTitle title="Metas ativas" />
        {metas === null ? <p className="muted">Carregando...</p> : !metas.length ? (
          <Empty title="Nenhuma meta ainda" text="Crie a primeira meta para os alunos." />
        ) : metas.map((m) => (
          <div className="meta-linha" key={m.id}>
            <div className="meta-topo">
              <strong>{m.titulo}</strong>
              <span><Badge tone="neutral">{m.escopo === "ESCOLA" ? "Escola toda" : m.escopo_nome}</Badge> <b>+{m.pontos} XP</b></span>
            </div>
            <p className="tiny muted">
              {TIPOS.find((t) => t.value === m.tipo)?.label.replace("X", String(m.alvo)) ?? m.tipo}
              {TIPOS.find((t) => t.value === m.tipo)?.unidade === "entregas" ? ` (${m.alvo})` : ""}
              {" · "}desde {br(m.inicio)}{m.fim ? ` até ${br(m.fim)}` : ""}
            </p>
            <Progress value={m.alunos_alvo ? Math.round((m.concluidos / m.alunos_alvo) * 100) : 0} label={`Concluíram ${m.titulo}`} />
            <p className="tiny muted">{m.concluidos} de {m.alunos_alvo} aluno(s) concluíram</p>
            {m.pode_editar && (
              <div className="form-actions left">
                <Button variant="secondary" icon={Pencil} onPress={() => { setCriando(false); setEditando(m); }}>Editar</Button>
                <Button variant="ghost" icon={Trash2} onPress={() => arquivar(m)}>Arquivar</Button>
              </div>
            )}
          </div>
        ))}
      </Card>
      <Ranking role={role} turmas={turmas} notify={notify} />
    </>
  );
}

// Edita uma meta. Titulo, descricao e fim sempre; alvo e pontos so enquanto ninguem concluiu
// (o servidor confere: depois disso muda o nivel de alguem, entao responde 409).
function EditarMeta({ meta, notify, onFechar, onSalva }: {
  meta: MetaAPI; notify: (m: string) => void; onFechar: () => void; onSalva: () => void;
}) {
  const congelada = meta.concluidos > 0;
  const percentual = TIPOS.find((t) => t.value === meta.tipo)?.unidade === "%";
  const [titulo, setTitulo] = useState(meta.titulo);
  const [descricao, setDescricao] = useState(meta.descricao ?? "");
  const [fim, setFim] = useState(meta.fim ?? "");
  const [alvo, setAlvo] = useState(meta.alvo);
  const [pontos, setPontos] = useState(meta.pontos);
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const salvar = async () => {
    if (!titulo.trim()) return setErro("Dê um título para a meta.");
    if (fim && fim < meta.inicio) return setErro("O fim não pode ser antes do início.");
    setSalvando(true); setErro("");
    try {
      await editarMeta(meta.id, {
        titulo: titulo.trim(), descricao: descricao.trim() || null, fim: fim || null,
        ...(congelada ? {} : { alvo, pontos }),
      });
      notify("Meta atualizada.");
      onSalva();
    } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível salvar."); }
    finally { setSalvando(false); }
  };
  return (
    <Card>
      <SectionTitle title="Editar meta" />
      <p className="tiny muted">
        {meta.escopo === "ESCOLA" ? "Escola toda" : meta.escopo_nome} · começa em {br(meta.inicio)}
        {congelada && " · já há alunos que concluíram: o alvo e os pontos não mudam mais (crie uma nova meta para isso)."}
      </p>
      <div className="form-grid">
        <label>Título<input value={titulo} onChange={(e) => setTitulo(e.target.value)} /></label>
        <label>Descrição (opcional)<textarea rows={2} value={descricao} onChange={(e) => setDescricao(e.target.value)} /></label>
        <label>Termina em (vazio = sem fim)<input type="date" value={fim} onChange={(e) => setFim(e.target.value)} /></label>
        {!congelada && (
          <>
            <label>{percentual ? "Percentual (X)" : "Quantidade"}
              <input type="number" min={1} max={percentual ? 100 : 1000} value={alvo} onChange={(e) => setAlvo(Number(e.target.value))} />
            </label>
            <label>XP que a meta vale
              <Escolha value={pontos} onChange={(e) => setPontos(Number(e.target.value))}>
                {[...new Set([10, 20, 30, 50, 100, meta.pontos])].sort((a, b) => a - b).map((p) => <option key={p} value={p}>{p}</option>)}
              </Escolha>
            </label>
          </>
        )}
      </div>
      {erro && <p className="error" role="alert">{erro}</p>}
      <div className="form-actions left">
        <Button variant="secondary" onPress={onFechar}>Cancelar</Button>
        <Button onPress={salvar} disabled={salvando}>{salvando ? "Salvando..." : "Salvar alterações"}</Button>
      </div>
    </Card>
  );
}

function NovaMeta({ role, turmas, materias, notify, onFechar, onCriada }: {
  role: Role; turmas: TurmaAPI[]; materias: MateriaAPI[]; notify: (m: string) => void; onFechar: () => void; onCriada: () => void;
}) {
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [tipo, setTipo] = useState<TipoMetaAPI | "">(""); // nada vem pre-selecionado
  const [alvoTxt, setAlvoTxt] = useState("");
  const alvo = Number(alvoTxt);
  const [materiaId, setMateriaId] = useState("");
  const [competencia, setCompetencia] = useState("");
  const [pontosTxt, setPontosTxt] = useState("");
  const pontos = Number(pontosTxt);
  const [inicio, setInicio] = useState(new Date().toISOString().slice(0, 10));
  const [fim, setFim] = useState("");
  const [escopo, setEscopo] = useState<"" | "TURMA" | "ALUNO" | "ESCOLA">("");
  const [turmaId, setTurmaId] = useState("");
  const [alunoId, setAlunoId] = useState("");
  const [alunos, setAlunos] = useState<RankingItemAPI[]>([]);
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  useEffect(() => { rankingMetas().then(setAlunos).catch(() => {}); }, []); // alunos que a pessoa enxerga
  const percentual = TIPOS.find((t) => t.value === tipo)?.unidade === "%";
  const redacoes = materias.filter((m) => m.tipo.startsWith("REDACAO"));
  const precisaMateria = tipo === "MEDIA_MATERIA" || tipo === "DOMINIO_COMPETENCIA";
  const opcoesMateria = tipo === "DOMINIO_COMPETENCIA" ? redacoes : materias;

  const salvar = async () => {
    if (!titulo.trim()) return setErro("Dê um título para a meta.");
    if (!tipo) return setErro("Escolha o que o aluno precisa fazer.");
    if (!(alvo >= 1)) return setErro("Informe a quantidade.");
    if (!pontos) return setErro("Escolha quantos pontos a meta vale.");
    if (!escopo) return setErro("Escolha para quem é a meta.");
    if (tipo === "DOMINIO_COMPETENCIA" && !competencia) return setErro("Escolha a competência.");
    if (escopo === "TURMA" && !turmaId) return setErro("Escolha a turma.");
    if (escopo === "ALUNO" && !alunoId) return setErro("Escolha o aluno.");
    if (precisaMateria && !materiaId) return setErro("Escolha a matéria.");
    setSalvando(true); setErro("");
    try {
      await criarMeta({
        titulo: titulo.trim(), descricao: descricao.trim() || undefined, tipo, alvo, pontos,
        materia_id: materiaId || undefined, competencia: tipo === "DOMINIO_COMPETENCIA" ? competencia : undefined,
        inicio, fim: fim || undefined,
        turma_id: escopo === "TURMA" ? turmaId : undefined, aluno_id: escopo === "ALUNO" ? alunoId : undefined,
      });
      notify("Meta criada. Os alunos já veem em Metas e níveis.");
      onCriada();
    } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível criar a meta."); }
    finally { setSalvando(false); }
  };
  return (
    <Card>
      <SectionTitle title="Nova meta" />
      <div className="form-grid">
        <label>Título<input value={titulo} onChange={(e) => setTitulo(e.target.value)} placeholder="Ex.: Entregar 3 atividades em novembro" /></label>
        <label>Descrição (opcional)<textarea rows={2} value={descricao} onChange={(e) => setDescricao(e.target.value)} /></label>
        <label>O aluno precisa…
          <Escolha value={tipo} onChange={(e) => { setTipo(e.target.value as TipoMetaAPI); setAlvoTxt(""); }}>
            <option value="">Escolha...</option>
            {TIPOS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </Escolha>
        </label>
        <label>{percentual ? "Percentual (X)" : "Quantidade"}
          <input type="number" min={1} max={percentual ? 100 : 1000} value={alvoTxt} placeholder={percentual ? "Ex.: 80" : "Ex.: 3"} onChange={(e) => setAlvoTxt(e.target.value)} />
        </label>
        {(precisaMateria || tipo === "ENTREGAS" || tipo === "NOTA_ATIVIDADE") && (
          <label>Matéria {precisaMateria ? "" : "(opcional: vazio = todas)"}
            <Escolha value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
              <option value="">{precisaMateria ? "Escolha..." : "Todas"}</option>
              {opcoesMateria.map((m) => <option key={m.id} value={m.id}>{m.nome}</option>)}
            </Escolha>
          </label>
        )}
        {tipo === "DOMINIO_COMPETENCIA" && (
          <label>Competência
            <Escolha value={competencia} onChange={(e) => setCompetencia(e.target.value)}>
              <option value="">Escolha...</option>
              {["C1", "C2", "C3", "C4", "C5"].map((c) => <option key={c}>{c}</option>)}
            </Escolha>
          </label>
        )}
        <label>XP que a meta vale
          <Escolha value={pontosTxt} onChange={(e) => setPontosTxt(e.target.value)}>
            <option value="">Escolha...</option>
            {[10, 20, 30, 50, 100].map((p) => <option key={p} value={p}>{p}</option>)}
          </Escolha>
        </label>
        <label>Começa em<input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} /></label>
        <label>Termina em (opcional)<input type="date" value={fim} onChange={(e) => setFim(e.target.value)} /></label>
        <label>Para quem
          <Escolha value={escopo} onChange={(e) => setEscopo(e.target.value as typeof escopo)}>
            <option value="">Escolha...</option>
            <option value="TURMA">Uma turma</option>
            <option value="ALUNO">Um aluno</option>
            {role === "gestor" && <option value="ESCOLA">A escola toda</option>}
          </Escolha>
        </label>
        {escopo === "TURMA" && (
          <label>Turma
            <Escolha value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
              <option value="">Escolha...</option>
              {turmas.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
            </Escolha>
          </label>
        )}
        {escopo === "ALUNO" && (
          <label>Aluno
            <Escolha value={alunoId} onChange={(e) => setAlunoId(e.target.value)}>
              <option value="">Escolha...</option>
              {alunos.map((a) => <option key={a.aluno_id} value={a.aluno_id}>{a.nome}</option>)}
            </Escolha>
          </label>
        )}
      </div>
      <p className="tiny muted">A meta só conta o que o aluno fizer a partir da data de início.</p>
      {erro && <p className="error" role="alert">{erro}</p>}
      <div className="form-actions left">
        <Button variant="secondary" onPress={onFechar}>Cancelar</Button>
        <Button onPress={salvar} disabled={salvando}>{salvando ? "Criando..." : "Criar meta"}</Button>
      </div>
    </Card>
  );
}

function Ranking({ role, turmas, notify }: { role: Role; turmas: TurmaAPI[]; notify: (m: string) => void }) {
  const [turmaId, setTurmaId] = useState("");
  const [itens, setItens] = useState<RankingItemAPI[] | null>(null);
  useEffect(() => {
    rankingMetas(turmaId || undefined).then(setItens).catch(() => notify("Não foi possível carregar o ranking."));
  }, [turmaId]);
  return (
    <Card>
      <SectionTitle title="Ranking de XP" />
      <p className="tiny muted">Só você e a equipe veem este ranking. Ele conta XP (metas, envios e exercícios), nunca notas.</p>
      <label>Turma
        <Escolha value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
          <option value="">{role === "gestor" ? "Escola toda" : "Todas as minhas turmas"}</option>
          {turmas.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
        </Escolha>
      </label>
      {itens === null ? <p className="muted">Carregando...</p> : !itens.length ? <p className="muted">Nenhum aluno por aqui.</p> : (
        <table className="tabela-ranking">
          <thead><tr><th>#</th><th>Aluno</th><th>Nível</th><th>XP</th><th>Metas</th></tr></thead>
          <tbody>
            {itens.map((a, i) => (
              <tr key={a.aluno_id}><td>{i + 1}</td><td>{a.nome}</td><td>{a.nivel} · {a.nome_nivel}</td><td>{a.pontos}</td><td>{a.metas_concluidas}</td></tr>
            ))}
          </tbody>
        </table>
      )}
    </Card>
  );
}
