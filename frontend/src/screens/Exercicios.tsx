import { Seletor, SeletorMultiplo, Escolha } from "../components/Seletor";
import { Filtros } from "../components/Filtros";
import { useEffect, useState } from "react";
import { Check, ChevronDown, ChevronUp, CircleCheck, MessageSquare, Pencil, Plus, Sparkles, Trash2, X } from "lucide-react";
import { Badge, Button, Card, Empty, Modal, SectionTitle } from "../components/ui";
import { EditorQuestao, LETRAS, MAX_EXEMPLOS, vazio, type Rascunho } from "../components/EditorQuestao";
import {
  avaliarRespostaExercicio, criarExerciciosLote, editarExercicio, excluirExercicio, listarExerciciosProfessor,
  listarMaterias, listarTurmasMinhas, membrosTurma, respostasDoExercicio, resumoExerciciosTurma,
  sugerirExercicios, sugerirRespostaExemplo, type RespostaAlunoAPI, type ResultadoAPI, type ResumoAlunoAPI,
  type ExercicioPayload, type MembroTurmaAPI, type ExercicioProfessorAPI, type MateriaAPI, type SugestaoExercicioAPI,
  type QuestaoExercicioPayload, type TipoExercicioAPI, type TurmaAPI,
} from "../services/api";

// Exercicios de PRATICA do professor (nao valem nota; provas continuam em Atividades).
// O professor escreve o exercicio ou pede rascunhos para a IA; nada chega ao aluno sem ele salvar.
// No aluno, tudo daqui aparece na aba "Do professor" (mesmo se a IA ajudou: so ganha um selo).

const erroDe = (e: unknown, padrao: string) => (e instanceof Error ? e.message : padrao);

export function ExerciciosProfessor({ notify }: { notify: (m: string) => void }) {
  const [lista, setLista] = useState<ExercicioProfessorAPI[] | null>(null);
  const [turmas, setTurmas] = useState<TurmaAPI[]>([]);
  const [materias, setMaterias] = useState<MateriaAPI[]>([]);
  // null = fechado; "novo" = criando; um exercicio = editando
  const [aberto, setAberto] = useState<"novo" | ExercicioProfessorAPI | null>(null);
  const recarregar = () =>
    listarExerciciosProfessor().then(setLista).catch(() => notify("Não foi possível carregar os exercícios."));
  useEffect(() => {
    recarregar();
    listarTurmasMinhas().then(setTurmas).catch(() => {});
    listarMaterias().then(setMaterias).catch(() => {});
  }, []);
  const excluir = async (ex: ExercicioProfessorAPI) => {
    const todas = ex.grupo_id ? " (todas as questões dele)" : "";
    if (!window.confirm(`Excluir o exercício "${ex.titulo}"${todas}? Ele some para os alunos.`)) return;
    try { await excluirExercicio(ex.id); notify("Exercício excluído."); recarregar(); }
    catch (e) { notify(erroDe(e, "Não foi possível excluir.")); }
  };
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Exercícios</h1>
          <p>Crie exercícios de prática para suas turmas, escrevendo você mesmo ou com ajuda da IA. Não valem nota.</p>
        </div>
        <Button icon={Plus} onPress={() => setAberto("novo")}>Novo exercício</Button>
      </div>
      {aberto && (
        <Modal title={aberto === "novo" ? "Novo exercício" : "Editar exercício"} largo onClose={() => setAberto(null)}>
        <FormExercicio
          key={aberto === "novo" ? "novo" : aberto.id}
          inicial={aberto === "novo" ? null : aberto}
          turmas={turmas}
          materias={materias}
          notify={notify}
          onFechar={() => setAberto(null)}
          onSalvo={(fechar) => { if (fechar) setAberto(null); recarregar(); }}
        />
        </Modal>
      )}
      {lista === null ? <Card><p className="muted">Carregando...</p></Card> : (
        <ListaPorTurma lista={lista} turmas={turmas} notify={notify}
          onEditar={(ex) => { setAberto(ex); window.scrollTo(0, 0); }} onExcluir={excluir} />
      )}
    </>
  );
}

function FormExercicio({ inicial, turmas, materias, notify, onFechar, onSalvo }: {
  inicial: ExercicioProfessorAPI | null;
  turmas: TurmaAPI[];
  materias: MateriaAPI[];
  notify: (m: string) => void;
  onFechar: () => void;
  onSalvo: (fechar: boolean) => void;
}) {
  const [titulo, setTitulo] = useState(inicial?.titulo ?? "");
  const [assunto, setAssunto] = useState(inicial?.assunto ?? "");
  const [materiaId, setMateriaId] = useState(inicial?.materia_id ?? "");
  // criando: pode marcar varias turmas (vira um exercicio por turma). Editando: a turma do exercicio
  const [turmaIds, setTurmaIds] = useState<string[]>(inicial ? [inicial.turma_id] : []);
  const turmaId = turmaIds.length === 1 ? turmaIds[0] : "";
  // para quem: a turma toda ou so alguns alunos dela
  const [paraAlguns, setParaAlguns] = useState<boolean | null>(inicial ? !!inicial.aluno_ids?.length : null);
  const [escolhidos, setEscolhidos] = useState<string[]>(inicial?.aluno_ids ?? []);
  // alunos de cada turma marcada (para escolher alunos de turmas diferentes)
  const [alunosPorTurma, setAlunosPorTurma] = useState<Record<string, MembroTurmaAPI[]>>({});
  // criando: "Como criar" e "Tipo do exercício" começam sem nada marcado; o resto do formulário aparece conforme a escolha
  const [aba, setAba] = useState<"escrever" | "ia" | null>(inicial ? "escrever" : null);
  const [tipoSel, setTipoSel] = useState<TipoExercicioAPI | null>(inicial ? inicial.tipo : null);
  // as questoes do exercicio (ao editar, so a que esta sendo editada); r = a primeira
  const [questoes, setQuestoes] = useState<Rascunho[]>([inicial ? {
    tipo: inicial.tipo, enunciado: inicial.enunciado,
    alternativas: inicial.alternativas ?? ["", "", "", ""], correta: inicial.resposta_correta,
    respostasExemplo: inicial.respostas_exemplo.length ? inicial.respostas_exemplo : [inicial.resposta_exemplo ?? ""],
    explicacao: inicial.explicacao ?? "",
    daIA: inicial.gerado_por_ia, respostaIA: false,
  } : vazio]);
  const r = questoes[0];
  const setR = (x: Rascunho) => setQuestoes((q) => [x, ...q.slice(1)]);
  const setQ = (i: number, x: Rascunho) => setQuestoes((q) => q.map((y, j) => (j === i ? x : y)));
  const novaQuestao = (tipo: TipoExercicioAPI): Rascunho => ({ ...vazio, tipo, alternativas: ["", "", "", ""], respostasExemplo: [""] });
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [sugerindoResposta, setSugerindoResposta] = useState<number | null>(null); // indice da questao
  // pedir para a IA
  const tipoIA: TipoExercicioAPI = tipoSel ?? "OBJETIVO";
  const [quantidade, setQuantidade] = useState(3);
  const [instrucoes, setInstrucoes] = useState("");
  const [gerando, setGerando] = useState(false);
  const [sugestoes, setSugestoes] = useState<SugestaoExercicioAPI[]>([]);

  useEffect(() => {
    turmaIds.filter((id) => !alunosPorTurma[id]).forEach((id) =>
      membrosTurma(id)
        .then((m) => setAlunosPorTurma((x) => ({ ...x, [id]: m.filter((a) => a.papel === "ALUNO") })))
        .catch(() => {}));
  }, [turmaIds]);
  const nomeTurma = (id: string) => turmas.find((t) => t.id === id)?.nome ?? "Turma";
  // so conta escolhido que e de uma turma marcada (desmarcar a turma tira os alunos dela)
  const escolhidosValidos = escolhidos.filter((a) => turmaIds.some((t) => alunosPorTurma[t]?.some((m) => m.id === a)));
  const trocarTurma = (id: string) => { setTurmaIds([id]); setEscolhidos([]); };
  const alternarAluno = (id: string) =>
    setEscolhidos(escolhidos.includes(id) ? escolhidos.filter((x) => x !== id) : [...escolhidos, id]);

  const comuns = (): string | null => {
    if (!materiaId) return "Escolha a matéria.";
    if (!assunto.trim()) return "Escreva o tema do exercício.";
    if (!turmaIds.length) return "Escolha pelo menos uma turma.";
    if (paraAlguns === null) return "Escolha para quem é o exercício.";
    if (paraAlguns && !escolhidosValidos.length) return "Escolha pelo menos um aluno (ou marque “Todos os alunos”).";
    return null;
  };

  const payloadDe = (x: Rascunho, nome: string): ExercicioPayload | string => {
    if (!nome.trim()) return "Dê um nome ao exercício.";
    if (!x.enunciado.trim()) return "Escreva o enunciado.";
    const base = { titulo: nome.trim(), assunto: assunto.trim(), materia_id: materiaId, turma_id: turmaIds[0],
      aluno_ids: paraAlguns ? escolhidosValidos : null,
      tipo: x.tipo, enunciado: x.enunciado.trim(), explicacao: x.explicacao.trim() || null,
      gerado_por_ia: x.daIA || (x.tipo === "DISCURSIVO" && x.respostaIA) };
    if (x.tipo === "OBJETIVO") {
      const alts = x.alternativas.map((a) => a.trim());
      if (alts.length < 2 || alts.some((a) => !a)) return "Preencha todas as alternativas (ou remova as vazias).";
      if (x.correta === null || x.correta >= alts.length) return "Marque qual alternativa é a correta.";
      return { ...base, alternativas: alts, resposta_correta: x.correta };
    }
    const exemplos = x.respostasExemplo.map((e) => e.trim()).filter(Boolean);
    if (!exemplos.length) return "Escreva a resposta de exemplo ou clique em “IA sugere”.";
    return { ...base, resposta_exemplo: exemplos[0], respostas_exemplo: exemplos };
  };

  const salvar = async (x: Rascunho, nome: string, fechar: boolean, extras: Rascunho[] = []): Promise<boolean> => {
    const p = comuns() ?? payloadDe(x, nome);
    if (typeof p === "string") { setErro(p); return false; }
    // as questoes de baixo entram no mesmo exercicio
    const mais: QuestaoExercicioPayload[] = [];
    for (const [k, e] of extras.entries()) {
      const pe = payloadDe(e, nome);
      if (typeof pe === "string") { setErro(`Questão ${k + 2}: ${pe}`); return false; }
      const { tipo, enunciado, alternativas, resposta_correta, resposta_exemplo, respostas_exemplo, explicacao, gerado_por_ia } = pe;
      mais.push({ tipo, enunciado, alternativas, resposta_correta, resposta_exemplo, respostas_exemplo, explicacao, gerado_por_ia });
    }
    setSalvando(true); setErro("");
    try {
      if (inicial) await editarExercicio(inicial.id, p);
      else await criarExerciciosLote({ ...p, turma_ids: turmaIds, mais_questoes: mais.length ? mais : undefined });
      const quem = p.aluno_ids?.length ? "Os alunos escolhidos já veem"
        : turmaIds.length > 1 ? `As ${turmaIds.length} turmas já veem` : "A turma já vê";
      notify(inicial ? "Exercício atualizado." : `Exercício${mais.length ? ` com ${mais.length + 1} questões` : ""} salvo. ${quem} em Exercícios › Do professor.`);
      onSalvo(fechar);
      return true;
    } catch (e) { setErro(erroDe(e, "Não foi possível salvar.")); return false; }
    finally { setSalvando(false); }
  };

  const iaSugereResposta = async (k: number) => {
    const q = questoes[k];
    if (!materiaId) return setErro("Escolha a matéria antes de pedir para a IA.");
    if (!q.enunciado.trim()) return setErro("Escreva o enunciado antes de pedir a resposta para a IA.");
    setSugerindoResposta(k); setErro("");
    try {
      const { resposta_exemplo } = await sugerirRespostaExemplo({ materia_id: materiaId, assunto: assunto.trim() || undefined, enunciado: q.enunciado });
      // preenche a primeira vazia; se todas estao preenchidas, entra como mais uma
      const vazia = q.respostasExemplo.findIndex((e) => !e.trim());
      const lista = vazia >= 0 ? q.respostasExemplo.map((e, i) => (i === vazia ? resposta_exemplo : e))
        : [...q.respostasExemplo, resposta_exemplo].slice(0, MAX_EXEMPLOS);
      setQ(k, { ...q, respostasExemplo: lista, respostaIA: true });
    } catch (e) { setErro(erroDe(e, "A IA não conseguiu sugerir agora.")); }
    finally { setSugerindoResposta(null); }
  };

  const gerar = async () => {
    if (!materiaId) return setErro("Escolha a matéria.");
    if (!assunto.trim()) return setErro("Escreva o tema para a IA.");
    setGerando(true); setErro(""); setSugestoes([]);
    try {
      setSugestoes(await sugerirExercicios({ materia_id: materiaId, assunto: assunto.trim(), tipo: tipoIA, quantidade,
        instrucoes: instrucoes.trim() || undefined }));
    } catch (e) { setErro(erroDe(e, "A IA não conseguiu gerar agora. Tente de novo.")); }
    finally { setGerando(false); }
  };

  const daSugestao = (s: SugestaoExercicioAPI): Rascunho => ({
    tipo: s.alternativas.length ? "OBJETIVO" : "DISCURSIVO", enunciado: s.enunciado,
    alternativas: s.alternativas.length ? s.alternativas : ["", "", "", ""], correta: s.resposta_correta,
    respostasExemplo: [s.resposta_exemplo ?? ""], explicacao: s.explicacao, daIA: true, respostaIA: false,
  });

  const revisar = (s: SugestaoExercicioAPI, i: number) => {
    setQuestoes([daSugestao(s)]);
    setTipoSel(daSugestao(s).tipo);
    if (!titulo.trim()) setTitulo(s.titulo);
    setSugestoes(sugestoes.filter((_, j) => j !== i));
    setAba("escrever");
    notify("Sugestão copiada para “Escrever eu mesmo”. Revise e salve.");
  };

  // varias sugestoes viram as questoes de UM exercicio (como em Atividades)
  const juntar = () => {
    setQuestoes(sugestoes.map(daSugestao));
    setTipoSel(daSugestao(sugestoes[0]).tipo);
    if (!titulo.trim()) setTitulo(sugestoes[0].titulo);
    setSugestoes([]);
    setAba("escrever");
    notify("Sugestões juntas num só exercício. Revise e salve.");
  };

  const salvarSugestao = async (s: SugestaoExercicioAPI, i: number) => {
    // com varias sugestoes, cada uma usa o proprio titulo (o "Nome" de cima vale so para uma)
    const nome = sugestoes.length === 1 && titulo.trim() ? titulo : s.titulo;
    if (await salvar(daSugestao(s), nome, false)) {
      const resto = sugestoes.filter((_, j) => j !== i);
      setSugestoes(resto);
    }
  };

  return (
    <div>
      <div className="form-grid">
        <label>Nome do exercício
          <input value={titulo} onChange={(e) => setTitulo(e.target.value)}
            placeholder={aba === "ia" ? "Opcional: se vazio, a IA sugere" : "Ex.: Conectivos entre parágrafos"} />
        </label>
        <label>Matéria
          <Escolha value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
            <option value="">Escolha...</option>
            {materias.map((m) => <option key={m.id} value={m.id}>{m.nome}</option>)}
          </Escolha>
        </label>
        <label>Tema
          <input value={assunto} onChange={(e) => setAssunto(e.target.value)} placeholder="Ex.: Coesão, Função afim, Porcentagem" />
        </label>
        {inicial ? (
          <label>Turma
            <Escolha value={turmaId} onChange={(e) => trocarTurma(e.target.value)}>
              {turmas.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
            </Escolha>
          </label>
        ) : (
          <fieldset className="para-quem">
            <legend>Turmas</legend>
            {turmas.length ? (
              <SeletorMultiplo todos="Selecionar todos" rotulo="Turmas" placeholder="Escolha as turmas"
                opcoes={turmas.map((t) => ({ valor: t.id, rotulo: t.nome }))} valores={turmaIds} onChange={setTurmaIds} />
            ) : <p className="tiny muted">Você ainda não está em nenhuma turma.</p>}
          </fieldset>
        )}
        {turmaIds.length > 0 && (
          <fieldset className="para-quem">
            <legend>Para quem</legend>
            <Seletor rotulo="Para quem" placeholder="Escolha para quem" obrigatorio
              opcoes={[{ valor: "todos", rotulo: turmaIds.length > 1 ? "Todos os alunos dessas turmas" : "Todos os alunos da turma" },
                       { valor: "alguns", rotulo: "Escolher alunos" }]}
              valor={paraAlguns === null ? "" : paraAlguns ? "alguns" : "todos"} onChange={(v) => setParaAlguns(v === "alguns")} />
            {paraAlguns && (
              <div className="lista-alunos">
                {turmaIds.map((t) => (
                  <div key={t} className="grupo-turma">
                    {turmaIds.length > 1 && <p className="grupo-turma-nome">{nomeTurma(t)}</p>}
                    {!alunosPorTurma[t] ? <p className="tiny muted">Carregando...</p>
                      : !alunosPorTurma[t].length ? <p className="tiny muted">Esta turma ainda não tem alunos.</p>
                      : alunosPorTurma[t].map((a) => (
                        <label key={a.id} className="aluno-check">
                          <input type="checkbox" checked={escolhidos.includes(a.id)} onChange={() => alternarAluno(a.id)} />
                          {a.nome}
                        </label>
                      ))}
                  </div>
                ))}
                <p className="tiny muted">
                  {escolhidosValidos.length} aluno(s) escolhido(s)
                  {turmaIds.length > 1 ? ". Só as turmas com algum aluno marcado recebem o exercício." : ""}
                </p>
              </div>
            )}
          </fieldset>
        )}
      </div>

      {!inicial && <p className="rotulo-escolha">Como criar</p>}
      {!inicial && (
        <Seletor rotulo="Como criar" placeholder="Escolha como criar"
          opcoes={[{ valor: "escrever", rotulo: "Escrever eu mesmo" }, { valor: "ia", rotulo: "Pedir para a IA" }]}
          valor={aba ?? ""} onChange={(v) => { setAba((v || null) as typeof aba); setTipoSel(null); setQuestoes([novaQuestao("OBJETIVO")]); setSugestoes([]); setQuantidade(3); setInstrucoes(""); }} />
      )}

      {aba !== null && (
        <>
          <p className="rotulo-escolha">Tipo do exercício</p>
          <Seletor rotulo="Tipo do exercício" placeholder="Escolha o tipo"
            opcoes={[{ valor: "OBJETIVO", rotulo: "Objetivo (alternativas)" }, { valor: "DISCURSIVO", rotulo: "Discursivo (o aluno escreve)" }]}
            valor={tipoSel ?? ""} onChange={(v) => { setTipoSel((v || null) as typeof tipoSel); setSugestoes([]); setQuantidade(3); setInstrucoes(""); setQuestoes([novaQuestao((v || "OBJETIVO") as TipoExercicioAPI)]); }} />
        </>
      )}

      {aba === null || tipoSel === null ? null : aba === "escrever" ? (
        <>
          {questoes.map((q, i) => (
            <div className={questoes.length > 1 ? "meta-linha" : undefined} key={i}>
              {questoes.length > 1 && (
                <div className="meta-topo">
                  <strong>Questão {i + 1}</strong>
                  <button type="button" className="botao-pequeno perigo" onClick={() => setQuestoes(questoes.filter((_, j) => j !== i))}>
                    <Trash2 size={14} /> Remover questão
                  </button>
                </div>
              )}
              <EditorQuestao r={q} setR={(x) => setQ(i, x)} sugerindoResposta={sugerindoResposta === i} onSugerirResposta={() => iaSugereResposta(i)} />
            </div>
          ))}
          {!inicial && (
            <div className="form-actions left">
              <Button variant="secondary" icon={Plus} onPress={() => setQuestoes([...questoes, novaQuestao(tipoSel ?? "OBJETIVO")])}>
                Adicionar questão
              </Button>
            </div>
          )}
          {erro && <p className="error" role="alert">{erro}</p>}
          {questoes.some((q) => q.tipo === "OBJETIVO" && q.correta === null) && <p className="tiny muted">Marque qual alternativa é a correta em cada questão para poder salvar.</p>}
          <div className="form-actions left">
            <Button variant="secondary" onPress={onFechar}>Cancelar</Button>
            <Button icon={Check} disabled={salvando || questoes.some((q) => q.tipo === "OBJETIVO" && q.correta === null)}
              onPress={() => salvar(r, titulo, true, questoes.slice(1))}>
              {salvando ? "Salvando..." : inicial ? "Salvar alterações" : "Salvar e publicar para a turma"}
            </Button>

          </div>
        </>
      ) : (
        <>
          <div className="form-grid">
            <label>Quantos exercícios
              <Escolha value={quantidade} onChange={(e) => setQuantidade(Number(e.target.value))}>
                {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
              </Escolha>
            </label>
            <label className="span-2">Pedido para a IA (opcional)
              <textarea rows={2} value={instrucoes} onChange={(e) => setInstrucoes(e.target.value)}
                placeholder="Ex.: nível fácil, usar situações do dia a dia, estilo ENEM" />
            </label>
          </div>
          <p className="tiny muted">A IA só cria rascunhos. Nada chega ao aluno até você salvar.</p>
          {erro && <p className="error" role="alert">{erro}</p>}
          <div className="form-actions left">
            <Button variant="secondary" onPress={onFechar}>Fechar</Button>
            <Button icon={Sparkles} disabled={gerando} onPress={gerar}>
              {gerando ? "A IA está criando..." : sugestoes.length ? "Gerar de novo" : "Gerar sugestões"}
            </Button>
            {sugestoes.length > 1 && (
              <Button variant="secondary" icon={Plus} onPress={juntar}>Juntar todas num exercício</Button>
            )}
          </div>
          {sugestoes.map((s, i) => (
            <div className="meta-linha" key={`${i}-${s.titulo}`}>
              <div className="meta-topo">
                <strong>{s.titulo}</strong>
                <Badge tone="neutral">{s.alternativas.length ? "Objetivo" : "Discursivo"}</Badge>
              </div>
              <p className="exercicio-preview">{s.enunciado}</p>
              {s.alternativas.length > 0 ? (
                <ol className="lista-alternativas">
                  {s.alternativas.map((a, k) => (
                    <li key={k} className={k === s.resposta_correta ? "certa" : ""}>
                      <b>{LETRAS[k]})</b> {a} {k === s.resposta_correta && <Badge>Correta</Badge>}
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="tiny"><b>Resposta de exemplo:</b> {s.resposta_exemplo}</p>
              )}
              {s.explicacao && <p className="tiny muted"><b>Explicação:</b> {s.explicacao}</p>}
              <div className="form-actions left">
                <Button variant="secondary" icon={Pencil} onPress={() => revisar(s, i)}>Revisar e editar</Button>
                <Button icon={Check} disabled={salvando} onPress={() => salvarSugestao(s, i)}>Salvar assim</Button>
              </div>
            </div>
          ))}
        </>
      )}
      {aba === null && (
        <div className="form-actions left">
          <Button variant="secondary" onPress={onFechar}>Cancelar</Button>
        </div>
      )}
    </div>
  );
}

/* ---------------- lista separada por turma ---------------- */

function ListaPorTurma({ lista, turmas, notify, onEditar, onExcluir }: {
  lista: ExercicioProfessorAPI[];
  turmas: TurmaAPI[];
  notify: (m: string) => void;
  onEditar: (ex: ExercicioProfessorAPI) => void;
  onExcluir: (ex: ExercicioProfessorAPI) => void;
}) {
  // as turmas do professor, mais alguma de onde ele tenha exercicio e ja nao esteja (fica no fim)
  const ids = [...turmas.map((t) => t.id), ...lista.map((e) => e.turma_id).filter((id) => !turmas.some((t) => t.id === id))];
  const unicas = [...new Set(ids)];
  const nome = (id: string) => turmas.find((t) => t.id === id)?.nome ?? lista.find((e) => e.turma_id === id)?.turma_nome ?? "Turma";
  const [turma, setTurma] = useState("");
  const atual = unicas.includes(turma) ? turma : ""; // nada pré-marcado; clicar de novo desmarca
  const daTurma = lista.filter((e) => !atual || e.turma_id === atual);
  const [verResumo, setVerResumo] = useState(false);
  const [abertoId, setAbertoId] = useState<string | null>(null);
  if (!unicas.length)
    return <Card><Empty title="Nenhuma turma" text="Quando você estiver em uma turma, os exercícios dela aparecem aqui." /></Card>;
  return (
    <Card>
      <Filtros grupos={[{
        id: "turma", titulo: "Turma", valor: atual, onChange: (v) => { setTurma(v); setAbertoId(null); },
        opcoes: unicas.map((id) => ({ valor: id, rotulo: `${nome(id)} (${lista.filter((e) => e.turma_id === id).length})` })),
      }]} />
      {atual && turmas.some((t) => t.id === atual) && (
        <div className="form-actions left">
          <Button variant="secondary" icon={verResumo ? ChevronUp : ChevronDown} onPress={() => setVerResumo(!verResumo)}>
            {verResumo ? "Esconder resumo dos alunos" : "Resumo dos alunos desta turma"}
          </Button>
        </div>
      )}
      {verResumo && atual && <ResumoTurma key={atual} turmaId={atual} notify={notify} />}
      {!daTurma.length ? (
        <Empty title="Nenhum exercício aqui" text="Crie um em “Novo exercício” ou mude os filtros." />
      ) : daTurma.map((ex) => (
        <div className="meta-linha" key={ex.id}>
          <div className="meta-topo">
            <strong>{ex.titulo}</strong>
            <span>
              {ex.grupo_id && <><Badge tone="neutral">Questão {ex.ordem + 1} de {lista.filter((x) => x.grupo_id === ex.grupo_id).length}</Badge>{" "}</>}
              <Badge tone="neutral">{ex.tipo === "OBJETIVO" ? "Objetivo" : "Discursivo"}</Badge>{" "}
              {ex.gerado_por_ia && <Badge tone="amber">Com ajuda da IA</Badge>}
            </span>
          </div>
          <p className="tiny muted">
            {ex.alunos_nomes.length ? `Só para ${ex.alunos_nomes.join(", ")}` : "Turma toda"}
            {" · "}{ex.materia_nome} · Tema: {ex.assunto}
          </p>
          <p className="exercicio-preview">{ex.enunciado}</p>
          <p className="tiny muted">
            {ex.respostas} de {ex.alunos_alvo} aluno(s) fizeram
            {ex.respostas > 0 && ex.tipo === "OBJETIVO" ? ` · ${ex.acertos} acertaram` : ""}
          </p>
          <div className="form-actions left">
            <Button variant={abertoId === ex.id ? "primary" : "secondary"} icon={abertoId === ex.id ? ChevronUp : ChevronDown}
              onPress={() => setAbertoId(abertoId === ex.id ? null : ex.id)}>
              {abertoId === ex.id ? "Esconder respostas" : "Ver respostas"}
            </Button>
            <Button variant="ghost" icon={Pencil} onPress={() => onEditar(ex)}>Editar</Button>
            <Button variant="ghost" icon={Trash2} onPress={() => onExcluir(ex)}>{ex.grupo_id ? "Excluir exercício inteiro" : "Excluir"}</Button>
          </div>
          {abertoId === ex.id && <RespostasExercicio ex={ex} notify={notify} />}
        </div>
      ))}
    </Card>
  );
}

function ResumoTurma({ turmaId, notify }: { turmaId: string; notify: (m: string) => void }) {
  const [linhas, setLinhas] = useState<ResumoAlunoAPI[] | null>(null);
  useEffect(() => {
    resumoExerciciosTurma(turmaId).then(setLinhas).catch((e) => notify(erroDe(e, "Não foi possível carregar o resumo.")));
  }, [turmaId]);
  if (!linhas) return <p className="muted">Carregando...</p>;
  if (!linhas.length) return <p className="tiny muted">Esta turma ainda não tem alunos.</p>;
  return (
    <div className="tabela-rolagem">
      <table className="tabela-ranking">
        <thead><tr><th>Aluno</th><th>Fez</th><th>Acertou</th></tr></thead>
        <tbody>
          {linhas.map((l) => (
            <tr key={l.aluno_id}>
              <td>{l.nome}</td>
              <td>{l.feitos} de {l.total}</td>
              <td>
                {l.corrigidos ? `${l.acertos} de ${l.corrigidos}${l.parciais ? ` (+${l.parciais} parcial)` : ""}` : "—"}
                {l.feitos > l.corrigidos && <span className="tiny muted"> ({l.feitos - l.corrigidos} discursivo(s) para corrigir)</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="tiny muted">“Acertou” conta os objetivos (automático) e os discursivos que você já corrigiu. Parcial aparece à parte.</p>
    </div>
  );
}

function RespostasExercicio({ ex, notify }: { ex: ExercicioProfessorAPI; notify: (m: string) => void }) {
  const [linhas, setLinhas] = useState<RespostaAlunoAPI[] | null>(null);
  const [filtro, setFiltro] = useState<"todos" | "fizeram" | "faltam">("todos");
  useEffect(() => {
    respostasDoExercicio(ex.id).then(setLinhas).catch((e) => notify(erroDe(e, "Não foi possível carregar as respostas.")));
  }, [ex.id]);
  if (!linhas) return <p className="muted">Carregando respostas...</p>;
  if (!linhas.length) return <p className="tiny muted">Ninguém precisa fazer este exercício (a turma está sem alunos).</p>;
  const fizeram = linhas.filter((l) => l.fez);
  const visiveis = filtro === "fizeram" ? fizeram : filtro === "faltam" ? linhas.filter((l) => !l.fez) : linhas;
  const atualizar = (nova: RespostaAlunoAPI) => setLinhas(linhas.map((l) => (l.aluno_id === nova.aluno_id ? nova : l)));
  return (
    <div className="painel-respostas">
      {ex.tipo === "DISCURSIVO" && ex.respostas_exemplo.length > 0 && (
        <details className="exemplo-prof">
          <summary>{ex.respostas_exemplo.length > 1 ? "Ver as respostas de exemplo (para comparar)" : "Ver a resposta de exemplo (para comparar)"}</summary>
          {ex.respostas_exemplo.map((e, i) => (
            <p key={i}>{ex.respostas_exemplo.length > 1 && <b>{i + 1}. </b>}{e}</p>
          ))}
        </details>
      )}
      <Filtros grupos={[{
        id: "situacao", titulo: "Situação", valor: filtro === "todos" ? "" : filtro, onChange: (v) => setFiltro((v || "todos") as typeof filtro),
        opcoes: [{ valor: "fizeram", rotulo: `Fizeram (${fizeram.length})` }, { valor: "faltam", rotulo: `Não fizeram (${linhas.length - fizeram.length})` }],
      }]} />
      {!visiveis.length && <p className="tiny muted">Ninguém aqui.</p>}
      {visiveis.map((l) => <LinhaResposta key={l.aluno_id} ex={ex} linha={l} onSalva={atualizar} notify={notify} />)}
    </div>
  );
}

function LinhaResposta({ ex, linha, onSalva, notify }: {
  ex: ExercicioProfessorAPI; linha: RespostaAlunoAPI; onSalva: (l: RespostaAlunoAPI) => void; notify: (m: string) => void;
}) {
  // nada salva sozinho: o professor escolhe, comenta e clica em "Salvar"
  const [escolha, setEscolha] = useState<ResultadoAPI | null>(linha.resultado ?? null);
  const [comentario, setComentario] = useState(linha.comentario ?? "");
  const [comentando, setComentando] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const objetivo = ex.tipo === "OBJETIVO";
  const mudou = escolha !== (linha.resultado ?? null) || comentario.trim() !== (linha.comentario ?? "");
  // parcial/errada precisa de comentario
  const exigeComentario = !objetivo && (escolha === "PARCIAL" || escolha === "ERRADA");
  const podeSalvar = mudou && (!exigeComentario || comentario.trim().length > 0);
  const caixaAberta = comentando || exigeComentario;
  const salvar = async () => {
    setSalvando(true);
    try {
      const p: { resultado?: ResultadoAPI | null; comentario?: string | null } = { comentario: comentario.trim() || null };
      if (!objetivo) p.resultado = escolha;
      onSalva(await avaliarRespostaExercicio(ex.id, linha.aluno_id, p));
      notify("Salvo.");
      setComentando(false);
    } catch (e) { notify(erroDe(e, "Não foi possível salvar.")); }
    finally { setSalvando(false); }
  };
  const cancelar = () => { setEscolha(linha.resultado ?? null); setComentario(linha.comentario ?? ""); setComentando(false); };
  const marcada = objetivo && linha.resposta !== null ? Number(linha.resposta) : null;
  const status = !linha.fez ? <Badge tone="neutral">Não fez</Badge>
    : linha.resultado === "CERTA" ? <Badge>Acertou</Badge>
    : linha.resultado === "PARCIAL" ? <Badge tone="amber">Parcial</Badge>
    : linha.resultado === "ERRADA" ? <Badge tone="amber">Errou</Badge>
    : <Badge tone="neutral">Para corrigir</Badge>;
  const BOTOES = [
    ["CERTA", "Certo", "marcado-certo", <Check size={14} key="i" />],
    ["PARCIAL", "Parcial", "marcado-parcial", <CircleHalf key="i" />],
    ["ERRADA", "Errado", "marcado-errado", <X size={14} key="i" />],
  ] as const;
  return (
    <div className={`resposta-aluno ${linha.fez ? "" : "nao-fez"}`}>
      <div className="meta-topo">
        <strong>{linha.nome}</strong>
        {status}
      </div>
      {linha.fez && (
        <>
          {objetivo ? (
            <p className="tiny">
              Marcou <b>{marcada !== null ? `${LETRAS[marcada]}) ${ex.alternativas?.[marcada] ?? ""}` : "—"}</b>
              {linha.resultado === "ERRADA" && ex.resposta_correta !== null && (
                <> · a certa era <b>{LETRAS[ex.resposta_correta]})</b></>
              )}
            </p>
          ) : (
            <p className="texto-resposta">{linha.resposta}</p>
          )}
          <div className="alternativa-acoes">
            {!objetivo && BOTOES.map(([valor, rotulo, classe, icone]) => (
              <button type="button" key={valor} disabled={salvando} aria-pressed={escolha === valor}
                className={`botao-pequeno ${escolha === valor ? classe : ""}`}
                onClick={() => setEscolha(escolha === valor ? null : valor)}>
                {icone} {rotulo}
              </button>
            ))}
            {!caixaAberta && (
              <button type="button" className="botao-pequeno" onClick={() => setComentando(true)}>
                <MessageSquare size={14} /> {linha.comentario ? "Editar comentário" : "Comentar"}
              </button>
            )}
          </div>
          {linha.comentario && !caixaAberta && (
            <p className="comentario-prof"><b>Seu comentário:</b> {linha.comentario}</p>
          )}
          {caixaAberta && (
            <div className="comentar">
              {exigeComentario && (
                <p className="tiny aviso-comentario">
                  Para marcar como {escolha === "PARCIAL" ? "parcial" : "errada"}, escreva o que faltou ou o que está errado.
                </p>
              )}
              <textarea rows={2} value={comentario} onChange={(e) => setComentario(e.target.value)}
                aria-label={`Comentário para ${linha.nome}`}
                placeholder={exigeComentario ? "Obrigatório: explique ao aluno o que faltou" : "Opcional: o aluno vê este comentário junto com a resposta dele"} />
            </div>
          )}
          {mudou && (
            <div className="alternativa-acoes acoes-salvar">
              <button type="button" className="botao-pequeno botao-salvar" disabled={salvando || !podeSalvar} aria-busy={salvando}
                onClick={salvar}>
                <Check size={14} /> {salvando ? "Salvando..." : "Salvar"}
              </button>
              <button type="button" className="botao-pequeno" disabled={salvando} onClick={cancelar}>Cancelar</button>
              {exigeComentario && !comentario.trim() && (
                <span className="tiny muted">O comentário é obrigatório quando a resposta é parcial ou errada.</span>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// meio circulo (parcial): o lucide nao tem um icone "meio certo" claro
function CircleHalf() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" />
    </svg>
  );
}
