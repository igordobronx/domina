import type { DominioAPI, EvolucaoMateriaAPI } from "./api";

// nome curto das competencias da redacao (ENEM), usado nas telas de dominio
export const HABILIDADE_NOME: Record<string, string> = {
  C1: "Norma culta",
  C2: "Compreensão do tema",
  C3: "Argumentação",
  C4: "Coesão textual",
  C5: "Proposta de intervenção",
};

export interface MateriaNoMapa {
  nome: string;
  percentual: number; // arredondado
  atividades: number; // atividades corrigidas
}
export interface SubtopicoNoMapa {
  nome: string;
  percentual: number; // arredondado
}
export interface MapaConhecimento {
  // tudo do menor % para o maior: o que precisa de mais atencao aparece primeiro
  materias: MateriaNoMapa[];
  subtopicos: Record<string, SubtopicoNoMapa[]>; // por nome da materia
}

// mesma regra da tela Minha evolucao: redacao usa as competencias C1-C5 (dominio);
// as outras materias usam os subtopicos das questoes
const ehRedacao = (materia: string) => materia.toLowerCase().startsWith("redação");

export function montarMapa(evolucao: EvolucaoMateriaAPI[], dominio: DominioAPI[]): MapaConhecimento {
  const materias = evolucao
    .map((m) => ({ nome: m.materia, percentual: Math.round(m.media_percentual), atividades: m.num_atividades }))
    .sort((a, b) => a.percentual - b.percentual || a.nome.localeCompare(b.nome));

  const subtopicos: Record<string, SubtopicoNoMapa[]> = {};
  for (const m of evolucao) {
    const subs = ehRedacao(m.materia)
      ? dominio
          .filter((d) => d.materia === m.materia && d.num_evidencias > 0)
          .map((d) => ({
            nome: `${d.habilidade_codigo} ${HABILIDADE_NOME[d.habilidade_codigo] ?? d.tema}`,
            percentual: Math.round(d.percentual_dominio),
          }))
      : (m.subtopicos ?? []).map((s) => ({ nome: s.nome, percentual: Math.round(s.percentual) }));
    subtopicos[m.materia] = subs.sort((a, b) => a.percentual - b.percentual || a.nome.localeCompare(b.nome));
  }

  return { materias, subtopicos };
}

// textos comuns da Visao geral e da Minha evolucao (as duas telas falam igual)
export const atividadesCorrigidas = (n: number) => `${n} ${n === 1 ? "atividade corrigida" : "atividades corrigidas"}`;
export const tituloSubtopicos = (materia: string) => (ehRedacao(materia) ? "Competências (C1 a C5)" : "Subtópicos");
