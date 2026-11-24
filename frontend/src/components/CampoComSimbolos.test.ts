import { describe, expect, it } from "vitest";
import { GRUPOS_SIMBOLOS, grupoDaMateria, inserirNoCursor } from "./CampoComSimbolos";

describe("inserirNoCursor", () => {
  it("insere no meio, na posição do cursor", () => {
    expect(inserirNoCursor("H2O", 1, 1, "₂")).toEqual({ texto: "H₂2O", cursor: 2 });
  });
  it("substitui o trecho selecionado", () => {
    expect(inserirNoCursor("x2", 1, 2, "²")).toEqual({ texto: "x²", cursor: 2 });
  });
  it("no fim e em campo vazio", () => {
    expect(inserirNoCursor("a", 1, 1, "→").texto).toBe("a→");
    expect(inserirNoCursor("", 0, 0, "√").texto).toBe("√");
  });
});

describe("grupoDaMateria", () => {
  it("escolhe o grupo de símbolos pelo nome da matéria", () => {
    expect(grupoDaMateria("Matemática")).toBe("Matemática");
    expect(grupoDaMateria("matematica financeira")).toBe("Matemática");
    expect(grupoDaMateria("Física")).toBe("Física");
    expect(grupoDaMateria("FISICA 2")).toBe("Física");
    expect(grupoDaMateria("Química")).toBe("Química");
  });
  it("matéria desconhecida ou vazia abre em Matemática", () => {
    expect(grupoDaMateria("Biologia")).toBe("Matemática");
    expect(grupoDaMateria(undefined)).toBe("Matemática");
  });
  it("o grupo Física existe e tem símbolos de física", () => {
    expect(GRUPOS_SIMBOLOS["Física"]).toEqual(expect.arrayContaining(["Δ", "μ", "λ", "ω", "°"]));
  });
});
