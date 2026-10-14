import { describe, expect, it } from "vitest";
import { approveActivity, validScores, visibleResult } from "./demoStore";
import { initialActivities } from "../data/demo";
import { readRoute } from "./navigation";
describe("Revisão humana", () => {
  it("esconde o resultado pendente do aluno", () =>
    expect(visibleResult(initialActivities[2], "aluno")).toBe(false));
  it("permite revisar e mantém a sugestão original separada da nota final", () => {
    const result = approveActivity(
      initialActivities[2],
      [200, 200, 180, 180, 200],
      "Boa argumentação. Revise a coesão.",
    );
    expect(result.aiScores).toEqual(initialActivities[2].aiScores);
    expect(result.scores).toEqual([200, 200, 180, 180, 200]);
    expect(visibleResult(result, "aluno")).toBe(true);
    expect(initialActivities[2].status).toBe("pendente");
  });
  it("rejeita nota inválida e feedback vazio", () => {
    expect(() =>
      approveActivity(
        initialActivities[2],
        [160, 160, 120, 140, 250],
        "Feedback",
      ),
    ).toThrow();
    expect(() =>
      approveActivity(initialActivities[2], [160, 160, 120, 140, 160], "   "),
    ).toThrow();
    expect(validScores([160, 160, 125, 140, 160])).toBe(false);
  });
  it("usa a escala separada de matemática", () => {
    expect(validScores([8], "matematica")).toBe(true);
    expect(validScores([11], "matematica")).toBe(false);
  });
});
describe("Navegação", () => {
  it("restaura um link de atividade", () =>
    expect(readRoute("#aluno/atividades/a1")).toMatchObject({
      role: "aluno",
      page: "atividades",
      activity: "a1",
    }));
  it("não abre a revisão por um link do gestor", () =>
    expect(readRoute("#gestor/revisoes/a1")).toMatchObject({
      role: "gestor",
      page: "inicio",
      activity: null,
    }));
});
