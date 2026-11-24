import { useState } from "react";
import { SlidersHorizontal } from "lucide-react";
import { Seletor, SeletorMultiplo } from "./Seletor";

interface BaseGrupo {
  id: string;
  titulo: string; // "Turma", "Status"...
  opcoes: { valor: string; rotulo: string }[];
}
// "" (ou lista vazia) = sem filtro (nada pre-selecionado); `multiplo` deixa marcar varias opcoes
export type GrupoFiltro = BaseGrupo & (
  | { multiplo?: false; valor: string; onChange: (valor: string) => void }
  | { multiplo: true; valor: string[]; onChange: (valor: string[]) => void }
);

// Padrao de filtros do sistema: a lista aparece inteira e o botao "Filtros" abre um painel com um
// grupo por assunto (turma, status, materia...). Clicar de novo numa opcao marcada desmarca.
export function Filtros({ grupos }: { grupos: GrupoFiltro[] }) {
  const [aberto, setAberto] = useState(false);
  const ativos = grupos.filter((g) => g.valor.length).length;
  if (!grupos.length) return null;
  return (
    <div className="filtros">
      <button type="button" className={`filtros-botao${ativos ? " ativo" : ""}`} aria-expanded={aberto}
        onClick={() => setAberto(!aberto)}>
        <SlidersHorizontal size={16} /> Filtros{ativos ? ` (${ativos})` : ""}
      </button>
      {aberto && (
        <div className="filtros-painel">
          {grupos.map((g) => (
            <div key={g.id}>
              <p className="rotulo-escolha">{g.titulo}</p>
              {g.multiplo ? (
                <SeletorMultiplo todos="Selecionar todos" rotulo={`Filtrar por ${g.titulo.toLowerCase()}`} placeholder="Todos" opcoes={g.opcoes}
                  valores={g.valor} onChange={g.onChange} />
              ) : (
                <Seletor rotulo={`Filtrar por ${g.titulo.toLowerCase()}`} placeholder="Todos" opcoes={g.opcoes}
                  valor={g.valor} onChange={g.onChange} />
              )}
            </div>
          ))}
          {ativos > 0 && (
            <button type="button" className="botao-pequeno" onClick={() => grupos.forEach((g) => (g.multiplo ? g.onChange([]) : g.onChange("")))}>
              Limpar filtros
            </button>
          )}
        </div>
      )}
    </div>
  );
}
