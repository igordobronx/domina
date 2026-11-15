import { useEffect, useState } from "react";
import { Check, Pencil, Plus, Sparkles, Trash2 } from "lucide-react";
import { Badge, Button, Card, Empty, SectionTitle } from "../components/ui";
import { CampoComSimbolos } from "../components/CampoComSimbolos";
import {
  criarExercicio, editarExercicio, excluirExercicio, listarExerciciosProfessor, listarMaterias,
  listarTurmasMinhas, sugerirExercicios, sugerirRespostaExemplo,
  type ExercicioPayload, type ExercicioProfessorAPI, type MateriaAPI, type SugestaoExercicioAPI,
  type TipoExercicioAPI, type TurmaAPI,
} from "../services/api";

// Exercicios de PRATICA do professor (nao valem nota; provas continuam em Atividades).
// O professor escreve o exercicio ou pede rascunhos para a IA; nada chega ao aluno sem ele salvar.
// No aluno, tudo daqui aparece na aba "Do professor" (mesmo se a IA ajudou: so ganha um selo).

const LETRAS = "ABCDEF";
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
    if (!window.confirm(`Excluir o exercício "${ex.titulo}"? Ele some para os alunos.`)) return;
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
        {!aberto && <Button icon={Plus} onPress={() => setAberto("novo")}>Novo exercício</Button>}
      </div>
      {aberto && (
        <FormExercicio
          key={aberto === "novo" ? "novo" : aberto.id}
          inicial={aberto === "novo" ? null : aberto}
          turmas={turmas}
          materias={materias}
          notify={notify}
          onFechar={() => setAberto(null)}
          onSalvo={(fechar) => { if (fechar) setAberto(null); recarregar(); }}
        />
      )}
      <Card>
        <SectionTitle title="Meus exercícios" />
        {lista === null ? <p className="muted">Carregando...</p> : !lista.length ? (
          <Empty title="Nenhum exercício ainda" text="Crie o primeiro: ele aparece para os alunos da turma na aba Exercícios › Do professor." />
        ) : lista.map((ex) => (
          <div className="meta-linha" key={ex.id}>
            <div className="meta-topo">
              <strong>{ex.titulo}</strong>
              <span>
                <Badge tone="neutral">{ex.tipo === "OBJETIVO" ? "Objetivo" : "Discursivo"}</Badge>{" "}
                {ex.gerado_por_ia && <Badge tone="amber">Com ajuda da IA</Badge>}
              </span>
            </div>
            <p className="tiny muted">{ex.turma_nome} · {ex.materia_nome} · Tema: {ex.assunto}</p>
            <p className="exercicio-preview">{ex.enunciado}</p>
            <p className="tiny muted">
              {ex.respostas === 0 ? "Nenhum aluno fez ainda"
                : `${ex.respostas} aluno(s) fizeram${ex.tipo === "OBJETIVO" ? ` · ${ex.acertos} acertaram` : ""}`}
            </p>
            <div className="form-actions left">
              <Button variant="ghost" icon={Pencil} onPress={() => { setAberto(ex); window.scrollTo(0, 0); }}>Editar</Button>
              <Button variant="ghost" icon={Trash2} onPress={() => excluir(ex)}>Excluir</Button>
            </div>
          </div>
        ))}
      </Card>
    </>
  );
}

type Rascunho = {
  tipo: TipoExercicioAPI;
  enunciado: string;
  alternativas: string[];
  correta: number | null;
  respostaExemplo: string;
  explicacao: string;
  daIA: boolean; // veio de uma sugestao da IA
  respostaIA: boolean; // a resposta de exemplo (discursivo) foi sugerida pela IA
};

const vazio: Rascunho = {
  tipo: "OBJETIVO", enunciado: "", alternativas: ["", "", "", ""], correta: null,
  respostaExemplo: "", explicacao: "", daIA: false, respostaIA: false,
};

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
  const [turmaId, setTurmaId] = useState(inicial?.turma_id ?? "");
  const [aba, setAba] = useState<"escrever" | "ia">("escrever");
  const [r, setR] = useState<Rascunho>(inicial ? {
    tipo: inicial.tipo, enunciado: inicial.enunciado,
    alternativas: inicial.alternativas ?? ["", "", "", ""], correta: inicial.resposta_correta,
    respostaExemplo: inicial.resposta_exemplo ?? "", explicacao: inicial.explicacao ?? "",
    daIA: inicial.gerado_por_ia, respostaIA: false,
  } : vazio);
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [sugerindoResposta, setSugerindoResposta] = useState(false);
  // pedir para a IA
  const [tipoIA, setTipoIA] = useState<TipoExercicioAPI>("OBJETIVO");
  const [quantidade, setQuantidade] = useState(3);
  const [instrucoes, setInstrucoes] = useState("");
  const [gerando, setGerando] = useState(false);
  const [sugestoes, setSugestoes] = useState<SugestaoExercicioAPI[]>([]);

  useEffect(() => { if (!turmaId && turmas.length === 1) setTurmaId(turmas[0].id); }, [turmas]);
  useEffect(() => { if (!materiaId && materias.length === 1) setMateriaId(materias[0].id); }, [materias]);

  const comuns = (): string | null => {
    if (!materiaId) return "Escolha a matéria.";
    if (!assunto.trim()) return "Escreva o tema do exercício.";
    if (!turmaId) return "Escolha a turma.";
    return null;
  };

  const payloadDe = (x: Rascunho, nome: string): ExercicioPayload | string => {
    if (!nome.trim()) return "Dê um nome ao exercício.";
    if (!x.enunciado.trim()) return "Escreva o enunciado.";
    const base = { titulo: nome.trim(), assunto: assunto.trim(), materia_id: materiaId, turma_id: turmaId,
      tipo: x.tipo, enunciado: x.enunciado.trim(), explicacao: x.explicacao.trim() || null,
      gerado_por_ia: x.daIA || (x.tipo === "DISCURSIVO" && x.respostaIA) };
    if (x.tipo === "OBJETIVO") {
      const alts = x.alternativas.map((a) => a.trim());
      if (alts.length < 2 || alts.some((a) => !a)) return "Preencha todas as alternativas (ou remova as vazias).";
      if (x.correta === null || x.correta >= alts.length) return "Marque qual alternativa é a correta.";
      return { ...base, alternativas: alts, resposta_correta: x.correta };
    }
    if (!x.respostaExemplo.trim()) return "Escreva a resposta de exemplo ou clique em “IA sugere”.";
    return { ...base, resposta_exemplo: x.respostaExemplo.trim() };
  };

  const salvar = async (x: Rascunho, nome: string, fechar: boolean): Promise<boolean> => {
    const p = comuns() ?? payloadDe(x, nome);
    if (typeof p === "string") { setErro(p); return false; }
    setSalvando(true); setErro("");
    try {
      if (inicial) await editarExercicio(inicial.id, p);
      else await criarExercicio(p);
      notify(inicial ? "Exercício atualizado." : "Exercício salvo. A turma já vê em Exercícios › Do professor.");
      onSalvo(fechar);
      return true;
    } catch (e) { setErro(erroDe(e, "Não foi possível salvar.")); return false; }
    finally { setSalvando(false); }
  };

  const iaSugereResposta = async () => {
    if (!materiaId) return setErro("Escolha a matéria antes de pedir para a IA.");
    if (!r.enunciado.trim()) return setErro("Escreva o enunciado antes de pedir a resposta para a IA.");
    setSugerindoResposta(true); setErro("");
    try {
      const { resposta_exemplo } = await sugerirRespostaExemplo({ materia_id: materiaId, assunto: assunto.trim() || undefined, enunciado: r.enunciado });
      setR({ ...r, respostaExemplo: resposta_exemplo, respostaIA: true });
    } catch (e) { setErro(erroDe(e, "A IA não conseguiu sugerir agora.")); }
    finally { setSugerindoResposta(false); }
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
    respostaExemplo: s.resposta_exemplo ?? "", explicacao: s.explicacao, daIA: true, respostaIA: false,
  });

  const revisar = (s: SugestaoExercicioAPI, i: number) => {
    setR(daSugestao(s));
    if (!titulo.trim()) setTitulo(s.titulo);
    setSugestoes(sugestoes.filter((_, j) => j !== i));
    setAba("escrever");
    notify("Sugestão copiada para “Escrever eu mesmo”. Revise e salve.");
  };

  const salvarSugestao = async (s: SugestaoExercicioAPI, i: number) => {
    // com varias sugestoes, cada uma usa o proprio titulo (o "Nome" de cima vale so para uma)
    const nome = sugestoes.length === 1 && titulo.trim() ? titulo : s.titulo;
    if (await salvar(daSugestao(s), nome, false)) {
      const resto = sugestoes.filter((_, j) => j !== i);
      setSugestoes(resto);
    }
  };

  const alts = r.alternativas;
  const setAlt = (k: number, v: string) => setR({ ...r, alternativas: alts.map((x, j) => (j === k ? v : x)) });

  return (
    <Card>
      <SectionTitle title={inicial ? "Editar exercício" : "Novo exercício"} />
      <div className="form-grid">
        <label>Nome do exercício
          <input value={titulo} onChange={(e) => setTitulo(e.target.value)}
            placeholder={aba === "ia" ? "Opcional: se vazio, a IA sugere" : "Ex.: Conectivos entre parágrafos"} />
        </label>
        <label>Matéria
          <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
            <option value="">Escolha...</option>
            {materias.map((m) => <option key={m.id} value={m.id}>{m.nome}</option>)}
          </select>
        </label>
        <label>Tema
          <input value={assunto} onChange={(e) => setAssunto(e.target.value)} placeholder="Ex.: Coesão, Função afim, Porcentagem" />
        </label>
        <label>Turma
          <select value={turmaId} onChange={(e) => setTurmaId(e.target.value)}>
            <option value="">Escolha...</option>
            {turmas.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
          </select>
        </label>
      </div>

      {!inicial && (
        <div className="tabs" role="group" aria-label="Como criar">
          <button aria-pressed={aba === "escrever"} className={aba === "escrever" ? "active" : ""}
            onClick={() => setAba("escrever")}>Escrever eu mesmo</button>
          <button aria-pressed={aba === "ia"} className={aba === "ia" ? "active" : ""}
            onClick={() => setAba("ia")}><Sparkles size={14} /> Pedir para a IA</button>
        </div>
      )}

      {aba === "escrever" ? (
        <>
          <div className="tabs" role="group" aria-label="Tipo do exercício">
            <button aria-pressed={r.tipo === "OBJETIVO"} className={r.tipo === "OBJETIVO" ? "active" : ""}
              onClick={() => setR({ ...r, tipo: "OBJETIVO" })}>Objetivo (alternativas)</button>
            <button aria-pressed={r.tipo === "DISCURSIVO"} className={r.tipo === "DISCURSIVO" ? "active" : ""}
              onClick={() => setR({ ...r, tipo: "DISCURSIVO" })}>Discursivo (o aluno escreve)</button>
          </div>
          <div className="form-grid ex-form">
          <label className="span-2">Enunciado
            <CampoComSimbolos rows={4} value={r.enunciado} onChange={(e) => setR({ ...r, enunciado: e.target.value })}
              placeholder="A pergunta, com o contexto que o aluno precisa" />
          </label>
          {r.tipo === "OBJETIVO" ? (
            <fieldset className="alternativas-form span-2">
              <legend>Alternativas (marque a correta)</legend>
              {alts.map((texto, k) => (
                <label key={k} className="alternativa">
                  <input type="radio" name="correta" aria-label={`Correta: ${LETRAS[k]}`} checked={r.correta === k}
                    onChange={() => setR({ ...r, correta: k })} />
                  <b>{LETRAS[k]})</b>
                  <CampoComSimbolos linha value={texto} placeholder={`Alternativa ${LETRAS[k]}`}
                    onChange={(e) => setAlt(k, e.target.value)} />
                </label>
              ))}
              <div className="form-actions left">
                {alts.length < LETRAS.length && (
                  <Button variant="ghost" icon={Plus} onPress={() => setR({ ...r, alternativas: [...alts, ""] })}>
                    Adicionar alternativa ({LETRAS[alts.length]})
                  </Button>
                )}
                {alts.length > 2 && (
                  <Button variant="ghost" icon={Trash2} onPress={() => setR({
                    ...r, alternativas: alts.slice(0, -1), correta: r.correta === alts.length - 1 ? null : r.correta,
                  })}>Remover a última</Button>
                )}
              </div>
            </fieldset>
          ) : (
            <>
              <label className="span-2">Resposta de exemplo (o aluno compara com a dele depois de responder)
                <CampoComSimbolos rows={4} value={r.respostaExemplo} onChange={(e) => setR({ ...r, respostaExemplo: e.target.value })}
                  placeholder="Escreva a resposta esperada, ou peça para a IA sugerir" />
              </label>
              <div className="form-actions left span-2">
                <Button variant="secondary" icon={Sparkles} disabled={sugerindoResposta} onPress={iaSugereResposta}>
                  {sugerindoResposta ? "A IA está escrevendo..." : "IA sugere a resposta"}
                </Button>
              </div>
            </>
          )}
          <label className="span-2">Explicação (opcional: aparece para o aluno depois que ele responde)
            <textarea rows={2} value={r.explicacao} onChange={(e) => setR({ ...r, explicacao: e.target.value })} />
          </label>
          </div>
          {erro && <p className="error" role="alert">{erro}</p>}
          <div className="form-actions left">
            <Button variant="secondary" onPress={onFechar}>Cancelar</Button>
            <Button icon={Check} disabled={salvando} onPress={() => salvar(r, titulo, true)}>
              {salvando ? "Salvando..." : inicial ? "Salvar alterações" : "Salvar e publicar para a turma"}
            </Button>
          </div>
        </>
      ) : (
        <>
          <div className="form-grid">
            <label>Tipo
              <select value={tipoIA} onChange={(e) => setTipoIA(e.target.value as TipoExercicioAPI)}>
                <option value="OBJETIVO">Objetivo (alternativas)</option>
                <option value="DISCURSIVO">Discursivo (o aluno escreve)</option>
              </select>
            </label>
            <label>Quantos
              <select value={quantidade} onChange={(e) => setQuantidade(Number(e.target.value))}>
                {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
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
    </Card>
  );
}
