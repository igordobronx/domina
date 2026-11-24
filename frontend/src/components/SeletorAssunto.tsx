import { useEffect, useRef, useState } from "react";
import { listarAssuntos, type AssuntoAPI } from "../services/api";

// Assunto opcional (os criados em "Treinar IA"): a IA busca primeiro nele. Sem escolha = Geral da matéria.
// Se a matéria não tem assunto nenhum, o campo nem aparece.
export function SeletorAssunto({ materiaId, value, onChange }: {
  materiaId: string; value: string; onChange: (id: string) => void;
}) {
  const [assuntos, setAssuntos] = useState<AssuntoAPI[]>([]);
  const primeira = useRef(true); // ao editar, o assunto que já estava salvo não pode ser zerado
  useEffect(() => {
    if (!primeira.current) onChange("");
    primeira.current = false;
    if (!materiaId) { setAssuntos([]); return; }
    listarAssuntos(materiaId).then(setAssuntos).catch(() => setAssuntos([]));
  }, [materiaId]);
  if (!assuntos.length) return null;
  return (
    <label>
      Assunto (opcional)
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">Geral (a matéria toda)</option>
        {assuntos.map((a) => <option key={a.id} value={a.id}>{a.nome}</option>)}
      </select>
    </label>
  );
}
