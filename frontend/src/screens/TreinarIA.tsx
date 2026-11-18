import { useEffect, useState } from "react";
import { BookOpen, PenLine, Sparkles, Trash2, Upload } from "lucide-react";
import { Badge, Button, Card, Empty, SectionTitle } from "../components/ui";
import {
  criarInstrucao, dispensarSugestaoInstrucao, enviarDocumento, listarSugestoesInstrucao, excluirInstrucao, listarDocumentos, listarAprendido, listarErrosDaIA, listarInstrucoes, listarMaterias, usoDoItem,
  verMemoriaIA, type DocumentoAPI, type ErroDaIAAPI, type InstrucaoAPI, type ItemAprendidoAPI, type MateriaAPI, type MemoriaIAAPI, type SugestaoInstrucaoAPI,
} from "../services/api";

// "Treinar IA": o professor ensina a IA a corrigir e criar exercicios do jeito dele.
// Dois caminhos: enviar arquivo (apostila, rubrica, gabarito, plano de aula; PDF, foto, DOCX, TXT)
// ou escrever instrucoes ("sempre exija a verificacao final"). As duas coisas valem na hora, so
// para este professor naquela materia, e ficam guardadas como base para a IA propria do Domina.
// Sem nada enviado, a IA corrige com o conhecimento geral dela.

const TIPOS: { value: DocumentoAPI["tipo"]; label: string }[] = [
  { value: "APOSTILA", label: "Apostila" },
  { value: "RUBRICA", label: "Rubrica de correção" },
  { value: "GABARITO", label: "Gabarito" },
  { value: "PLANO_DE_AULA", label: "Plano de aula" },
];
const EXEMPLOS = [
  "Sempre exijo a verificação final da conta.",
  "Não desconto ponto por erro de acentuação.",
  "Resposta sem unidade perde metade da questão.",
  "No comentário, comece pelo que o aluno acertou.",
  "Aceite qualquer método de resolução que chegue ao resultado certo.",
  "Dê meio ponto quando o raciocínio estiver certo e só a conta errada.",
  "Explique o erro do aluno em uma frase simples, sem termos difíceis.",
  "Não aceite resposta sem justificativa, mesmo que o resultado esteja certo.",
  "Na redação, valorize argumento próprio mais do que texto decorado.",
  "Peça sempre a fórmula usada antes da conta.",
];
const NIVEL: Record<MemoriaIAAPI["nivel"], { label: string; tone: "neutral" | "amber" | "green" }> = {
  SEM_TREINO: { label: "Sem treino", tone: "neutral" },
  APRENDENDO: { label: "Ainda aprendendo", tone: "amber" },
  QUASE: { label: "Quase lá", tone: "amber" },
  PRONTA: { label: "Pronta", tone: "green" },
};
// concordância a cada 10 revisadas: barras simples (semana não serve: o professor pode corrigir pouco numa semana)
function Evolucao({ pontos }: { pontos: MemoriaIAAPI["evolucao"] }) {
  if (pontos.length < 2) return null;
  return (
    <div aria-label="Concordância da IA com você a cada 10 correções revisadas">
      <span className="tiny muted">Concordância a cada 10 correções que você revisou:</span>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 60, marginTop: 4 }}>
        {pontos.map((p) => (
          <div key={p.ate} title={`Até a correção ${p.ate}: ${p.concordancia}%`}
            style={{ flex: 1, maxWidth: 28, height: `${Math.max(p.concordancia, 4)}%`, background: "currentColor", opacity: 0.55, borderRadius: 3 }} />
        ))}
      </div>
      <span className="tiny muted">{pontos[0].concordancia}% → {pontos[pontos.length - 1].concordancia}%</span>
    </div>
  );
}
const LIMITE_MB = 20;
const erroDe = (e: unknown, padrao: string) => (e instanceof Error ? e.message : padrao);

export function TreinarIA({ notify }: { notify: (m: string) => void }) {
  const [materias, setMaterias] = useState<MateriaAPI[] | null>(null);
  const [materiaId, setMateriaId] = useState("");
  const [como, setComo] = useState<"arquivo" | "texto" | null>(null);
  const [tipo, setTipo] = useState<DocumentoAPI["tipo"]>("APOSTILA");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [texto, setTexto] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [memoria, setMemoria] = useState<Record<string, MemoriaIAAPI>>({});
  const [documentos, setDocumentos] = useState<DocumentoAPI[]>([]);
  const [instrucoes, setInstrucoes] = useState<InstrucaoAPI[]>([]);
  const [sugestoes, setSugestoes] = useState<SugestaoInstrucaoAPI[]>([]);
  const [erros, setErros] = useState<ErroDaIAAPI[]>([]);
  const [aprendido, setAprendido] = useState<ItemAprendidoAPI[]>([]);

  const carregarResumo = (ms: MateriaAPI[]) =>
    Promise.all(ms.map((m) => verMemoriaIA(m.id).then((r) => [m.id, r] as const)))
      .then((pares) => setMemoria(Object.fromEntries(pares)))
      .catch(() => setMemoria({})); // o resumo e um extra: se falhar a tela continua funcionando
  const carregarMateria = (id: string) => {
    if (!id) return;
    listarDocumentos(id).then(setDocumentos).catch(() => setDocumentos([]));
    listarInstrucoes(id).then(setInstrucoes).catch(() => setInstrucoes([]));
    listarSugestoesInstrucao(id).then(setSugestoes).catch(() => setSugestoes([]));
    listarErrosDaIA(id).then(setErros).catch(() => setErros([]));
    listarAprendido(id).then(setAprendido).catch(() => setAprendido([]));
  };
  useEffect(() => {
    listarMaterias()
      .then((ms) => {
        setMaterias(ms);
        if (ms.length === 1) setMateriaId(ms[0].id);
        carregarResumo(ms);
      })
      .catch(() => { setMaterias([]); notify("Não foi possível carregar as matérias."); });
  }, []);
  useEffect(() => carregarMateria(materiaId), [materiaId]);

  const depois = (aviso: string) => {
    notify(aviso);
    setErro("");
    carregarMateria(materiaId);
    if (materias) carregarResumo(materias);
  };
  const enviarArquivo = async () => {
    if (!materiaId) return setErro("Escolha a matéria que a IA vai aprender.");
    if (!arquivo) return setErro("Escolha o arquivo.");
    setSalvando(true);
    try {
      const doc = await enviarDocumento(materiaId, arquivo, tipo);
      setArquivo(null);
      if (doc.status_processamento === "ERRO") {
        setErro(doc.detalhe || "A IA não conseguiu ler este arquivo.");
        carregarMateria(materiaId);
      } else depois("A IA leu o material e já vai usar nas próximas correções.");
    } catch (e) { setErro(erroDe(e, "Não foi possível enviar o arquivo.")); }
    finally { setSalvando(false); }
  };
  const salvarTexto = async () => {
    if (!materiaId) return setErro("Escolha a matéria que a IA vai aprender.");
    if (texto.trim().length < 5) return setErro("Escreva a instrução (pelo menos 5 letras).");
    setSalvando(true);
    try {
      await criarInstrucao(materiaId, texto.trim());
      setTexto("");
      depois("Instrução salva. A IA vai seguir sempre nesta matéria.");
    } catch (e) { setErro(erroDe(e, "Não foi possível salvar a instrução.")); }
    finally { setSalvando(false); }
  };
  const apagar = async (i: InstrucaoAPI) => {
    if (!window.confirm("Apagar esta instrução? A IA para de segui-la.")) return;
    try { await excluirInstrucao(i.materia_id, i.id); depois("Instrução apagada."); }
    catch (e) { notify(erroDe(e, "Não foi possível apagar.")); }
  };
  const adotar = async (g: SugestaoInstrucaoAPI) => {
    try {
      await criarInstrucao(materiaId, g.texto);
      depois("Pronto: a IA vai seguir isso sempre nesta matéria.");
    } catch (e) { notify(erroDe(e, "Não foi possível salvar a instrução.")); }
  };
  const dispensar = async (g: SugestaoInstrucaoAPI) => {
    try { await dispensarSugestaoInstrucao(materiaId, g.correcao_ids); depois("Sugestão dispensada."); }
    catch (e) { notify(erroDe(e, "Não foi possível dispensar.")); }
  };
  const trocarUso = async (i: ItemAprendidoAPI) => {
    try { await usoDoItem(materiaId, i, !i.em_uso); depois(i.em_uso ? "A IA parou de usar isso (continua guardado)." : "A IA voltou a usar isso."); }
    catch (e) { notify(erroDe(e, "Não foi possível mudar.")); }
  };
  const nomeMateria = materias?.find((m) => m.id === materiaId)?.nome;

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">ENSINE A IA A CORRIGIR DO SEU JEITO</div>
          <h1>Treinar IA</h1>
          <p>
            Envie seus materiais ou escreva como você quer que a IA trabalhe. Ela passa a corrigir e criar
            exercícios do seu jeito. Sem nada seu, ela usa o conhecimento geral dela.
          </p>
        </div>
      </div>

      {!!materias?.length && (
        <Card>
          <SectionTitle title="O que a IA já aprendeu com você" />
          {materias.map((m) => {
            const r = memoria[m.id];
            const nada = !r || r.nivel === "SEM_TREINO";
            return (
              <div className="material-row" key={m.id}>
                <div className="activity-icon"><Sparkles size={21} /></div>
                <div className="activity-info">
                  <strong>{m.nome}</strong>
                  <span>
                    {nada
                      ? "Ainda nada seu. A IA corrige com o conhecimento geral dela."
                      : `${r.instrucoes} instrução(ões) · ${r.trechos_de_material} trecho(s) de material · ${r.correcoes_aprendidas} correção(ões) aprovada(s) · ${r.exercicios_aprendidos} exercício(s) corrigido(s)`}
                  </span>
                  {r && r.revisadas > 0 && r.concordancia !== null && (
                    <span>
                      {`Concorda com você em ${r.concordancia}% das ${r.revisadas} correção(ões) que você revisou`}
                      {r.revisadas > 20 && r.concordancia_recente !== null ? ` (${r.concordancia_recente}% nas últimas 20)` : ""}
                      {r.revisadas < 10 ? ". Ainda poucas para saber ao certo." : "."}
                    </span>
                  )}
                  {r && r.vies !== null && r.revisadas >= 3 && (
                    <span>
                      Seu jeito: {Math.abs(r.vies) < 5 ? "suas notas são parecidas com as da IA"
                        : `você costuma dar notas uns ${Math.abs(r.vies)}% ${r.vies < 0 ? "mais baixas" : "mais altas"} que a IA`}.
                    </span>
                  )}
                  {r && !!r.falta.length && <span>Falta: {r.falta.join(" ")}</span>}
                  {r && <Evolucao pontos={r.evolucao} />}
                </div>
                <Badge tone={r ? NIVEL[r.nivel].tone : "neutral"}>{r ? NIVEL[r.nivel].label : "Sem treino"}</Badge>
              </div>
            );
          })}
        </Card>
      )}

      <Card>
        <SectionTitle title="Ensinar a IA" />
        {materias === null ? <p className="muted">Carregando...</p> : !materias.length ? (
          <Empty title="Nenhuma matéria na escola" text="Peça ao gestor para criar a matéria. Depois você ensina a IA aqui." />
        ) : (
          <>
            <div className="form-grid">
              <label>Matéria que a IA vai aprender
                <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)}>
                  <option value="">Escolha a matéria</option>
                  {materias.map((m) => <option key={m.id} value={m.id}>{m.nome}</option>)}
                </select>
              </label>
            </div>
            <p className="rotulo-escolha">Como ensinar</p>
            <div className="botoes-escolha" role="group" aria-label="Como ensinar">
              <button aria-pressed={como === "arquivo"} className={como === "arquivo" ? "active" : ""}
                onClick={() => { setComo("arquivo"); setErro(""); }}><Upload size={14} /> Enviar arquivo</button>
              <button aria-pressed={como === "texto"} className={como === "texto" ? "active" : ""}
                onClick={() => { setComo("texto"); setErro(""); }}><PenLine size={14} /> Escrever instruções</button>
            </div>

            {como === "arquivo" && (
              <div className="form-grid">
                <label>Tipo do material
                  <select value={tipo} onChange={(e) => setTipo(e.target.value as DocumentoAPI["tipo"])}>
                    {TIPOS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </label>
                <label className="span-2">Arquivo (PDF, foto, DOCX ou TXT, até {LIMITE_MB} MB)
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg,.docx,.txt,.md"
                    onChange={(e) => {
                      const f = e.target.files?.[0] ?? null;
                      if (f && f.size > LIMITE_MB * 1024 * 1024) {
                        setArquivo(null); e.target.value = ""; setErro(`Arquivo maior que ${LIMITE_MB} MB.`);
                      } else { setArquivo(f); setErro(""); }
                    }} />
                </label>
              </div>
            )}
            {como === "texto" && (
              <>
                <label className="span-2">Como a IA deve agir nesta matéria
                  <textarea className="text-area" rows={4} maxLength={2000} value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Ex.: Sempre exijo a verificação final da conta. Não desconto ponto por erro de acentuação." />
                </label>
                <p className="tiny muted">Ideias (toque para usar):</p>
                <div className="botoes-escolha" role="group" aria-label="Exemplos de instrução">
                  {EXEMPLOS.map((e) => (
                    <button type="button" key={e} onClick={() => setTexto((t) => (t.trim() ? `${t.trim()} ${e}` : e))}>{e}</button>
                  ))}
                </div>
              </>
            )}
            {erro && <p className="error" role="alert">{erro}</p>}
            {como && (
              <Button icon={como === "arquivo" ? Upload : PenLine} disabled={salvando}
                onPress={como === "arquivo" ? enviarArquivo : salvarTexto}>
                {salvando ? "Enviando..." : como === "arquivo" ? "Enviar para a IA" : "Salvar instrução"}
              </Button>
            )}
          </>
        )}
      </Card>

      {!!materiaId && (
        <>
          {!!sugestoes.length && (
            <Card>
              <SectionTitle title="A IA sugere" />
              <p className="muted">Você mudou a nota por motivos parecidos várias vezes. Quer que a IA siga isso sempre?</p>
              {sugestoes.map((g) => (
                <div className="material-row" key={g.correcao_ids[0]}>
                  <div className="activity-icon"><Sparkles size={21} /></div>
                  <div className="activity-info">
                    <strong>{g.texto}</strong>
                    <span>Você deu esse motivo em {g.vezes} correções.</span>
                  </div>
                  <Button onPress={() => adotar(g)}>Adotar como instrução</Button>
                  <Button variant="secondary" onPress={() => dispensar(g)}>Dispensar</Button>
                </div>
              ))}
            </Card>
          )}
          {!!erros.length && (
            <Card>
              <SectionTitle title="Onde a IA mais errou" />
              <p className="muted">Correções suas em que a nota da IA ficou mais longe da sua. Bom para decidir o que ensinar.</p>
              {erros.map((e) => (
                <div className="material-row" key={e.submissao_id}>
                  <div className="activity-icon"><Sparkles size={21} /></div>
                  <div className="activity-info">
                    <strong>{e.atividade}</strong>
                    <span>
                      {e.nota_professor !== null && Math.abs(e.nota_ia - e.nota_professor) > 0.01
                        ? `IA deu ${e.nota_ia}, você deu ${e.nota_professor}.` : "Nota igual, mas você marcou a explicação como ruim."}
                      {e.motivo ? ` Motivo: ${e.motivo}` : ""}
                    </span>
                  </div>
                </div>
              ))}
            </Card>
          )}
          {!!aprendido.length && (
            <Card>
              <SectionTitle title="O que a IA aprendeu (as que ela mais errou primeiro)" />
              <p className="muted">
                "Esquecer" só faz a IA parar de usar o item nas correções. Nada é apagado: o dado continua guardado.
              </p>
              {aprendido.map((i) => (
                <div className="material-row" key={`${i.tipo}-${i.id}`} style={i.em_uso ? undefined : { opacity: 0.6 }}>
                  <div className="activity-icon">{i.tipo === "MATERIAL" ? <BookOpen size={21} /> : <Sparkles size={21} />}</div>
                  <div className="activity-info">
                    <strong>{i.titulo}</strong>
                    <span>
                      {i.tipo === "MATERIAL" ? "Material" : i.tipo === "CORRECAO" ? "Correção aprovada" : "Exercício corrigido"}
                      {i.erro > 0 ? " · a IA errou aqui" : ""}{i.em_uso ? "" : " · fora de uso"}
                    </span>
                    {!!i.trecho && <span className="tiny muted">{i.trecho}</span>}
                  </div>
                  <Button variant="secondary" onPress={() => trocarUso(i)}>{i.em_uso ? "Esquecer" : "Voltar a usar"}</Button>
                </div>
              ))}
            </Card>
          )}
          <Card>
            <SectionTitle title={`Instruções para ${nomeMateria ?? "a matéria"}`} />
            {!instrucoes.length ? (
              <Empty title="Nenhuma instrução ainda" text='Use "Escrever instruções" para dizer à IA como você quer que ela aja.' />
            ) : instrucoes.map((i) => (
              <div className="material-row" key={i.id}>
                <div className="activity-icon"><PenLine size={21} /></div>
                <div className="activity-info"><strong>{i.texto}</strong></div>
                <button className="back-link" aria-label="Apagar instrução" onClick={() => apagar(i)}><Trash2 size={16} /></button>
              </div>
            ))}
          </Card>
          <Card>
            <SectionTitle title={`Materiais enviados para ${nomeMateria ?? "a matéria"}`} />
            {!documentos.length ? (
              <Empty title="Nenhum material enviado" text="Envie apostilas, rubricas ou gabaritos para a IA aprender." />
            ) : documentos.map((d) => (
              <div className="material-row" key={d.id}>
                <div className="activity-icon"><BookOpen size={21} /></div>
                <div className="activity-info">
                  <strong>{d.nome_arquivo}</strong>
                  <span>{TIPOS.find((t) => t.value === d.tipo)?.label ?? d.tipo}</span>
                </div>
                <Badge tone={d.status_processamento === "PROCESSADO" ? "green" : "amber"}>
                  {d.status_processamento === "PROCESSADO" ? "A IA já aprendeu"
                    : d.status_processamento === "ERRO" ? d.detalhe || "A IA não conseguiu ler"
                    : "Enviado antes da IA aprender"}
                </Badge>
              </div>
            ))}
          </Card>
        </>
      )}

      <div className="info-banner">
        <Sparkles size={22} />
        <p>
          A IA também aprende sozinha com cada correção que você aprova. Quando você muda uma nota dela, pode
          explicar o motivo, e ela passa a corrigir mais parecido com você.
        </p>
      </div>
    </>
  );
}
