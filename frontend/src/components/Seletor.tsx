import { Children, Fragment, isValidElement, useEffect, useRef, useState, type ChangeEvent, type ReactNode } from "react";
import { Check, ChevronDown } from "lucide-react";

export interface OpcaoSeletor {
  valor: string;
  rotulo: string;
}

interface Base {
  opcoes: OpcaoSeletor[];
  placeholder?: string;
  rotulo?: string; // aria-label
}

// Padrao de escolha do sistema: uma lista que abre ao clicar (no lugar de botoes lado a lado).
// Nada vem pre-selecionado; no modo simples, clicar de novo na opcao marcada desmarca
// (a menos que `obrigatorio`). No modo multiplo a lista fica aberta enquanto se marca.
function Lista({ opcoes, placeholder = "Escolha...", rotulo, marcados, aoClicar, multiplo }: Base & {
  marcados: string[]; aoClicar: (valor: string) => void; multiplo: boolean;
}) {
  const [aberto, setAberto] = useState(false);
  const raiz = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!aberto) return;
    const fora = (e: MouseEvent) => { if (!raiz.current?.contains(e.target as Node)) setAberto(false); };
    document.addEventListener("mousedown", fora);
    // captura: fecha so a lista (o Esc nao chega ao pop-up por baixo)
    const esc2 = (e: KeyboardEvent) => { if (e.key === "Escape") { e.stopPropagation(); setAberto(false); } };
    document.addEventListener("keydown", esc2, true);
    return () => { document.removeEventListener("mousedown", fora); document.removeEventListener("keydown", esc2, true); };
  }, [aberto]);
  const nomes = opcoes.filter((o) => marcados.includes(o.valor)).map((o) => o.rotulo);
  return (
    <div className="seletor" ref={raiz}>
      <button type="button" className={`seletor-botao${nomes.length ? " cheio" : ""}`} aria-haspopup="listbox"
        aria-expanded={aberto} aria-label={rotulo} onClick={() => setAberto(!aberto)}>
        <span>{nomes.length ? nomes.join(", ") : placeholder}</span>
        <ChevronDown size={16} />
      </button>
      {aberto && (
        <ul className="seletor-lista" role="listbox" aria-multiselectable={multiplo}>
          {opcoes.map((o) => {
            const on = marcados.includes(o.valor);
            return (
              <li key={o.valor} role="option" aria-selected={on} className={on ? "on" : ""}
                onClick={(e) => { e.preventDefault(); aoClicar(o.valor); if (!multiplo) setAberto(false); }}>
                <span className="seletor-check">{on && <Check size={14} />}</span>{o.rotulo}
              </li>
            );
          })}
          {!opcoes.length && <li className="vazio">Nada para escolher.</li>}
        </ul>
      )}
    </div>
  );
}

export function Seletor({ valor, onChange, obrigatorio, ...base }: Base & {
  valor: string; onChange: (valor: string) => void; obrigatorio?: boolean;
}) {
  return (
    <Lista {...base} multiplo={false} marcados={valor ? [valor] : []}
      aoClicar={(v) => onChange(v === valor && !obrigatorio ? "" : v)} />
  );
}

export function SeletorMultiplo({ valores, onChange, ...base }: Base & {
  valores: string[]; onChange: (valores: string[]) => void;
}) {
  return (
    <Lista {...base} multiplo marcados={valores}
      aoClicar={(v) => onChange(valores.includes(v) ? valores.filter((x) => x !== v) : [...valores, v])} />
  );
}

// Troca direta do <select> nativo: mesmas props (value, onChange, aria-label, <option>), visual do Seletor.
// Uma <option value=""> vira o texto de "nada escolhido".
function opcoesDe(filhos: ReactNode, saida: { valor: string; rotulo: string }[] = []) {
  Children.forEach(filhos, (f) => {
    if (!isValidElement(f)) return;
    const p = f.props as { value?: string | number; children?: ReactNode };
    if (f.type === Fragment) opcoesDe(p.children, saida);
    else if (f.type === "option") {
      const rotulo = Children.toArray(p.children).join("");
      saida.push({ valor: String(p.value ?? rotulo), rotulo });
    }
  });
  return saida;
}

export function Escolha({ value, onChange, children, disabled, ...resto }: {
  value: string | number; onChange: (e: ChangeEvent<HTMLSelectElement>) => void; children: ReactNode; disabled?: boolean;
  "aria-label"?: string;
}) {
  const todas = opcoesDe(children);
  const vazia = todas.find((o) => o.valor === "");
  return (
    <div className={disabled ? "seletor-desativado" : undefined}>
      <Seletor rotulo={resto["aria-label"]} placeholder={vazia?.rotulo ?? "Escolha..."} obrigatorio
        opcoes={todas.filter((o) => o.valor !== "")} valor={String(value ?? "")}
        onChange={(v) => onChange({ target: { value: v } } as ChangeEvent<HTMLSelectElement>)} />
    </div>
  );
}
