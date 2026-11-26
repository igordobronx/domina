import { describe, expect, it } from "vitest";
import type { DominioAPI, EvolucaoMateriaAPI } from "./api";
import { atividadesCorrigidas, montarMapa, tituloSubtopicos } from "./mapaConhecimento";

const ev = (materia: string, pct: number, subs: [string, number][] = [], num = 1): EvolucaoMateriaAPI => ({
  materia_id: materia,
  materia,
  media_percentual: pct,
  num_atividades: num,
  historico: [],
  subtopicos: subs.map(([nome, percentual]) => ({ nome, percentual, num_questoes: 1 })),
});
const dom = (codigo: string, pct: number, evid = 1, materia = "Redação ENEM"): DominioAPI => ({
  tema_id: codigo,
  tema: `Tema ${codigo}`,
  materia,
  habilidade_codigo: codigo,
  percentual_dominio: pct,
  num_evidencias: evid,
});

describe("Mapa de conhecimento do aluno", () => {
  const evolucao = [
    ev("Redação ENEM", 70),
    ev("Matemática", 75, [["Geometria plana", 50], ["Função afim", 100]], 2),
    ev("Física", 66.7, [["Cinemática", 100], ["Dinâmica", 0]]),
  ];
  const dominio = [dom("C1", 80), dom("C4", 30), dom("C2", 60, 0)];

  it("lista só as matérias, do maior % para o menor, arredondado", () => {
    const m = montarMapa(evolucao, dominio);
    expect(m.materias.map((x) => [x.nome, x.percentual])).toEqual([
      ["Matemática", 75],
      ["Redação ENEM", 70],
      ["Física", 67],
    ]);
    expect(m.materias[0].atividades).toBe(2);
  });

  it("a aba que abre primeiro é a matéria de menor %", () => {
    expect(montarMapa(evolucao, dominio).inicial).toBe("Física");
  });

  it("exatas: subtópicos das questões, do menor % para o maior", () => {
    const m = montarMapa(evolucao, dominio);
    expect(m.subtopicos["Matemática"].map((s) => [s.nome, s.percentual])).toEqual([
      ["Geometria plana", 50],
      ["Função afim", 100],
    ]);
  });

  it("redação: competências com evidência, com nome curto", () => {
    const m = montarMapa(evolucao, dominio);
    expect(m.subtopicos["Redação ENEM"].map((s) => [s.nome, s.percentual])).toEqual([
      ["C4 Coesão textual", 30],
      ["C1 Norma culta", 80],
    ]);
  });

  it("sem nada corrigido, o mapa vem vazio", () => {
    const m = montarMapa([], []);
    expect(m.materias).toEqual([]);
    expect(m.inicial).toBeNull();
  });
});

describe("Textos comuns da Visão geral e da Minha evolução", () => {
  it("singular e plural de atividades corrigidas", () => {
    expect(atividadesCorrigidas(1)).toBe("1 atividade corrigida");
    expect(atividadesCorrigidas(3)).toBe("3 atividades corrigidas");
    expect(atividadesCorrigidas(0)).toBe("0 atividades corrigidas");
  });
  it("redação mostra competências; as outras, subtópicos", () => {
    expect(tituloSubtopicos("Redação ENEM")).toBe("Competências (C1 a C5)");
    expect(tituloSubtopicos("Física")).toBe("Subtópicos");
  });
});
