import { useRef, useState, type ChangeEvent } from "react";

// Simbolos Unicode (nao LaTeX): funcionam no banco, na correcao pelo Gemini e nas telas, sem biblioteca.
const GRUPOS: Record<string, string[]> = {
  Química: [..."₀₁₂₃₄₅₆₇₈₉", ..."⁺⁻²³", "→", "⇌", "⇄", "↑", "↓", "Δ", "°", "·", "⁰", "¹", "⁴", "⁵"],
  Matemática: [..."√∛∑∫∞π±×÷≤≥≠≈", ..."²³ⁿ½¼¾", ..."∠⊥∥∈∉∪∩⊂∅", "ₙ", "ₓ", "°", "′", "″", "‰", "∴"],
  Grego: [..."αβγδεθλμνρσφψωΔΣΩΦΨ"],
};

// texto novo e posicao do cursor depois de inserir o simbolo no lugar da selecao
export function inserirNoCursor(valor: string, ini: number, fim: number, simbolo: string) {
  return { texto: valor.slice(0, ini) + simbolo + valor.slice(fim), cursor: ini + simbolo.length };
}

type Props = {
  value: string;
  onChange: (e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => void;
  linha?: boolean; // campo de uma linha so (ex.: alternativa), em vez de textarea
  placeholder?: string;
  rows?: number;
  className?: string;
  "aria-label"?: string;
};

// Campo de texto com uma barra de simbolos: o clique insere o simbolo NA POSICAO DO CURSOR (nao no fim).
// Mesma interface de um <textarea>/<input>, entao e so trocar a tag onde precisar.
export function CampoComSimbolos({ value, onChange, linha, ...resto }: Props) {
  const ref = useRef<HTMLTextAreaElement & HTMLInputElement>(null);
  const [aberto, setAberto] = useState(false);
  const [grupo, setGrupo] = useState("Química");

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

  const comum = { ref, value, onChange, ...resto };
  return (
    <div className="campo-simbolos">
      {linha ? <input {...comum} /> : <textarea {...comum} />}
      <button type="button" className="simbolos-toggle" aria-expanded={aberto} onClick={() => setAberto(!aberto)}>
        Ω Símbolos
      </button>
      {aberto && (
        <div className="simbolos-painel">
          <div className="tabs" role="group" aria-label="Grupos de símbolos">
            {Object.keys(GRUPOS).map((g) => (
              <button type="button" key={g} className={g === grupo ? "active" : ""} aria-pressed={g === grupo} onClick={() => setGrupo(g)}>
                {g}
              </button>
            ))}
          </div>
          <div className="simbolos-lista">
            {GRUPOS[grupo].map((s, i) => (
              <button
                type="button"
                key={`${s}${i}`}
                aria-label={`Inserir ${s}`}
                onMouseDown={(e) => e.preventDefault()} // nao tira o foco nem a selecao do campo
                onClick={() => inserir(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
