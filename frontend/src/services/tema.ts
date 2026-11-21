// Tema claro/escuro. A escolha fica neste navegador (cada pessoa escolhe o seu), sem passar pelo servidor.
// "auto" segue o sistema (celular/computador). O CSS so olha para html[data-theme="escuro"].
export type Tema = "auto" | "claro" | "escuro";

const CHAVE = "domina.tema";
const sistema = typeof window !== "undefined" && window.matchMedia
  ? window.matchMedia("(prefers-color-scheme: dark)")
  : null;

export function lerTema(): Tema {
  try {
    const t = localStorage.getItem(CHAVE);
    return t === "claro" || t === "escuro" ? t : "auto";
  } catch {
    return "auto";
  }
}

export function aplicarTema(tema: Tema = lerTema()) {
  const escuro = tema === "escuro" || (tema === "auto" && !!sistema?.matches);
  document.documentElement.dataset.theme = escuro ? "escuro" : "claro";
  // cor da barra do navegador/celular acompanha o fundo
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", escuro ? "#10141f" : "#141A2E");
}

export function salvarTema(tema: Tema) {
  try {
    localStorage.setItem(CHAVE, tema);
  } catch {
    /* sem storage: vale so ate fechar a aba */
  }
  aplicarTema(tema);
}

// no "auto", trocar o tema do sistema troca o do site na hora
sistema?.addEventListener("change", () => aplicarTema());
