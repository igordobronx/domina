import { dominioMeu, type DominioAPI } from "./api";

export interface Recomendacao {
  habilidadeCodigo: string;
  tema: string;
  percentual: number;
}

// regra simples (MVP): recomenda a competencia com menor dominio ja observado.
// so considera temas com pelo menos 1 evidencia (ja apareceram numa correcao aprovada).
export function recomendar(dominio: DominioAPI[]): Recomendacao | null {
  const comEvidencia = dominio.filter((d) => d.num_evidencias > 0);
  if (!comEvidencia.length) return null;
  const pior = comEvidencia.reduce((a, b) => (b.percentual_dominio < a.percentual_dominio ? b : a));
  return {
    habilidadeCodigo: pior.habilidade_codigo,
    tema: pior.tema,
    percentual: Math.round(pior.percentual_dominio),
  };
}

export async function carregarDominioReal(): Promise<{ dominio: DominioAPI[]; recomendacao: Recomendacao | null }> {
  const dominio = await dominioMeu();
  return { dominio, recomendacao: recomendar(dominio) };
}
