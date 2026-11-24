import { Seletor, Escolha } from "../components/Seletor";
import { useEffect, useState } from "react";
import { BookOpen, PenLine, Plus, Sparkles, Trash2, Upload } from "lucide-react";
import { Badge, Button, Card, Empty, Modal, SectionTitle } from "../components/ui";
import {
  baixarDocumento, criarAssunto, listarAssuntos, usoDoDocumento, criarInstrucao, criarMateria, dispensarSugestaoInstrucao, enviarDocumento, listarSugestoesInstrucao, excluirInstrucao, listarDocumentos, listarAprendido, listarErrosDaIA, listarInstrucoes, listarMaterias, usoDoItem,
  verMemoriaIA, type AssuntoAPI, type DocumentoAPI, type ErroDaIAAPI, type InstrucaoAPI, type ItemAprendidoAPI, type MateriaAPI, type MemoriaIAAPI, type SugestaoInstrucaoAPI,
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
  { value: "OUTRO", label: "Outros" },
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

// area da materia e as sugestoes de cada uma; o professor pode sempre digitar a dele
const AREAS_MATERIA: { value: MateriaAPI["area"]; label: string; sugestoes: string[] }[] = [
  { value: "EXATAS", label: "Exatas", sugestoes: ["Matemática", "Física", "Química"] },
  { value: "NATUREZA", label: "Natureza", sugestoes: ["Biologia", "Ciências"] },
  { value: "HUMANAS", label: "Humanas", sugestoes: ["História", "Geografia", "Filosofia", "Sociologia"] },
  { value: "LINGUAGENS", label: "Linguagens", sugestoes: ["Língua Portuguesa", "Literatura", "Redação", "Inglês", "Espanhol", "Artes", "Educação Física"] },
  { value: "REDACAO", label: "Redação", sugestoes: ["ENEM", "FUVEST", "UFG", "UEG", "UFU", "PUC", "UNIEVA"] },
  { value: "OUTRA", label: "Outra", sugestoes: [] },
];
const OUTRA_OPCAO = "__outra__";

export function TreinarIA({ notify }: { notify: (m: string) => void }) {
  const [materias, setMaterias] = useState<MateriaAPI[] | null>(null);
  const [materiaId, setMateriaId] = useState("");
  const [novaMateria, setNovaMateria] = useState(false);
  const [novaNome, setNovaNome] = useState("");
  const [novaArea, setNovaArea] = useState("");
  const [novaEscolha, setNovaEscolha] = useState(""); // sugestao da area ou OUTRA_OPCAO (digitar)
  const [como, setComo] = useState<"arquivo" | "texto" | null>(null);
  const [tipo, setTipo] = useState<DocumentoAPI["tipo"] | "">("");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [texto, setTexto] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [assuntos, setAssuntos] = useState<AssuntoAPI[]>([]);
  const [assuntoId, setAssuntoId] = useState(""); // "" = Geral (sem assunto)
  const [criandoAssunto, setCriandoAssunto] = useState(false);
  const [assuntoNovo, setAssuntoNovo] = useState("");
  const [erroAssunto, setErroAssunto] = useState("");
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
  const carregarDocumentos = () => listarDocumentos(true).then(setDocumentos).catch(() => setDocumentos([]));
  const carregarInstrucoes = (id: string) => {
    if (!id) { setInstrucoes([]); setSugestoes([]); return; }
    listarInstrucoes(id).then(setInstrucoes).catch(() => setInstrucoes([]));
    listarSugestoesInstrucao(id).then(setSugestoes).catch(() => setSugestoes([]));
  };
  const carregarMateria = (id: string) => {
    carregarDocumentos();
    carregarInstrucoes(id);
    if (!id) { setAssuntos([]); return; }
    listarAssuntos(id).then(setAssuntos).catch(() => setAssuntos([]));
    listarErrosDaIA(id).then(setErros).catch(() => setErros([]));
    listarAprendido(id).then(setAprendido).catch(() => setAprendido([]));
  };
  useEffect(() => {
    listarMaterias()
      .then((ms) => {
        setMaterias(ms);
                carregarResumo(ms);
      })
      .catch(() => { setMaterias([]); notify("Não foi possível carregar as matérias."); });
  }, []);
  useEffect(() => { setAssuntoId(""); setCriandoAssunto(false); }, [materiaId]);
  useEffect(() => carregarMateria(materiaId), [materiaId]);
  const areaNova = AREAS_MATERIA.find((a) => a.value === novaArea);
  const digitando = novaEscolha === OUTRA_OPCAO || (!!areaNova && !areaNova.sugestoes.length);
  const criarNovaMateria = () => {
    const nome = (digitando ? novaNome : novaEscolha).trim();
    if (!areaNova || !nome) return notify("Escolha a área e a matéria.");
    criarMateria({ nome, area: areaNova.value })
      .then((nova) => listarMaterias().then((ms) => {
        setMaterias(ms);
        setNovaMateria(false); setNovaNome(""); setNovaArea(""); setNovaEscolha("");
      }))
      .catch((e) => notify(e instanceof Error ? e.message : "Não foi possível criar a matéria."));
  };
  const mb = (b: number | null) => (b === null ? "" : b < 1024 * 1024 ? `${Math.max(1, Math.round(b / 1024))} KB` : `${(b / 1024 / 1024).toFixed(1)} MB`);

  const depois = (aviso: string) => {
    notify(aviso);
    setErro("");
    carregarMateria(materiaId);
    if (materias) carregarResumo(materias);
  };
  const enviarArquivo = async () => {
    if (!materiaId) return setErro("Escolha a matéria que a IA vai aprender.");
    if (!tipo) return setErro("Escolha o tipo do material.");
    if (!arquivo) return setErro("Escolha o arquivo.");
    setSalvando(true);
    try {
      const doc = await enviarDocumento(materiaId, arquivo, tipo, assuntoId || undefined);
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
      await criarInstrucao(materiaId, texto.trim(), assuntoId || undefined);
      setTexto("");
      depois(assuntoId ? "Instrução salva. A IA vai seguir sempre neste assunto." : "Instrução salva. A IA vai seguir sempre nesta matéria.");
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
  const trocarUsoMaterial = async (d: DocumentoAPI) => {
    const tirar = d.ativo !== false;
    if (tirar && !window.confirm("Tirar este material de uso? A IA para de usar, mas o arquivo continua guardado.")) return;
    try { await usoDoDocumento(d.id, !tirar); depois(tirar ? "A IA parou de usar este material (continua guardado)." : "A IA voltou a usar este material."); }
    catch (e) { notify(erroDe(e, "Não foi possível mudar.")); }
  };
  const criarNovoAssunto = async () => {
    if (!assuntoNovo.trim()) return setErroAssunto("Dê um nome para o assunto.");
    setSalvando(true);
    try {
      const novo = await criarAssunto(materiaId, assuntoNovo.trim());
      setAssuntos(await listarAssuntos(materiaId));
      setAssuntoId(novo.id);
      setCriandoAssunto(false);
      setAssuntoNovo("");
      setErroAssunto("");
      notify("Assunto criado. Envie material ou escreva instruções para ele.");
    } catch (e) { setErroAssunto(erroDe(e, "Não foi possível criar o assunto.")); }
    finally { setSalvando(false); }
  };
  const nomeAssunto = (id?: string | null) => (id ? assuntos.find((a) => a.id === id)?.nome ?? "outro assunto" : "Geral");
  const assuntoAtual = assuntos.find((a) => a.id === assuntoId);

  const nomeMateria = materias?.find((m) => m.id === materiaId)?.nome;
  const r = memoria[materiaId];
  const nada = !r || r.nivel === "SEM_TREINO";
  const instrucoesDoAssunto = instrucoes.filter((i) => (i.assunto_id ?? "") === assuntoId);
  const docsMateria = documentos.filter((d) => d.materia_id === materiaId && (d.assunto_id ?? "") === assuntoId);
  // só depois do primeiro material/instrução: sugere o que mais ajuda a IA (rubrica ou gabarito em uso)
  const falta = [...(r?.falta ?? [])];
  if (!nada && !docsMateria.some((d) => d.ativo !== false && (d.tipo === "RUBRICA" || d.tipo === "GABARITO")))
    falta.push("envie uma rubrica ou um gabarito (a IA acerta mais com eles).");

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

      {materias !== null && (
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <SectionTitle title="Matéria" />
            <Button variant="secondary" icon={Plus} onPress={() => setNovaMateria(true)}>Nova matéria</Button>
          </div>
          {materias.length ? (
            <>
              <p className="rotulo-escolha">Escolha a matéria para ver e ensinar a IA</p>
              <Seletor rotulo="Matéria" placeholder="Escolha a matéria" opcoes={materias.map((m) => ({ valor: m.id, rotulo: m.nome }))}
                valor={materiaId} onChange={setMateriaId} />
            </>
          ) : (
            <Empty title="Nenhuma matéria na escola" text="Crie a primeira com o botão acima. Depois você ensina a IA aqui." />
          )}
        </Card>
      )}

      {novaMateria && (
        <Modal title="Nova matéria" onClose={() => setNovaMateria(false)}>
          <div className="form-grid">
            <label>
              Área
              <Escolha value={novaArea} onChange={(e) => { setNovaArea(e.target.value); setNovaEscolha(""); }}>
                <option value="">Escolha a área</option>
                {AREAS_MATERIA.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
              </Escolha>
            </label>
            {!!areaNova?.sugestoes.length && (
              <label>
                {areaNova.value === "REDACAO" ? "Vestibular" : "Matéria"}
                <Escolha value={novaEscolha} onChange={(e) => setNovaEscolha(e.target.value)}>
                  <option value="">Escolha...</option>
                  {areaNova.sugestoes.map((n) => <option key={n} value={n}>{n}</option>)}
                  <option value={OUTRA_OPCAO}>{areaNova.value === "REDACAO" ? "Outro" : "Outra"}</option>
                </Escolha>
              </label>
            )}
            {!!areaNova && digitando && (
              <label>
                Nome
                <input value={novaNome} onChange={(e) => setNovaNome(e.target.value)} placeholder="Ex.: Matemática" />
              </label>
            )}
          </div>
          <div className="form-actions">
            <Button variant="secondary" onPress={() => setNovaMateria(false)}>Cancelar</Button>
            <Button onPress={criarNovaMateria}>Criar matéria</Button>
          </div>
        </Modal>
      )}

      {!!materiaId && (
        <Card>
          <SectionTitle title="Assunto" />
          <p className="rotulo-escolha">Escolha o assunto para ensinar ou crie um novo. "Geral" vale para a matéria toda.</p>
          <Seletor rotulo="Assunto" placeholder="Geral (a matéria toda)"
            opcoes={assuntos.map((a) => ({ valor: a.id, rotulo: `${a.nome}${a.da_escola ? " (escola)" : ""}` }))}
            valor={assuntoId} onChange={setAssuntoId} />
          {assuntoAtual && (
            <p className="tiny muted">{assuntoAtual.materiais} trecho(s) de material · {assuntoAtual.instrucoes} instrução(ões) · {assuntoAtual.correcoes} exemplo(s) de correção neste assunto.</p>
          )}
          {!criandoAssunto ? (
            <Button variant="secondary" icon={Plus} onPress={() => setCriandoAssunto(true)}>Novo assunto</Button>
          ) : (
            <>
              <div className="form-grid">
                <label>Nome do assunto
                  <input value={assuntoNovo} onChange={(e) => setAssuntoNovo(e.target.value)} placeholder="Ex.: Função afim" />
                </label>
              </div>
              {erroAssunto && <p className="error" role="alert">{erroAssunto}</p>}
              <div className="form-actions">
                <Button variant="secondary" onPress={() => setCriandoAssunto(false)}>Cancelar</Button>
                <Button disabled={salvando} onPress={criarNovoAssunto}>{salvando ? "Salvando..." : "Criar assunto"}</Button>
              </div>
            </>
          )}
        </Card>
      )}

      {!!materiaId && (
        <Card>
          <SectionTitle title={`O que a IA já aprendeu em ${nomeMateria ?? "a matéria"}`} />
          <div className="material-row">
            <div className="activity-icon"><Sparkles size={21} /></div>
            <div className="activity-info">
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
              {r && r.vies !== null && r.diferenca_media !== null && r.revisadas >= 3 && r.vies !== 0 && (
                // uma frase só: a média some com +10 e -10, então a diferença por correção só entra quando acrescenta algo
                <span>
                  {`Em média, suas notas ficam ${Math.abs(r.vies)}% ${r.vies < 0 ? "mais baixas" : "mais altas"} que as da IA`}
                  {r.diferenca_media >= Math.abs(r.vies) + 5 ? `, mas em cada correção a diferença costuma ser de ${r.diferenca_media}%` : ""}
                  .
                </span>
              )}
              {!!falta.length && <span>Falta: {falta.join(" ")}</span>}
              {r && <Evolucao pontos={r.evolucao} />}
            </div>
            <Badge tone={r ? NIVEL[r.nivel].tone : "neutral"}>{r ? NIVEL[r.nivel].label : "Sem treino"}</Badge>
          </div>
        </Card>
      )}

      {!!materiaId && (
      <Card>
        <SectionTitle title="Ensinar a IA" />
        {(
          <>
            <p className="rotulo-escolha">Como ensinar</p>
            <Seletor rotulo="Como ensinar" placeholder="Escolha como ensinar"
              opcoes={[{ valor: "arquivo", rotulo: "Enviar arquivo" }, { valor: "texto", rotulo: "Escrever instruções" }]}
              valor={como ?? ""} onChange={(v) => { setComo((v || null) as typeof como); setErro(""); }} />

            {como === "arquivo" && (
              <div className="form-grid">
                <label>Tipo do material
                  <Escolha value={tipo} onChange={(e) => setTipo(e.target.value as DocumentoAPI["tipo"])}>
                    <option value="">Escolha o tipo</option>
                    {TIPOS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </Escolha>
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
      )}

      {!!materiaId && (
        <Card>
          <SectionTitle title={`Materiais enviados · ${nomeAssunto(assuntoId)}`} />
          <p className="tiny muted">Tirar de uso: a IA para de usar o material e ele sai do treino, mas o arquivo continua guardado. Você pode voltar a usar quando quiser.</p>
          {!docsMateria.length ? (
            <Empty title="Nenhum material enviado" text="Envie apostilas, rubricas ou gabaritos para a IA aprender." />
          ) : docsMateria.map((d) => (
            <div className="material-row" key={d.id} style={d.ativo === false ? { opacity: 0.6 } : undefined}>
              <div className="activity-icon"><BookOpen size={21} /></div>
              <div className="activity-info">
                <strong>{d.nome_arquivo}</strong>
                <span>
                  {TIPOS.find((t) => t.value === d.tipo)?.label ?? d.tipo} · {d.materia_nome} · enviado por {d.enviado_por_nome}
                  {d.tamanho_bytes !== null ? ` · ${mb(d.tamanho_bytes)}` : ""}{d.ativo === false ? " · fora de uso" : ""}
                </span>
              </div>
              <Badge tone={d.status_processamento === "PROCESSADO" ? "green" : "amber"}>
                {d.status_processamento === "PROCESSADO" ? "A IA já aprendeu"
                  : d.status_processamento === "ERRO" ? d.detalhe || "A IA não conseguiu ler"
                  : "Enviado antes da IA aprender"}
              </Badge>
              {d.pode_baixar && (
                <Button variant="secondary" onPress={() => baixarDocumento(d.id, d.nome_arquivo).catch((e) => notify(erroDe(e, "Não foi possível baixar.")))}>Baixar</Button>
              )}
              <Button variant="secondary" onPress={() => trocarUsoMaterial(d)}>{d.ativo === false ? "Voltar a usar" : "Tirar de uso"}</Button>
            </div>
          ))}
        </Card>
      )}

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
          {(
          <Card>
            <SectionTitle title={`Instruções para ${nomeMateria ?? "a matéria"} · ${nomeAssunto(assuntoId)}`} />
            {!instrucoesDoAssunto.length ? (
              <Empty title="Nenhuma instrução ainda" text='Use "Escrever instruções" para dizer à IA como você quer que ela aja.' />
            ) : instrucoesDoAssunto.map((i) => (
              <div className="material-row" key={i.id}>
                <div className="activity-icon"><PenLine size={21} /></div>
                <div className="activity-info"><strong>{i.texto}</strong></div>
                <button className="back-link" aria-label="Apagar instrução" onClick={() => apagar(i)}><Trash2 size={16} /></button>
              </div>
            ))}
          </Card>
          )}
        </>
      )}

      {!!materiaId && (
        <>
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
                  <div className="activity-icon"><Sparkles size={21} /></div>
                  <div className="activity-info">
                    <strong>{i.titulo}</strong>
                    <span>
                      {i.tipo === "CORRECAO" ? "Correção aprovada" : "Exercício corrigido"}
                      {i.erro > 0 ? " · a IA errou aqui" : ""}{i.em_uso ? "" : " · fora de uso"}
                    </span>
                    {!!i.trecho && <span className="tiny muted">{i.trecho}</span>}
                  </div>
                  <Button variant="secondary" onPress={() => trocarUso(i)}>{i.em_uso ? "Esquecer" : "Voltar a usar"}</Button>
                </div>
              ))}
            </Card>
          )}
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
