import { describe, expect, it } from "vitest";
import { inserirNoCursor } from "./CampoComSimbolos";

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
