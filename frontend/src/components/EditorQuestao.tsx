import { Check, CircleCheck, Plus, Sparkles, X } from "lucide-react";
import { Button } from "./ui";
import { CampoComSimbolos } from "./CampoComSimbolos";
import type { TipoExercicioAPI } from "../services/api";

// Editor de UMA questao (enunciado + alternativas ou respostas de exemplo): o mesmo em Exercicios e em Atividades.
export const LETRAS = "ABCDEF";
export const MAX_EXEMPLOS = 5;

export type Rascunho = {
  tipo: TipoExercicioAPI;
  enunciado: string;
  alternativas: string[];
  correta: number | null;
  respostasExemplo: string[]; // discursivo: uma ou mais respostas de exemplo
  explicacao: string;
  daIA: boolean; // veio de uma sugestao da IA
  respostaIA: boolean; // a resposta de exemplo (discursivo) foi sugerida pela IA
};

export const vazio: Rascunho = {
  tipo: "OBJETIVO", enunciado: "", alternativas: ["", "", "", ""], correta: null,
  respostasExemplo: [""], explicacao: "", daIA: false, respostaIA: false,
};

export function EditorQuestao({ r, setR, sugerindoResposta, onSugerirResposta, comExplicacao = true }: {
  r: Rascunho;
  setR: (r: Rascunho) => void;
  sugerindoResposta: boolean;
  onSugerirResposta: () => void;
  comExplicacao?: boolean; // exercicio tem explicacao; atividade nao
}) {
  const alts = r.alternativas;
  const setAlt = (k: number, v: string) => setR({ ...r, alternativas: alts.map((x, j) => (j === k ? v : x)) });
  // tirar uma do meio: as de baixo sobem uma letra, e a marcada como correta acompanha
  const removerAlt = (k: number) => setR({
    ...r, alternativas: alts.filter((_, j) => j !== k),
    correta: r.correta === null || r.correta === k ? null : r.correta > k ? r.correta - 1 : r.correta,
  });

  return (
  <div className="form-grid ex-form">
  <label className="span-2">Enunciado
    <CampoComSimbolos rows={4} value={r.enunciado} onChange={(e) => setR({ ...r, enunciado: e.target.value })}
      placeholder="A pergunta, com o contexto que o aluno precisa" />
  </label>
  {r.tipo === "OBJETIVO" ? (
    <fieldset className="alternativas-form span-2">
              <legend>Alternativas</legend>
      {alts.map((texto, k) => (
        <div key={k} className={`alternativa-linha ${r.correta === k ? "certa" : ""}`}>
          <div className="alternativa">
            <b>{LETRAS[k]})</b>
            <CampoComSimbolos linha value={texto} placeholder={`Alternativa ${LETRAS[k]}`}
              aria-label={`Alternativa ${LETRAS[k]}`} onChange={(e) => setAlt(k, e.target.value)} />
          </div>
          <div className="alternativa-acoes">
            {r.correta === k ? (
              <span className="marcada-correta"><CircleCheck size={16} /> Esta é a correta</span>
            ) : (
              <button type="button" className="botao-pequeno" onClick={() => setR({ ...r, correta: k })}>
                <Check size={14} /> Marcar esta como correta
              </button>
            )}
            {alts.length > 2 && (
              <button type="button" className="botao-pequeno perigo" aria-label={`Remover alternativa ${LETRAS[k]}`}
                onClick={() => removerAlt(k)}>
                <X size={14} /> Remover alternativa
              </button>
            )}
          </div>
        </div>
      ))}
      {alts.length < LETRAS.length && (
        <div className="form-actions left">
          <Button variant="ghost" icon={Plus} onPress={() => setR({ ...r, alternativas: [...alts, ""] })}>
            Adicionar alternativa ({LETRAS[alts.length]})
          </Button>
        </div>
      )}
    </fieldset>
  ) : (
    <>
      <fieldset className="span-2 exemplos-form">
        <legend>Respostas de exemplo (o aluno compara com a dele depois de responder)</legend>
        {r.respostasExemplo.map((texto, k) => (
          <div key={k} className="alternativa-linha">
            <label>
              {r.respostasExemplo.length > 1 ? `Resposta de exemplo ${k + 1}` : "Resposta de exemplo"}
              <CampoComSimbolos rows={4} value={texto}
                onChange={(e) => setR({ ...r, respostasExemplo: r.respostasExemplo.map((x, j) => (j === k ? e.target.value : x)) })}
                placeholder={k === 0 ? "Escreva a resposta esperada, ou peça para a IA sugerir" : "Outra forma certa de responder"} />
            </label>
            {r.respostasExemplo.length > 1 && (
              <div className="alternativa-acoes">
                <button type="button" className="botao-pequeno perigo"
                  onClick={() => setR({ ...r, respostasExemplo: r.respostasExemplo.filter((_, j) => j !== k) })}>
                  <X size={14} /> Remover esta resposta
                </button>
              </div>
            )}
          </div>
        ))}
        <div className="form-actions left">
          {r.respostasExemplo.length < MAX_EXEMPLOS && (
            <Button variant="ghost" icon={Plus} onPress={() => setR({ ...r, respostasExemplo: [...r.respostasExemplo, ""] })}>
              Adicionar outra resposta de exemplo
            </Button>
          )}
          <Button variant="secondary" icon={Sparkles} disabled={sugerindoResposta} onPress={onSugerirResposta}>
            {sugerindoResposta ? "A IA está escrevendo..." : "IA sugere uma resposta"}
          </Button>
        </div>
      </fieldset>
    </>
  )}
  {comExplicacao && (
    <label className="span-2">Explicação (opcional: aparece para o aluno depois que ele responde)
      <textarea rows={2} value={r.explicacao} onChange={(e) => setR({ ...r, explicacao: e.target.value })} />
    </label>
  )}
  </div>
  );
}
