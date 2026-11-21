import { describe, expect, it } from "vitest";
import { paraStatusAluno, paraStatusRevisao } from "./atividades";

describe("Status do aluno", () => {
  it("enviada sem correção fica 'pendente' (Enviada)", () =>
    expect(paraStatusAluno("AGUARDANDO_CORRECAO", false)).toBe("pendente"));
  it("com correção da IA vira 'corrigida_ia'", () => {
    expect(paraStatusAluno("PENDENTE", true)).toBe("corrigida_ia");
    expect(paraStatusAluno("REQUER_ATENCAO", true)).toBe("corrigida_ia");
  });
  it("sem notas da IA continua 'pendente' mesmo com REQUER_ATENCAO", () =>
    expect(paraStatusAluno("REQUER_ATENCAO", false)).toBe("pendente"));
  it("aprovada pelo professor (ou prova objetiva) é 'aprovada'", () =>
    expect(paraStatusAluno("APROVADA", true)).toBe("aprovada"));
});

describe("Status na fila do professor", () => {
  it("separa enviada, corrigida pela IA e corrigida", () => {
    expect(paraStatusRevisao("AGUARDANDO_CORRECAO")).toBe("pendente");
    expect(paraStatusRevisao("PENDENTE")).toBe("corrigida_ia");
    expect(paraStatusRevisao("REQUER_ATENCAO")).toBe("corrigida_ia");
    expect(paraStatusRevisao("APROVADA")).toBe("aprovada");
  });
});
