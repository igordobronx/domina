import { describe, expect, it } from "vitest";
import { paraStatus, paraStatusAluno } from "./atividades";

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
  it("o status do professor não muda", () =>
    expect(paraStatus("PENDENTE")).toBe("pendente"));
});
