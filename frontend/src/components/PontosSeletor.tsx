import { useState } from "react";
import { Seletor } from "./Seletor";

const OUTRO = "__outro__";

// Pontos em lista que abre ao clicar; "Outro" abre um campo para digitar. O valor sai como texto ("" = nada escolhido).
export function PontosSeletor({ rotulo, valor, onChange, opcoes, placeholder = "Escolha os pontos" }: {
  rotulo: string; valor: string; onChange: (v: string) => void; opcoes: string[]; placeholder?: string;
}) {
  const [outro, setOutro] = useState(false);
  const digitando = outro || (!!valor && !opcoes.includes(valor));
  return (
    <div className="pontos-seletor">
      <Seletor rotulo={rotulo} placeholder={placeholder}
        opcoes={[...opcoes.map((o) => ({ valor: o, rotulo: o })), { valor: OUTRO, rotulo: "Outro" }]}
        valor={digitando ? OUTRO : valor}
        onChange={(v) => {
          if (v === OUTRO) { setOutro(true); onChange(""); } else { setOutro(false); onChange(v); }
        }} />
      {digitando && (
        <input type="number" min={0.5} step={0.5} aria-label={`${rotulo} (digite)`} value={valor} placeholder="Digite os pontos"
          onChange={(e) => onChange(e.target.value)} />
      )}
    </div>
  );
}
