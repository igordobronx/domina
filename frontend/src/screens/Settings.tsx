import { useState } from "react";
import { Download, RotateCcw, Save } from "lucide-react";
import type { DemoState } from "../types";
import { Button, Card, SectionTitle } from "../components/ui";
import { initialState } from "../data/demo";

export function Settings({
  state,
  update,
  notify,
  onInstall,
}: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  notify: (s: string) => void;
  onInstall: () => void;
}) {
  const [name, setName] = useState(state.name),
    [goal, setGoal] = useState(state.goal),
    [confirm, setConfirm] = useState(false),
    [error, setError] = useState("");
  const exportData = () => {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(state, null, 2)], { type: "application/json" }),
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = "domina-dados-demonstrativos.json";
    a.click();
    URL.revokeObjectURL(url);
    notify("Dados demonstrativos exportados.");
  };
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">DO SEU JEITO</div>
          <h1>Preferências</h1>
          <p>Ajuste seu espaço e seu ritmo de estudo.</p>
        </div>
      </div>
      <Card>
        <SectionTitle title="Seu perfil de demonstração" />
        <div className="form-grid">
          <label>
            Nome do aluno
            <input
              value={name}
              maxLength={60}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
          <label>
            Meta semanal de práticas
            <select
              value={goal}
              onChange={(e) => setGoal(Number(e.target.value))}
            >
              {[2, 3, 4, 5, 6, 7].map((n) => (
                <option key={n} value={n}>
                  {n} práticas por semana
                </option>
              ))}
            </select>
          </label>
        </div>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <Button
          icon={Save}
          onPress={() => {
            if (!name.trim()) {
              setError("Digite um nome para continuar.");
              return;
            }
            update((s) => ({ ...s, name: name.trim(), goal }));
            setError("");
            notify("Preferências salvas neste navegador.");
          }}
        >
          Salvar preferências
        </Button>
      </Card>
      <Card>
        <SectionTitle title="Aplicativo e dados locais" />
        <p>
          Os dados deste protótipo ficam somente neste navegador. Não use
          informações pessoais reais.
        </p>
        <div className="form-actions left">
          <Button variant="secondary" icon={Download} onPress={onInstall}>
            Como instalar o Domina
          </Button>
          <Button variant="secondary" icon={Download} onPress={exportData}>
            Exportar demonstração
          </Button>
          <Button
            variant="ghost"
            icon={RotateCcw}
            onPress={() => setConfirm(true)}
          >
            Restaurar demonstração
          </Button>
        </div>
        {confirm && (
          <div className="confirmation">
            <strong>Restaurar os dados de exemplo?</strong>
            <p>
              Os envios, rascunhos e alterações locais serão removidos. Exporte
              antes se quiser guardá-los.
            </p>
            <div className="form-actions">
              <Button variant="secondary" onPress={() => setConfirm(false)}>
                Cancelar
              </Button>
              <Button
                onPress={() => {
                  update(() => structuredClone(initialState));
                  setName(initialState.name);
                  setGoal(initialState.goal);
                  setConfirm(false);
                  notify("Demonstração restaurada.");
                }}
              >
                Confirmar restauração
              </Button>
            </div>
          </div>
        )}
      </Card>
    </>
  );
}
export function Help() {
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">PODE CONTAR COM A GENTE</div>
          <h1>Um pouco de orientação.</h1>
          <p>Respostas simples para continuar com confiança.</p>
        </div>
      </div>
      <Card>
        {[
          [
            "Como funciona a correção?",
            "Você envia uma atividade, a IA sugere uma correção e seu professor revisa. A nota e o feedback só aparecem para você depois da aprovação. Neste protótipo, as sugestões são exemplos fixos.",
          ],
          [
            "Como testar o fluxo completo?",
            "Abra Atividades no perfil Aluno, envie uma resposta e troque para Professor no seletor da barra superior. Em Revisões, abra a atividade, ajuste as notas, escreva um feedback e aprove. Volte ao perfil Aluno para ver o resultado.",
          ],
          [
            "O que significa meu percentual de domínio?",
            "É uma estimativa de aprendizagem por tema, baseada em evidências. Não é uma nota oficial. Os valores e gráficos desta demonstração são ilustrativos e não são recalculados pelos seus envios.",
          ],
          [
            "Meu rascunho fica salvo?",
            "Sim, o texto é salvo automaticamente neste navegador quando o armazenamento está disponível. Os arquivos escolhidos não são armazenados; apenas seus nomes são registrados ao enviar.",
          ],
          [
            "Posso usar no celular?",
            "Sim. O layout se adapta ao celular. Na página inicial, use Instalar app. No iPhone, abra no Safari e procure Compartilhar → Adicionar à Tela de Início.",
          ],
          [
            "Funciona sem internet?",
            "Após uma primeira visita à versão de produção, a interface e os exemplos podem funcionar offline. Esta demonstração não envia dados a um servidor nem sincroniza entre aparelhos.",
          ],
          [
            "O que ainda depende do backend?",
            "Login real, convites, permissões, consentimento, armazenamento de arquivos, OCR, correção por IA, cálculo de domínio e sincronização. A troca de perfil aqui serve apenas para testar as telas.",
          ],
        ].map(([q, a]) => (
          <details className="faq" key={q}>
            <summary>{q}</summary>
            <p>{a}</p>
          </details>
        ))}
      </Card>
    </>
  );
}
