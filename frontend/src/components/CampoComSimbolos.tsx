import { createContext, useContext, useRef, useState, type ChangeEvent, type ReactNode } from "react";

// Simbolos Unicode (nao LaTeX): funcionam no banco, na correcao pelo Gemini e nas telas, sem biblioteca.
export const GRUPOS_SIMBOLOS: Record<string, string[]> = {
  Matemática: [..."√∛∑∫∞π±×÷≤≥≠≈", ..."²³ⁿ½¼¾", ..."∠⊥∥∈∉∪∩⊂∅", "ₙ", "ₓ", "°", "′", "″", "‰", "∴"],
  Física: [..."ΔμλωθρΩπαβγ", "→", "°", "·", "×", "²", "³", "√", "≈", "±", "∝", "⁻", "¹", "₀", "₁", "₂", "Σ", "∞", "≤", "≥"],
  Química: [..."₀₁₂₃₄₅₆₇₈₉", ..."⁺⁻²³", "→", "⇌", "⇄", "↑", "↓", "Δ", "°", "·", "⁰", "¹", "⁴", "⁵"],
  Grego: [..."αβγδεθλμνρσφψωΔΣΩΦΨ"],
};

// a barra ja abre nos simbolos da materia (pelo nome, pois o tipo da materia nao diz se e fisica ou quimica)
export function grupoDaMateria(nome?: string): string {
  const n = (nome ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  if (n.includes("fisica")) return "Física";
  if (n.includes("quimica")) return "Química";
  return "Matemática";
}

// texto novo e posicao do cursor depois de inserir o simbolo no lugar da selecao
export function inserirNoCursor(valor: string, ini: number, fim: number, simbolo: string) {
  return { texto: valor.slice(0, ini) + simbolo + valor.slice(fim), cursor: ini + simbolo.length };
}

// barra unica (tela do professor): guarda o "inserir" do ultimo campo focado
type Inserir = (simbolo: string) => void;
const BarraContexto = createContext<{ current: Inserir | null } | null>(null);

type Props = {
  value: string;
  onChange: (e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => void;
  linha?: boolean; // campo de uma linha so (ex.: alternativa), em vez de textarea
  placeholder?: string;
  rows?: number;
  className?: string;
  "aria-label"?: string;
};

function PainelSimbolos({ grupoInicial, onSimbolo }: { grupoInicial: string; onSimbolo: Inserir }) {
  const [grupo, setGrupo] = useState(grupoInicial);
  return (
    <div className="simbolos-painel">
      <div className="tabs" role="group" aria-label="Grupos de símbolos">
        {Object.keys(GRUPOS_SIMBOLOS).map((g) => (
          <button type="button" key={g} className={g === grupo ? "active" : ""} aria-pressed={g === grupo} onClick={() => setGrupo(g)}>
            {g}
          </button>
        ))}
      </div>
      <div className="simbolos-lista">
        {GRUPOS_SIMBOLOS[grupo].map((s, i) => (
          <button
            type="button"
            key={`${s}${i}`}
            aria-label={`Inserir ${s}`}
            onMouseDown={(e) => e.preventDefault()} // nao tira o foco nem a selecao do campo
            onClick={() => onSimbolo(s)}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

// Barra de simbolos unica, sempre a mostra, para varios CampoComSimbolos dentro dela: o clique
// insere no campo onde o cursor esta (o ultimo focado). Os campos de dentro escondem o proprio botao.
export function ComBarraSimbolos({ materia, children }: { materia?: string; children: ReactNode }) {
  const ultimo = useRef<Inserir | null>(null);
  return (
    <BarraContexto.Provider value={ultimo}>
      <div className="barra-simbolos" role="toolbar" aria-label="Símbolos">
        <span className="tiny muted">Símbolos: clique para inserir onde está o cursor</span>
        {/* key: trocar a materia reabre a barra no grupo dela */}
        <PainelSimbolos key={grupoDaMateria(materia)} grupoInicial={grupoDaMateria(materia)} onSimbolo={(s) => ultimo.current?.(s)} />
      </div>
      {children}
    </BarraContexto.Provider>
  );
}

// Campo de texto com simbolos: o clique insere o simbolo NA POSICAO DO CURSOR (nao no fim).
// Mesma interface de um <textarea>/<input>, entao e so trocar a tag onde precisar.
// Fora de uma ComBarraSimbolos, cada campo tem o proprio botao "Ω Símbolos" (telas do aluno).
export function CampoComSimbolos({ value, onChange, linha, ...resto }: Props) {
  const ref = useRef<HTMLTextAreaElement & HTMLInputElement>(null);
  const barra = useContext(BarraContexto);
  const [aberto, setAberto] = useState(false);

  const inserir = (simbolo: string) => {
    const el = ref.current;
    const ini = el?.selectionStart ?? value.length;
    const fim = el?.selectionEnd ?? value.length;
    const { texto, cursor } = inserirNoCursor(value, ini, fim, simbolo);
    // passa um "evento" com o novo texto: quem usa so le e.target.value
    onChange({ target: { value: texto } } as ChangeEvent<HTMLTextAreaElement>);
    requestAnimationFrame(() => {
      el?.focus();
      el?.setSelectionRange(cursor, cursor);
    });
  };

  // a barra chama sempre o "inserir" mais novo (com o texto atual), nao o do momento do foco
  const inserirAtual = useRef(inserir);
  inserirAtual.current = inserir;
  const comum = {
    ref,
    value,
    onChange,
    // na barra unica, o campo focado passa a receber os simbolos
    onFocus: barra ? () => { barra.current = (s: string) => inserirAtual.current(s); } : undefined,
    ...resto,
  };

  if (barra) return linha ? <input {...comum} /> : <textarea {...comum} />;
  return (
    <div className="campo-simbolos">
      {linha ? <input {...comum} /> : <textarea {...comum} />}
      <button type="button" className="simbolos-toggle" aria-expanded={aberto} onClick={() => setAberto(!aberto)}>
        Ω Símbolos
      </button>
      {aberto && <PainelSimbolos grupoInicial="Química" onSimbolo={inserir} />}
    </div>
  );
}
