import { useCallback, useEffect, useState } from "react";
import { listarCalendario, type ItemCalendarioAPI } from "../services/api";

const SEGUNDOS = 45;
export const iso = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

/** Itens do calendario entre `de` e `ate`. Recarrega sozinho a cada 45 s e ao voltar para a aba:
 *  e assim que um evento criado por outra conta aparece aqui (polling, sem WebSocket). */
export function useCalendario(de: string, ate: string, escolaId?: string) {
  const [itens, setItens] = useState<ItemCalendarioAPI[]>([]);
  const [erro, setErro] = useState("");
  const recarregar = useCallback(() => {
    listarCalendario(de, ate, escolaId)
      .then((r) => { setItens(r); setErro(""); })
      .catch((e: Error) => setErro(e.message));
  }, [de, ate, escolaId]);

  useEffect(() => {
    recarregar();
    const t = setInterval(recarregar, SEGUNDOS * 1000);
    const aoVoltar = () => document.visibilityState === "visible" && recarregar();
    document.addEventListener("visibilitychange", aoVoltar);
    return () => { clearInterval(t); document.removeEventListener("visibilitychange", aoVoltar); };
  }, [recarregar]);

  return { itens, erro, recarregar };
}
