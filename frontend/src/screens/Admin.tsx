import { SeletorMultiplo, Escolha } from "../components/Seletor";
import { useEffect, useState } from "react";
import { Building2, Plus, Power, Save } from "lucide-react";
import { Badge, BotaoCriar, Button, Card, Empty, Modal, SectionTitle } from "../components/ui";
import {
  criarEscola,
  ativarUsuario,
  criarUsuario,
  definirVinculos,
  editarEscola,
  editarUsuario,
  listarEscolas,
  listarMaterias,
  listarTurmasMinhas,
  listarUsuarios,
  painelEscola,
  painelPlataforma,
  trocarSenhaUsuario,
  vinculosDoUsuario,
  type MateriaAPI,
  type VinculoTurmaAPI,
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
  const [perfil, setPerfil] = useState<PerfilConta | "">("");
  const [turmas, setTurmas] = useState<TurmaAPI[]>([]);
  const [vinculos, setVinculos] = useState<VinculoTurmaAPI[]>([]);
  const [materias, setMaterias] = useState<MateriaAPI[]>([]);
  const [erro, setErro] = useState("");
  const [minhaSenha, setMinhaSenha] = useState(""); // reautenticacao ao criar gestor
  const [salvando, setSalvando] = useState(false);
  useEffect(() => {
    setVinculos([]);
    listarTurmasMinhas(escolaId)
      .then(setTurmas)
      .catch(() => setTurmas([]));
    if (!escolaId) listarMaterias().then(setMaterias).catch(() => setMaterias([]));
  }, [escolaId]);
  const salvar = async () => {
    if (!nome.trim() || !email.trim() || senha.length < 6 || !perfil) {
      setErro("Preencha nome, email, perfil e uma senha provisória de pelo menos 6 caracteres.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      const novo = await criarUsuario({
        nome: nome.trim(), email: email.trim(), senha, perfil, escola_id: escolaId,
        turmas: perfil === "GESTOR" || !vinculos.length ? undefined : vinculos,
      }, perfil === "GESTOR" ? minhaSenha : undefined);
      notify(`${novo.nome} cadastrado(a) como ${ROTULO[perfil].toLowerCase()}${vinculos.length && perfil !== "GESTOR" ? ` em ${vinculos.length} turma(s)` : ""}.`);
      setVinculos([]);
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
          <Escolha value={perfil} onChange={(e) => setPerfil(e.target.value as PerfilConta)}>
            <option value="">Escolha o perfil</option>
            {perfis.map((p) => (
              <option key={p} value={p}>
                {ROTULO[p]}
              </option>
            ))}
          </Escolha>
        </label>
        {perfil === "GESTOR" && (
          <label>
            Confirme a sua senha
            <input type="password" autoComplete="current-password" value={minhaSenha} onChange={(e) => setMinhaSenha(e.target.value)} />
          </label>
        )}
      </div>
      {perfil && perfil !== "GESTOR" && (
        <TurmasEMaterias perfil={perfil} turmas={turmas} materias={materias} valor={vinculos} onChange={setVinculos} />
      )}
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

// Escolhe as turmas da pessoa; no professor, tambem a materia que ele leciona em CADA turma
function TurmasEMaterias({
  perfil, turmas, materias, valor, onChange,
}: {
  perfil: PerfilConta; turmas: TurmaAPI[]; materias: MateriaAPI[];
  valor: VinculoTurmaAPI[]; onChange: (v: VinculoTurmaAPI[]) => void;
}) {
  const da = (id: string) => valor.find((v) => v.turma_id === id);
  if (!turmas.length) return <p className="muted">Nenhuma turma cadastrada ainda.</p>;
  return (
    <div>
      <p className="tiny muted">
        {perfil === "PROFESSOR" ? "Turmas e, em cada uma, as matérias que ele leciona" : "Turmas do aluno"}
      </p>
      <SeletorMultiplo rotulo="Turmas" placeholder="Escolha as turmas"
        opcoes={turmas.map((t) => ({ valor: t.id, rotulo: `${t.nome} (${t.ano})` }))}
        valores={valor.map((v) => v.turma_id)}
        onChange={(ids) => onChange(ids.map((id) => da(id) ?? { turma_id: id, materia_ids: [] }))} />
      {perfil === "PROFESSOR" && valor.map((v) => {
        const t = turmas.find((x) => x.id === v.turma_id);
        return (
          <div key={v.turma_id}>
            <p className="rotulo-escolha">Matérias em {t?.nome}</p>
            {materias.length ? (
              <SeletorMultiplo rotulo={`Matérias em ${t?.nome}`} placeholder="Escolha as matérias"
                opcoes={materias.map((m) => ({ valor: m.id, rotulo: m.nome }))} valores={v.materia_ids}
                onChange={(ids) => onChange(valor.map((x) => x.turma_id === v.turma_id ? { ...x, materia_ids: ids } : x))} />
            ) : <span className="tiny muted">Nenhuma matéria cadastrada.</span>}
          </div>
        );
      })}
    </div>
  );
}

// Editar: dados, senha, turmas/materias e desativar. Gestor mexe em aluno e professor; conta de gestor so o admin.
function EditarConta({
  conta, podeVinculos, onMudou, notify,
}: { conta: UsuarioAtual; podeVinculos: boolean; onMudou: () => void; notify: (s: string) => void }) {
  const [nome, setNome] = useState(conta.nome);
  const [email, setEmail] = useState(conta.email);
  const [novaSenha, setNovaSenha] = useState("");
  const [minhaSenha, setMinhaSenha] = useState("");
  const [erro, setErro] = useState("");
  const [turmas, setTurmas] = useState<TurmaAPI[]>([]);
  const [materias, setMaterias] = useState<MateriaAPI[]>([]);
  const [vinculos, setVinculos] = useState<VinculoTurmaAPI[] | null>(null);
  const perfil = conta.perfil as PerfilConta;
  useEffect(() => {
    if (!podeVinculos || perfil === "GESTOR") return;
    listarTurmasMinhas().then(setTurmas).catch(() => {});
    listarMaterias().then(setMaterias).catch(() => {});
    vinculosDoUsuario(conta.id).then((r) => setVinculos(r.turmas)).catch(() => setVinculos([]));
  }, [conta.id, podeVinculos, perfil]);
  const rodar = async (fn: () => Promise<unknown>, ok: string) => {
    setErro("");
    try {
      await fn();
      notify(ok);
      onMudou();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível salvar.");
    }
  };
  const ativa = conta.ativo !== false;
  return (
    <div className="student-domain">
      <div className="form-grid">
        <label>Nome<input value={nome} onChange={(e) => setNome(e.target.value)} /></label>
        <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
      </div>
      <Button variant="secondary" onPress={() => rodar(() => editarUsuario(conta.id, nome.trim(), email.trim()), "Dados salvos.")}>
        Salvar dados
      </Button>
      <div className="form-grid">
        <label>Nova senha (mín. 6)<input type="password" autoComplete="new-password" value={novaSenha} onChange={(e) => setNovaSenha(e.target.value)} /></label>
        <label>Sua senha (para confirmar)<input type="password" autoComplete="current-password" value={minhaSenha} onChange={(e) => setMinhaSenha(e.target.value)} /></label>
      </div>
      <Button variant="secondary" disabled={novaSenha.length < 6 || !minhaSenha}
        onPress={() => rodar(async () => { await trocarSenhaUsuario(conta.id, novaSenha, minhaSenha); setNovaSenha(""); setMinhaSenha(""); }, "Senha trocada. Passe a senha nova para a pessoa.")}>
        Trocar senha
      </Button>
      {podeVinculos && perfil !== "GESTOR" && vinculos && (
        <>
          <TurmasEMaterias perfil={perfil} turmas={turmas} materias={materias} valor={vinculos} onChange={setVinculos} />
          <Button variant="secondary" onPress={() => rodar(() => definirVinculos(conta.id, vinculos), "Turmas salvas.")}>
            Salvar turmas{perfil === "PROFESSOR" ? " e matérias" : ""}
          </Button>
        </>
      )}
      {erro && <p className="error" role="alert">{erro}</p>}
      <Button variant="secondary" icon={Power}
        onPress={() => {
          if (ativa && !window.confirm(`Desativar ${conta.nome}? A pessoa não consegue mais entrar; o histórico fica.`)) return;
          rodar(() => ativarUsuario(conta.id, !ativa), ativa ? "Conta desativada." : "Conta reativada.");
        }}>
        {ativa ? "Desativar conta" : "Reativar conta"}
      </Button>
    </div>
  );
}

function ListaContas({ escolaId, versao, notify }: { escolaId?: string; versao: number; notify: (s: string) => void }) {
  const [contas, setContas] = useState<UsuarioAtual[] | null>(null);
  const [aberta, setAberta] = useState<string | null>(null);
  const [v, setV] = useState(0);
  useEffect(() => {
    listarUsuarios(escolaId)
      .then(setContas)
      .catch(() => setContas([]));
  }, [escolaId, versao, v]);
  return (
    <Card>
      <SectionTitle title="Contas da instituição" />
      {!contas ? (
        <p className="muted">Carregando...</p>
      ) : !contas.length ? (
        <p className="muted">Nenhuma conta ainda.</p>
      ) : (
        contas.map((c) => {
          const gestorEditando = !escolaId; // sem escolaId = gestor logado; o admin informa a escola
          const editavel = c.perfil !== "ADMIN" && (c.perfil !== "GESTOR" || !gestorEditando);
          return (
            <div key={c.id}>
              <div className="material-row">
                <div className="activity-info">
                  <strong>{c.nome}</strong>
                  <span>
                    {c.email}
                    {c.turmas?.length ? ` · ${c.turmas.join(", ")}` : ""}
                  </span>
                </div>
                {c.ativo === false && <Badge tone="amber">Desativada</Badge>}
                <Badge tone="neutral">{ROTULO[c.perfil as PerfilConta] ?? c.perfil}</Badge>
                {editavel && (
                  <Button variant="secondary" onPress={() => setAberta(aberta === c.id ? null : c.id)}>
                    {aberta === c.id ? "Fechar" : "Editar"}
                  </Button>
                )}
              </div>
              {aberta === c.id && (
                <EditarConta key={c.id + (c.ativo === false)} conta={c} podeVinculos={gestorEditando}
                  onMudou={() => setV((n) => n + 1)} notify={notify} />
              )}
            </div>
          );
        })
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
          <p>Cadastre, edite e desative professores e alunos, e defina as turmas e matérias de cada um.</p>
        </div>
        <BotaoCriar rotulo="Nova conta" titulo="Nova conta">
          {(fechar) => <NovaConta perfis={["PROFESSOR", "ALUNO"]} onCriada={() => { fechar(); setVersao((v) => v + 1); }} notify={notify} />}
        </BotaoCriar>
      </div>
      <ListaContas versao={versao} notify={notify} />
    </>
  );
}

// Admin: instituicoes (criar, editar, desativar) + contas e painel de cada uma
export function Escolas({ notify }: { notify: (s: string) => void }) {
  const [novaAberta, setNovaAberta] = useState(false);
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
      setNovaAberta(false);
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
        <Button icon={Plus} onPress={() => setNovaAberta(true)}>Nova instituição</Button>
      </div>
      {novaAberta && (
      <Modal title="Nova instituição" onClose={() => setNovaAberta(false)}>
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
        <div className="form-actions">
          <Button variant="secondary" onPress={() => setNovaAberta(false)}>Cancelar</Button>
          <Button icon={Plus} onPress={criar}>
            Cadastrar instituição
          </Button>
        </div>
      </Card>
      </Modal>
      )}
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
            <BotaoCriar rotulo="Nova conta" titulo={`Nova conta em ${escola.nome}`}>
              {(fechar) => (
                <NovaConta
                  perfis={["GESTOR", "PROFESSOR", "ALUNO"]}
                  escolaId={escola.id}
                  onCriada={() => { fechar(); setVersao((v) => v + 1); }}
                  notify={notify}
                />
              )}
            </BotaoCriar>
          )}
          <ListaContas escolaId={escola.id} versao={versao} notify={notify} />
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
