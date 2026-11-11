import { useEffect, useState } from "react";
import { Building2, Plus, Power, Save } from "lucide-react";
import { Badge, Button, Card, Empty, SectionTitle } from "../components/ui";
import {
  criarEscola,
  criarUsuario,
  editarEscola,
  listarEscolas,
  listarTurmasMinhas,
  listarUsuarios,
  painelEscola,
  painelPlataforma,
  type EscolaAPI,
  type ResumoEscolaAPI,
  type ResumoPlataformaAPI,
  type TurmaAPI,
  type UsuarioAtual,
} from "../services/api";

const brl = (n: number) => n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const num = (n: number) => Math.round(n).toLocaleString("pt-BR");
const mb = (b: number) =>
  `${(b / 1024 / 1024).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} MB`;
const mesAtual = () => new Date().toISOString().slice(0, 7);
const ROTULO = { GESTOR: "Gestor(a)", PROFESSOR: "Professor(a)", ALUNO: "Aluno(a)" } as const;
type PerfilConta = keyof typeof ROTULO;

function Tile({ valor, rotulo }: { valor: string; rotulo: string }) {
  return (
    <div>
      <strong>{valor}</strong>
      <p className="muted">{rotulo}</p>
    </div>
  );
}

function SeletorMes({ mes, onChange }: { mes: string; onChange: (m: string) => void }) {
  return (
    <label>
      Mês
      <input type="month" value={mes} max={mesAtual()} onChange={(e) => e.target.value && onChange(e.target.value)} />
    </label>
  );
}

function BlocosResumo({ r }: { r: ResumoEscolaAPI }) {
  return (
    <>
      <Card>
        <SectionTitle title="Resumo financeiro" />
        <div className="form-grid">
          <Tile valor={brl(r.receita)} rotulo="receita do mês (plano fixo + alunos ativos)" />
          <Tile valor={brl(r.custo_ia)} rotulo="custo estimado de IA e OCR" />
          <Tile valor={brl(r.margem)} rotulo="margem" />
        </div>
      </Card>
      <Card>
        <SectionTitle title="Consumo no mês" />
        <div className="form-grid">
          <Tile valor={num(r.alunos_ativos)} rotulo={`alunos ativos (de ${num(r.alunos_cadastrados)} cadastrados)`} />
          <Tile valor={num(r.submissoes)} rotulo="envios dos alunos" />
          <Tile valor={num(r.execucoes_agente)} rotulo="execuções do agente" />
          <Tile valor={num(r.tokens_llm)} rotulo="tokens de correção" />
          <Tile valor={num(r.chamadas_ocr)} rotulo="leituras de foto (OCR)" />
          <Tile valor={mb(r.armazenamento_bytes)} rotulo="armazenamento (fotos e materiais)" />
          <Tile valor={num(r.professores)} rotulo="professores" />
          <Tile valor={num(r.turmas)} rotulo="turmas" />
        </div>
      </Card>
    </>
  );
}

// Gestor: sem escolaId (o servidor usa a escola dele). Admin: escolaId da escola escolhida.
export function PainelEscola({ escolaId, notify }: { escolaId?: string; notify: (s: string) => void }) {
  const [mes, setMes] = useState(mesAtual());
  const [resumo, setResumo] = useState<ResumoEscolaAPI | null>(null);
  useEffect(() => {
    setResumo(null);
    painelEscola(mes, escolaId)
      .then(setResumo)
      .catch((e) => notify(e instanceof Error ? e.message : "Não foi possível carregar o painel."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes, escolaId]);
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">INSTITUIÇÃO</div>
          <h1>{resumo?.escola_nome ?? "Painel da escola"}</h1>
          <p>Resumo financeiro e consumo de IA e armazenamento.</p>
        </div>
        <SeletorMes mes={mes} onChange={setMes} />
      </div>
      {!resumo ? <p className="muted">Carregando...</p> : <BlocosResumo r={resumo} />}
    </>
  );
}

// Admin: visao consolidada da plataforma + cada instituicao
export function PainelPlataforma({ notify, abrirEscola }: { notify: (s: string) => void; abrirEscola: () => void }) {
  const [mes, setMes] = useState(mesAtual());
  const [dados, setDados] = useState<ResumoPlataformaAPI | null>(null);
  useEffect(() => {
    painelPlataforma(mes)
      .then(setDados)
      .catch((e) => notify(e instanceof Error ? e.message : "Não foi possível carregar o painel."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes]);
  const t = dados?.totais;
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">PLATAFORMA DOMINA</div>
          <h1>Visão geral</h1>
          <p>Todas as instituições ativas somadas.</p>
        </div>
        <SeletorMes mes={mes} onChange={setMes} />
      </div>
      {!dados || !t ? (
        <p className="muted">Carregando...</p>
      ) : (
        <>
          <Card>
            <SectionTitle title="Totais" />
            <div className="form-grid">
              <Tile valor={num(dados.escolas_ativas)} rotulo="instituições ativas" />
              <Tile valor={num(t.alunos_ativos)} rotulo="alunos ativos" />
              <Tile valor={brl(t.receita)} rotulo="receita" />
              <Tile valor={brl(t.custo_ia)} rotulo="custo de IA e OCR" />
              <Tile valor={brl(t.margem)} rotulo="margem" />
              <Tile valor={num(t.tokens_llm)} rotulo="tokens de correção" />
              <Tile valor={num(t.chamadas_ocr)} rotulo="leituras de foto (OCR)" />
              <Tile valor={num(t.execucoes_agente)} rotulo="execuções do agente" />
              <Tile valor={mb(t.armazenamento_bytes)} rotulo="armazenamento" />
            </div>
          </Card>
          <Card>
            <SectionTitle title="Por instituição" />
            {!dados.escolas.length ? (
              <Empty title="Nenhuma instituição ativa" text="Cadastre a primeira em Instituições." />
            ) : (
              dados.escolas.map((e) => (
                <div className="material-row" key={e.escola_id}>
                  <div className="activity-info">
                    <strong>{e.escola_nome}</strong>
                    <span>
                      {num(e.alunos_ativos)} alunos ativos · {num(e.tokens_llm)} tokens · {num(e.chamadas_ocr)} OCR ·{" "}
                      {mb(e.armazenamento_bytes)}
                    </span>
                  </div>
                  <Badge tone="neutral">
                    {brl(e.receita)} − {brl(e.custo_ia)} = {brl(e.margem)}
                  </Badge>
                </div>
              ))
            )}
            <Button variant="secondary" icon={Building2} onPress={abrirEscola}>
              Gerenciar instituições
            </Button>
          </Card>
        </>
      )}
    </>
  );
}

// Formulario de nova conta. Admin passa escolaId e pode criar gestor; gestor so professor e aluno.
function NovaConta({
  perfis,
  escolaId,
  onCriada,
  notify,
}: {
  perfis: PerfilConta[];
  escolaId?: string;
  onCriada: () => void;
  notify: (s: string) => void;
}) {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState<PerfilConta>(perfis[0]);
  const [turmas, setTurmas] = useState<TurmaAPI[]>([]);
  const [turmaId, setTurmaId] = useState("");
  const [erro, setErro] = useState("");
  const [minhaSenha, setMinhaSenha] = useState(""); // reautenticacao ao criar gestor
  const [salvando, setSalvando] = useState(false);
  useEffect(() => {
    setTurmaId("");
    listarTurmasMinhas(escolaId)
      .then(setTurmas)
      .catch(() => setTurmas([]));
  }, [escolaId]);
  const salvar = async () => {
    if (!nome.trim() || !email.trim() || senha.length < 6) {
      setErro("Preencha nome, email e uma senha provisória de pelo menos 6 caracteres.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      const novo = await criarUsuario({
        nome: nome.trim(), email: email.trim(), senha, perfil, escola_id: escolaId,
        turma_id: perfil === "GESTOR" ? undefined : turmaId || undefined,
      }, perfil === "GESTOR" ? minhaSenha : undefined);
      const turma = turmas.find((t) => t.id === turmaId);
      notify(`${novo.nome} cadastrado(a) como ${ROTULO[perfil].toLowerCase()}${turma && perfil !== "GESTOR" ? ` na turma ${turma.nome}` : ""}.`);
      setNome("");
      setEmail("");
      setSenha("");
      setMinhaSenha("");
      onCriada();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível cadastrar.");
    } finally {
      setSalvando(false);
    }
  };
  return (
    <Card>
      <SectionTitle title="Nova conta" />
      <div className="form-grid">
        <label>
          Nome
          <input value={nome} onChange={(e) => setNome(e.target.value)} />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Senha provisória
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} />
        </label>
        <label>
          Perfil
          <select value={perfil} onChange={(e) => setPerfil(e.target.value as PerfilConta)}>
            {perfis.map((p) => (
              <option key={p} value={p}>
                {ROTULO[p]}
              </option>
            ))}
          </select>
        </label>
        {perfil === "GESTOR" && (
          <label>
            Confirme a sua senha
            <input type="password" autoComplete="current-password" value={minhaSenha} onChange={(e) => setMinhaSenha(e.target.value)} />
          </label>
        )}
        {perfil !== "GESTOR" && (
          <label>
            Turma
            <select value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
              <option value="">Sem turma por enquanto</option>
              {turmas.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.nome} ({t.ano})
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      {erro && (
        <p className="error" role="alert">
          {erro}
        </p>
      )}
      <Button icon={Plus} disabled={salvando} onPress={salvar}>
        {salvando ? "Salvando..." : "Cadastrar"}
      </Button>
    </Card>
  );
}

function ListaContas({ escolaId, versao }: { escolaId?: string; versao: number }) {
  const [contas, setContas] = useState<UsuarioAtual[] | null>(null);
  useEffect(() => {
    listarUsuarios(escolaId)
      .then(setContas)
      .catch(() => setContas([]));
  }, [escolaId, versao]);
  return (
    <Card>
      <SectionTitle title="Contas da instituição" />
      {!contas ? (
        <p className="muted">Carregando...</p>
      ) : !contas.length ? (
        <p className="muted">Nenhuma conta ainda.</p>
      ) : (
        contas.map((c) => (
          <div className="material-row" key={c.id}>
            <div className="activity-info">
              <strong>{c.nome}</strong>
              <span>{c.email}</span>
            </div>
            <Badge tone="neutral">{ROTULO[c.perfil as PerfilConta] ?? c.perfil}</Badge>
          </div>
        ))
      )}
    </Card>
  );
}

// Gestor: cria professor e aluno da propria escola
export function Equipe({ notify }: { notify: (s: string) => void }) {
  const [versao, setVersao] = useState(0);
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">MINHA ESCOLA</div>
          <h1>Equipe e alunos</h1>
          <p>Cadastre professores e alunos da sua instituição.</p>
        </div>
      </div>
      <NovaConta perfis={["PROFESSOR", "ALUNO"]} onCriada={() => setVersao((v) => v + 1)} notify={notify} />
      <ListaContas versao={versao} />
    </>
  );
}

// Admin: instituicoes (criar, editar, desativar) + contas e painel de cada uma
export function Escolas({ notify }: { notify: (s: string) => void }) {
  const [escolas, setEscolas] = useState<EscolaAPI[] | null>(null);
  const [aberta, setAberta] = useState<string | null>(null);
  const [versao, setVersao] = useState(0);
  const [novo, setNovo] = useState({ nome: "", cnpj: "", plano_fixo: "1000", valor_por_aluno: "8" });
  const [erro, setErro] = useState("");
  const recarregar = () =>
    listarEscolas()
      .then(setEscolas)
      .catch(() => notify("Não foi possível carregar as instituições."));
  useEffect(() => {
    recarregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const criar = async () => {
    setErro("");
    try {
      const e = await criarEscola({
        nome: novo.nome.trim(),
        cnpj: novo.cnpj.trim(),
        plano_fixo: Number(novo.plano_fixo),
        valor_por_aluno: Number(novo.valor_por_aluno),
      });
      notify(`${e.nome} cadastrada.`);
      setNovo({ nome: "", cnpj: "", plano_fixo: "1000", valor_por_aluno: "8" });
      setAberta(e.id);
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível cadastrar a instituição.");
    }
  };
  const escola = escolas?.find((e) => e.id === aberta);

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">PLATAFORMA</div>
          <h1>Instituições</h1>
          <p>Cadastre escolas, crie gestores e acompanhe o consumo de cada uma.</p>
        </div>
      </div>
      <Card>
        <SectionTitle title="Nova instituição" />
        <div className="form-grid">
          <label>
            Nome
            <input value={novo.nome} onChange={(e) => setNovo({ ...novo, nome: e.target.value })} />
          </label>
          <label>
            CNPJ
            <input value={novo.cnpj} onChange={(e) => setNovo({ ...novo, cnpj: e.target.value })} />
          </label>
          <label>
            Plano fixo (R$/mês)
            <input type="number" min="0" value={novo.plano_fixo}
              onChange={(e) => setNovo({ ...novo, plano_fixo: e.target.value })} />
          </label>
          <label>
            Valor por aluno ativo (R$)
            <input type="number" min="0" value={novo.valor_por_aluno}
              onChange={(e) => setNovo({ ...novo, valor_por_aluno: e.target.value })} />
          </label>
        </div>
        {erro && (
          <p className="error" role="alert">
            {erro}
          </p>
        )}
        <Button icon={Plus} onPress={criar}>
          Cadastrar instituição
        </Button>
      </Card>
      <Card>
        <SectionTitle title="Instituições" />
        {!escolas ? (
          <p className="muted">Carregando...</p>
        ) : !escolas.length ? (
          <p className="muted">Nenhuma instituição ainda.</p>
        ) : (
          escolas.map((e) => (
            <div className="material-row" key={e.id}>
              <div className="activity-info">
                <strong>{e.nome}</strong>
                <span>
                  {e.cnpj} · {brl(e.plano_fixo)} + {brl(e.valor_por_aluno)}/aluno
                </span>
              </div>
              <Badge tone={e.ativa ? "green" : "neutral"}>{e.ativa ? "Ativa" : "Desativada"}</Badge>
              <Button variant="secondary" onPress={() => setAberta(aberta === e.id ? null : e.id)}>
                {aberta === e.id ? "Fechar" : "Abrir"}
              </Button>
            </div>
          ))
        )}
      </Card>
      {escola && (
        <>
          <EditarEscola
            key={escola.id + escola.ativa}
            escola={escola}
            onSalvo={recarregar}
            notify={notify}
          />
          {escola.ativa && (
            <NovaConta
              perfis={["GESTOR", "PROFESSOR", "ALUNO"]}
              escolaId={escola.id}
              onCriada={() => setVersao((v) => v + 1)}
              notify={notify}
            />
          )}
          <ListaContas escolaId={escola.id} versao={versao} />
          <PainelEscola escolaId={escola.id} notify={notify} />
        </>
      )}
    </>
  );
}

function EditarEscola({
  escola,
  onSalvo,
  notify,
}: {
  escola: EscolaAPI;
  onSalvo: () => void;
  notify: (s: string) => void;
}) {
  const [f, setF] = useState({
    nome: escola.nome,
    plano_fixo: String(escola.plano_fixo),
    valor_por_aluno: String(escola.valor_por_aluno),
  });
  const [minhaSenha, setMinhaSenha] = useState(""); // reautenticacao ao desativar/reativar
  const salvar = (extra: { ativa?: boolean } = {}) =>
    editarEscola(escola.id, {
      nome: f.nome.trim(),
      plano_fixo: Number(f.plano_fixo),
      valor_por_aluno: Number(f.valor_por_aluno),
      ...extra,
    }, extra.ativa === undefined ? undefined : minhaSenha)
      .then(() => {
        notify(extra.ativa === undefined ? "Instituição atualizada." : extra.ativa ? "Instituição reativada." : "Instituição desativada.");
        onSalvo();
      })
      .catch((e) => notify(e instanceof Error ? e.message : "Não foi possível salvar."));
  return (
    <Card>
      <SectionTitle title={`Editar ${escola.nome}`} />
      <div className="form-grid">
        <label>
          Nome
          <input value={f.nome} onChange={(e) => setF({ ...f, nome: e.target.value })} />
        </label>
        <label>
          Plano fixo (R$/mês)
          <input type="number" min="0" value={f.plano_fixo} onChange={(e) => setF({ ...f, plano_fixo: e.target.value })} />
        </label>
        <label>
          Valor por aluno ativo (R$)
          <input type="number" min="0" value={f.valor_por_aluno}
            onChange={(e) => setF({ ...f, valor_por_aluno: e.target.value })} />
        </label>
        <label>
          Sua senha (para desativar ou reativar)
          <input type="password" autoComplete="current-password" value={minhaSenha} onChange={(e) => setMinhaSenha(e.target.value)} />
        </label>
      </div>
      <div className="form-actions left">
        <Button icon={Save} onPress={() => salvar()}>
          Salvar
        </Button>
        <Button variant="ghost" icon={Power} onPress={() => salvar({ ativa: !escola.ativa })}>
          {escola.ativa ? "Desativar instituição" : "Reativar instituição"}
        </Button>
      </div>
    </Card>
  );
}
