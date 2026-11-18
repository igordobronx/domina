import { useEffect, useState } from "react";
import { BookOpen, Check, Plus, Users } from "lucide-react";
import type { DemoState, Role } from "../types";
import { Badge, Button, Card, Empty, Progress, SectionTitle } from "../components/ui";
import {
  criarTurma,
  criarUsuario,
  definirMateriasDoProfessor,
  dominioDoAluno,
  evolucaoDoAluno,
  materiasDosProfessores,
  type EvolucaoMateriaAPI,
  baixarDocumento,
  enviarDocumento,
  excluirDocumento,
  listarDocumentos,
  listarMaterias,
  listarTurmasMinhas,
  listarUsuarios,
  matricular,
  membrosTurma,
  type DocumentoAPI,
  type DominioAPI,
  type MateriaAPI,
  type MembroTurmaAPI,
  type TurmaAPI,
  type UsuarioAtual,
} from "../services/api";

export function Classes({
  state,
  role,
  currentUser,
  notify,
}: {
  state: DemoState;
  role: Role;
  currentUser?: UsuarioAtual | null;
  notify: (s: string) => void;
}) {
  const gestor = role === "gestor";
  const real = !!currentUser && (role === "gestor" || role === "professor");
  const [turmas, setTurmas] = useState<TurmaAPI[] | null>(null);
  const [loading, setLoading] = useState(real);
  const [criando, setCriando] = useState(false);
  const [nome, setNome] = useState("");
  const [ano, setAno] = useState(new Date().getFullYear());
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  const recarregar = () => {
    if (!real) return;
    setLoading(true);
    listarTurmasMinhas()
      .then(setTurmas)
      .catch(() => notify("Não foi possível carregar as turmas."))
      .finally(() => setLoading(false));
  };
  useEffect(recarregar, [real, currentUser?.id]);

  if (!real)
    return (
      <Empty
        title="Entre com uma conta de professor ou gestor"
        text="A gestão de turmas é exclusiva desses perfis."
      />
    );

  const criarTurmaForm = async () => {
    if (!nome.trim()) {
      setErro("Informe o nome da turma.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      await criarTurma({ nome: nome.trim(), ano });
      setNome("");
      setCriando(false);
      recarregar();
      notify("Turma criada.");
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível criar a turma.");
    } finally {
      setSalvando(false);
    }
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">APRENDER JUNTOS</div>
          <h1>{gestor ? "Turmas da escola" : "Minhas turmas"}</h1>
          <p>Uma visão próxima de cada jornada de aprendizagem.</p>
        </div>
        {gestor && (
          <Button icon={Plus} onPress={() => setCriando(!criando)}>
            {criando ? "Fechar" : "Nova turma"}
          </Button>
        )}
      </div>
      {criando && (
        <Card>
          <SectionTitle title="Nova turma" />
          <div className="form-grid">
            <label>
              Nome
              <input
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Ex.: 3º Ano B"
              />
            </label>
            <label>
              Ano
              <input
                type="number"
                value={ano}
                onChange={(e) => setAno(Number(e.target.value))}
              />
            </label>
          </div>
          {erro && (
            <p className="error" role="alert">
              {erro}
            </p>
          )}
          <Button disabled={salvando} onPress={criarTurmaForm}>
            {salvando ? "Criando..." : "Criar turma"}
          </Button>
        </Card>
      )}
      {loading ? (
        <Empty title="Carregando..." text="Buscando turmas no servidor." />
      ) : !turmas?.length ? (
        <Empty
          title="Nenhuma turma ainda"
          text={gestor ? "Crie a primeira turma da escola." : "Nenhuma turma vinculada a você."}
        />
      ) : (
        turmas.map((t) => (
          <TurmaCard key={t.id} turma={t} gestor={gestor} notify={notify} />
        ))
      )}
    </>
  );
}

function TurmaCard({
  turma,
  gestor,
  notify,
}: {
  turma: TurmaAPI;
  gestor: boolean;
  notify: (s: string) => void;
}) {
  const [aberta, setAberta] = useState(false);
  const [membros, setMembros] = useState<MembroTurmaAPI[] | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [adicionando, setAdicionando] = useState(false);
  const [materias, setMaterias] = useState<MateriaAPI[]>([]);
  const [vinculos, setVinculos] = useState<{ professor_id: string; materia_id: string }[]>([]);

  const recarregarMembros = () => {
    setCarregando(true);
    listarMaterias().then(setMaterias).catch(() => {});
    materiasDosProfessores(turma.id).then(setVinculos).catch(() => {});
    membrosTurma(turma.id)
      .then(setMembros)
      .catch(() => notify("Não foi possível carregar os alunos da turma."))
      .finally(() => setCarregando(false));
  };

  const alunos = membros?.filter((m) => m.papel === "ALUNO") ?? [];

  return (
    <Card>
      <div className="class-summary">
        <span className="class-icon">
          <Users size={30} />
        </span>
        <div>
          <h2>{turma.nome}</h2>
          <p>{turma.ano}</p>
        </div>
        {membros && <Badge tone="neutral">{alunos.length} aluno(s)</Badge>}
      </div>
      <Button
        variant="secondary"
        onPress={() => {
          setAberta(!aberta);
          if (!aberta && !membros) recarregarMembros();
        }}
      >
        {aberta ? "Ocultar alunos" : "Ver alunos da turma"}
      </Button>
      {aberta && (
        <>
          {carregando ? (
            <p className="muted">Carregando...</p>
          ) : (
            (membros ?? []).map((m) =>
              m.papel === "ALUNO" ? (
                <AlunoRow key={m.id} aluno={m} notify={notify} />
              ) : (
                <div className="student-table" key={m.id}>
                  <div className="avatar">
                    {m.nome
                      .split(" ")
                      .map((n) => n[0])
                      .slice(0, 2)
                      .join("")
                      .toUpperCase()}
                  </div>
                  <div>
                    <strong>{m.nome}</strong>
                    <p className="muted">{m.email}</p>
                  </div>
                  <Badge tone="neutral">Professor(a)</Badge>
                  {gestor ? (
                    <MateriasDoProfessor
                      turmaId={turma.id} professorId={m.id} materias={materias}
                      escolhidas={vinculos.filter((v) => v.professor_id === m.id).map((v) => v.materia_id)}
                      onSalvo={(ids) => setVinculos((vs) => [...vs.filter((v) => v.professor_id !== m.id),
                        ...ids.map((id) => ({ professor_id: m.id, materia_id: id }))])}
                      notify={notify}
                    />
                  ) : (
                    <span className="tiny muted">
                      {vinculos.length
                        ? `Você leciona: ${materias.filter((x) => vinculos.some((v) => v.materia_id === x.id)).map((x) => x.nome).join(", ")}`
                        : "Você ainda não tem matérias nesta turma. Peça ao gestor para definir."}
                    </span>
                  )}
                </div>
              ),
            )
          )}
          {!adicionando && (
            <Button variant="secondary" icon={Plus} onPress={() => setAdicionando(true)}>
              Adicionar à turma
            </Button>
          )}
          {adicionando && (
            <AdicionarMembro
              turmaId={turma.id}
              soAluno={!gestor}
              jaMatriculados={new Set((membros ?? []).map((m) => m.id))}
              onDone={() => {
                setAdicionando(false);
                recarregarMembros();
              }}
              onCancel={() => setAdicionando(false)}
              notify={notify}
            />
          )}
        </>
      )}
    </Card>
  );
}

// gestor: marca as materias que o professor leciona nesta turma
function MateriasDoProfessor({
  turmaId, professorId, materias, escolhidas, onSalvo, notify,
}: {
  turmaId: string; professorId: string; materias: MateriaAPI[]; escolhidas: string[];
  onSalvo: (ids: string[]) => void; notify: (s: string) => void;
}) {
  const [aberto, setAberto] = useState(false);
  const [marcadas, setMarcadas] = useState<string[]>(escolhidas);
  const [salvando, setSalvando] = useState(false);
  const alterna = (id: string) => setMarcadas((m) => (m.includes(id) ? m.filter((x) => x !== id) : [...m, id]));
  const salvar = async () => {
    setSalvando(true);
    try {
      await definirMateriasDoProfessor(turmaId, professorId, marcadas);
      onSalvo(marcadas);
      setAberto(false);
      notify("Matérias do professor salvas.");
    } catch (e) {
      notify(e instanceof Error ? e.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  };
  if (!aberto)
    return (
      <Button variant="secondary" onPress={() => { setMarcadas(escolhidas); setAberto(true); }}>
        {escolhidas.length ? `Matérias: ${materias.filter((m) => escolhidas.includes(m.id)).map((m) => m.nome).join(", ")}` : "Definir matérias"}
      </Button>
    );
  return (
    <div className="botoes-escolha" role="group" aria-label="Matérias que o professor leciona nesta turma">
      {materias.map((m) => (
        <button key={m.id} aria-pressed={marcadas.includes(m.id)} className={marcadas.includes(m.id) ? "active" : ""}
          onClick={() => alterna(m.id)}>
          {m.nome}
        </button>
      ))}
      <Button disabled={salvando} onPress={salvar}>{salvando ? "Salvando..." : "Salvar"}</Button>
      <Button variant="secondary" onPress={() => setAberto(false)}>Cancelar</Button>
    </div>
  );
}

function AlunoRow({ aluno, notify }: { aluno: MembroTurmaAPI; notify: (s: string) => void }) {
  const [aberto, setAberto] = useState(false);
  const [dominio, setDominio] = useState<DominioAPI[] | null>(null);
  const [evolucao, setEvolucao] = useState<EvolucaoMateriaAPI[]>([]);
  const [carregando, setCarregando] = useState(false);

  const abrir = () => {
    const vaiAbrir = !aberto;
    setAberto(vaiAbrir);
    if (vaiAbrir && !dominio) {
      setCarregando(true);
      evolucaoDoAluno(aluno.id).then(setEvolucao).catch(() => {});
      dominioDoAluno(aluno.id)
        .then(setDominio)
        .catch(() => notify("Não foi possível carregar o domínio deste aluno."))
        .finally(() => setCarregando(false));
    }
  };

  return (
    <div className="student-table-expandable">
      <button className="student-table student-table-button" onClick={abrir} aria-expanded={aberto}>
        <div className="avatar">
          {aluno.nome
            .split(" ")
            .map((n) => n[0])
            .slice(0, 2)
            .join("")
            .toUpperCase()}
        </div>
        <div>
          <strong>{aluno.nome}</strong>
          <p className="muted">{aluno.email}</p>
        </div>
        <Badge tone="neutral">{aberto ? "Ocultar domínio" : "Ver domínio"}</Badge>
      </button>
      {aberto && (
        <div className="student-domain">
          {carregando ? (
            <p className="muted">Carregando...</p>
          ) : !dominio?.length && !evolucao.length ? (
            <p className="muted">Ainda sem correções aprovadas nas matérias que você leciona para este aluno.</p>
          ) : (
            <>
              {evolucao.map((e) => (
                <div key={e.materia_id}>
                  <p className="tiny">
                    <strong>{e.materia}</strong> · média {Math.round(e.media_percentual)}% · {e.num_atividades} atividade(s)
                  </p>
                  <Progress value={e.media_percentual} label={e.materia} />
                </div>
              ))}
              {(dominio ?? []).map((d) => (
                <div key={d.tema_id}>
                  <p className="tiny">
                    <strong>{d.materia} · {d.habilidade_codigo}</strong> · {d.tema} · {Math.round(d.percentual_dominio)}%
                  </p>
                  <Progress value={d.percentual_dominio} label={d.tema} />
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

function AdicionarMembro({
  turmaId,
  soAluno,
  jaMatriculados,
  onDone,
  onCancel,
  notify,
}: {
  turmaId: string;
  soAluno: boolean; // professor so cadastra e matricula alunos
  jaMatriculados: Set<string>;
  onDone: () => void;
  onCancel: () => void;
  notify: (s: string) => void;
}) {
  const [modo, setModo] = useState<"existente" | "novo">("existente");
  const [candidatos, setCandidatos] = useState<UsuarioAtual[] | null>(null);
  const [usuarioId, setUsuarioId] = useState("");
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState<"ALUNO" | "PROFESSOR">("ALUNO");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    listarUsuarios()
      .then((todos) =>
        setCandidatos(
          todos.filter(
            (u) =>
              (u.perfil === "ALUNO" || (!soAluno && u.perfil === "PROFESSOR")) && !jaMatriculados.has(u.id),
          ),
        ),
      )
      .catch(() => notify("Não foi possível carregar os usuários da escola."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const adicionarExistente = async () => {
    const escolhido = candidatos?.find((u) => u.id === usuarioId);
    if (!escolhido) {
      setErro("Selecione um usuário.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      await matricular(turmaId, {
        usuario_id: escolhido.id,
        papel: escolhido.perfil as "ALUNO" | "PROFESSOR",
      });
      notify(`${escolhido.nome} matriculado(a).`);
      onDone();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível matricular.");
    } finally {
      setSalvando(false);
    }
  };

  const cadastrarEMatricular = async () => {
    if (!nome.trim() || !email.trim() || senha.length < 6) {
      setErro("Preencha nome, email e uma senha com 6+ caracteres.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      const novo = await criarUsuario({ nome: nome.trim(), email: email.trim(), senha, perfil });
      await matricular(turmaId, { usuario_id: novo.id, papel: perfil });
      notify(`${novo.nome} cadastrado(a) e matriculado(a).`);
      onDone();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível cadastrar.");
    } finally {
      setSalvando(false);
    }
  };

  return (
    <Card>
      <div className="tabs input-tabs">
        {(["existente", "novo"] as const).map((m) => (
          <button
            key={m}
            aria-pressed={modo === m}
            className={modo === m ? "active" : ""}
            onClick={() => setModo(m)}
          >
            {m === "existente" ? "Usuário já cadastrado" : "Cadastrar novo"}
          </button>
        ))}
      </div>
      {modo === "existente" ? (
        <div className="form-grid">
          <label>
            Usuário
            <select value={usuarioId} onChange={(e) => setUsuarioId(e.target.value)}>
              <option value="">Selecione...</option>
              {(candidatos ?? []).map((u) => (
                <option key={u.id} value={u.id}>
                  {u.nome} ({u.perfil === "PROFESSOR" ? "Professor(a)" : "Aluno(a)"})
                </option>
              ))}
            </select>
          </label>
        </div>
      ) : (
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
          {!soAluno && (
          <label>
            Perfil
            <select value={perfil} onChange={(e) => setPerfil(e.target.value as "ALUNO" | "PROFESSOR")}>
              <option value="ALUNO">Aluno(a)</option>
              <option value="PROFESSOR">Professor(a)</option>
            </select>
          </label>
          )}
        </div>
      )}
      {erro && (
        <p className="error" role="alert">
          {erro}
        </p>
      )}
      <div className="form-actions">
        <Button variant="secondary" onPress={onCancel}>
          Cancelar
        </Button>
        <Button
          disabled={salvando}
          onPress={modo === "existente" ? adicionarExistente : cadastrarEMatricular}
        >
          {salvando ? "Salvando..." : "Adicionar à turma"}
        </Button>
      </div>
    </Card>
  );
}
const EXT_DOCUMENTO = /\.(pdf|docx|txt|png|jpe?g|webp)$/i;
const TIPOS_DOCUMENTO: { value: DocumentoAPI["tipo"]; label: string }[] = [
  { value: "APOSTILA", label: "Apostila" },
  { value: "RUBRICA", label: "Rubrica de correção" },
  { value: "GABARITO", label: "Gabarito" },
  { value: "PLANO_DE_AULA", label: "Plano de aula" },
];

export function Materials({
  state,
  update,
  notify,
  role,
  currentUser,
}: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  notify: (s: string) => void;
  role: Role;
  currentUser?: UsuarioAtual | null;
}) {
  const real = !!currentUser && (role === "professor" || role === "gestor");
  const [adding, setAdding] = useState(false),
    [name, setName] = useState(""),
    [subject, setSubject] = useState("Redação ENEM"),
    [file, setFile] = useState<File | null>(null),
    [error, setError] = useState("");

  // modo real: materia/documentos vem do backend (por matéria, ja que /materias/{id}/documentos
  // so lista os de uma materia por vez -- juntamos todas as materias da escola aqui)
  const [materias, setMaterias] = useState<MateriaAPI[] | null>(null);
  const [documentos, setDocumentos] = useState<DocumentoAPI[] | null>(null);
  const [filtro, setFiltro] = useState(""); // matéria escolhida no filtro da lista (vazio = todas)
  const [materiaId, setMateriaId] = useState("");
  const [tipo, setTipo] = useState<DocumentoAPI["tipo"]>("APOSTILA");
  const [carregando, setCarregando] = useState(real);
  const [salvando, setSalvando] = useState(false);

  const recarregar = () => {
    if (!real) return;
    setCarregando(true);
    listarMaterias()
      .then((ms) => {
        setMaterias(ms);
        return listarDocumentos();
      })
      .then(setDocumentos)
      .catch(() => notify("Não foi possível carregar os materiais."))
      .finally(() => setCarregando(false));
  };
  useEffect(recarregar, [real, currentUser?.id]);

  const add = async () => {
    if (!file) {
      setError("Selecione o documento.");
      return;
    }
    if (real) {
      if (!materiaId) {
        setError("Escolha a matéria do material.");
        return;
      }
      setSalvando(true);
      setError("");
      try {
        await enviarDocumento(materiaId, file, tipo);
        setAdding(false);
        setFile(null);
        notify("Material enviado para a escola.");
        recarregar();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Não foi possível enviar o material.");
      } finally {
        setSalvando(false);
      }
      return;
    }
    if (!name.trim()) {
      setError("Informe um título e selecione o documento.");
      return;
    }
    update((s) => ({
      ...s,
      materials: [
        ...s.materials,
        {
          id: crypto.randomUUID(),
          name: name.trim(),
          subject,
          approved: false,
          fileName: file.name,
        },
      ],
    }));
    setAdding(false);
    setName("");
    setFile(null);
    setError("");
    notify(
      "Material adicionado à demonstração. Nenhum arquivo foi enviado ao servidor.",
    );
  };
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">A BASE DE UM BOM APRENDIZADO</div>
          <h1>Materiais e critérios</h1>
          <p>O conteúdo da escola orienta cada correção.</p>
        </div>
        <Button icon={Plus} onPress={() => setAdding(!adding)}>
          {adding ? "Fechar formulário" : "Adicionar material"}
        </Button>
      </div>
      {adding && (
        <Card>
          <SectionTitle title="Novo material" />
          <div className="form-grid">
            {real ? (
              <>
                <label>
                  Matéria
                  <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
                    <option value="">Escolha a matéria…</option>
                    {(materias ?? []).map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.nome}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Tipo
                  <select value={tipo} onChange={(e) => setTipo(e.target.value as DocumentoAPI["tipo"])}>
                    {TIPOS_DOCUMENTO.map((t) => (
                      <option key={t.value} value={t.value}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            ) : (
              <>
                <label>
                  Título
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Ex.: Rubrica de argumentação"
                  />
                </label>
                <label>
                  Matéria
                  <select
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                  >
                    <option>Redação ENEM</option>
                    <option>Matemática</option>
                  </select>
                </label>
              </>
            )}
            <label>
              Documento (até {real ? "20" : "10"} MB)
              <input
                type="file"
                accept={real ? ".pdf,.docx,.txt,.png,.jpg,.jpeg,.webp" : ".pdf,.docx,.txt"}
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  const limite = real ? 20 * 1024 * 1024 : 10 * 1024 * 1024;
                  if (f && (f.size > limite || (!real && !/\.(pdf|docx|txt)$/i.test(f.name)) || (real && !EXT_DOCUMENTO.test(f.name)))) {
                    setFile(null);
                    setError(real ? "Envie PDF, DOCX, TXT ou imagem, com até 20 MB." : "Escolha PDF, DOCX ou TXT com até 10 MB.");
                    e.target.value = "";
                  } else {
                    setFile(f || null);
                    setError("");
                  }
                }}
              />
            </label>
          </div>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <Button disabled={salvando} onPress={add}>
            {salvando ? "Enviando..." : real ? "Enviar material" : "Salvar material demonstrativo"}
          </Button>
        </Card>
      )}
      {real ? (
        <>
          <div className="botoes-escolha" role="group" aria-label="Filtrar por matéria">
            <button aria-pressed={filtro === ""} className={filtro === "" ? "active" : ""} onClick={() => setFiltro("")}>
              Todas
            </button>
            {(materias ?? []).map((m) => (
              <button key={m.id} aria-pressed={filtro === m.id} className={filtro === m.id ? "active" : ""}
                onClick={() => setFiltro(m.id)}>
                {m.nome}
              </button>
            ))}
          </div>
          {carregando ? (
            <Card><p className="muted">Carregando...</p></Card>
          ) : (
            (materias ?? []).filter((m) => !filtro || m.id === filtro).map((m) => {
              const docs = (documentos ?? []).filter((d) => d.materia_id === m.id);
              return (
                <Card key={m.id}>
                  <SectionTitle title={`${m.nome} · ${docs.length} ${docs.length === 1 ? "material" : "materiais"}`} />
                  {!docs.length ? (
                    <p className="muted">Nenhum material enviado para esta matéria.</p>
                  ) : (
                    docs.map((d) => (
                      <div className="material-row" key={d.id}>
                        <div className="activity-icon">
                          <BookOpen size={21} />
                        </div>
                        <div className="activity-info">
                          <strong>{d.nome_arquivo}</strong>
                          <span>
                            {TIPOS_DOCUMENTO.find((t) => t.value === d.tipo)?.label ?? d.tipo} · {d.enviado_por_nome} ·{" "}
                            {new Date(d.criado_em).toLocaleDateString("pt-BR")}
                            {d.tamanho_bytes ? ` · ${(d.tamanho_bytes / 1024 / 1024).toFixed(1)} MB` : ""}
                          </span>
                        </div>
                        <Badge tone={d.status_processamento === "PROCESSADO" ? "green" : "amber"}>
                          {d.status_processamento === "PROCESSADO" ? "Base aprovada" : "Aguardando integração"}
                        </Badge>
                        {d.pode_baixar && (
                          <Button variant="secondary" onPress={() => baixarDocumento(d.id, d.nome_arquivo).catch((e) => notify(e instanceof Error ? e.message : "Não foi possível baixar."))}>
                            Baixar
                          </Button>
                        )}
                        <Button variant="secondary" onPress={async () => {
                          if (!window.confirm(`Excluir "${d.nome_arquivo}"?`)) return;
                          try { await excluirDocumento(d.id); notify("Material excluído."); recarregar(); }
                          catch (e) { notify(e instanceof Error ? e.message : "Não foi possível excluir."); }
                        }}>
                          Excluir
                        </Button>
                      </div>
                    ))
                  )}
                </Card>
              );
            })
          )}
        </>
      ) : (
        <Card>
          {state.materials.map((m) => (
            <div className="material-row" key={m.id}>
              <div className="activity-icon">
                <BookOpen size={21} />
              </div>
              <div className="activity-info">
                <strong>{m.name}</strong>
                <span>
                  {m.subject} · {m.fileName}
                </span>
              </div>
              <Badge tone={m.approved ? "green" : "amber"}>
                {m.approved ? "Base aprovada" : "Aguardando integração"}
              </Badge>
            </div>
          ))}
        </Card>
      )}
      <div className="info-banner">
        <Check size={22} />
        <p>
          {real
            ? "A extração de temas ainda depende do processamento do conteúdo (P2/P3); os arquivos já ficam salvos na escola."
            : "A extração de temas e a aprovação de critérios dependem do processamento real. Os materiais adicionados aqui ficam como registros locais; não entram nas correções."}
        </p>
      </div>
    </>
  );
}
