import { useEffect, useState } from "react";
import { Download, RotateCcw, Save, ShieldCheck } from "lucide-react";
import type { DemoState, Role } from "../types";
import { Badge, Button, Card, SectionTitle } from "../components/ui";
import { initialState } from "../data/demo";
import {
  auditLog,
  custoUso,
  meuConsentimento,
  registrarConsentimento,
  type AuditLogAPI,
  type CustoUsoAPI,
  type UsuarioAtual,
} from "../services/api";

export function Settings({
  state,
  update,
  notify,
  onInstall,
  role,
  currentUser,
}: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  notify: (s: string) => void;
  onInstall: () => void;
  role?: Role;
  currentUser?: UsuarioAtual | null;
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
  const real = !!currentUser;
  return (
    <>
      {real && role === "aluno" && <Consentimento notify={notify} />}
      {real && role === "gestor" && <CustoEAuditoria notify={notify} />}
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

function Consentimento({ notify }: { notify: (s: string) => void }) {
  const [consentimento, setConsentimento] = useState<{ responsavel_nome: string; aceito_em: string } | "ausente" | null>(null);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    meuConsentimento()
      .then(setConsentimento)
      .catch(() => setConsentimento("ausente"));
  }, []);

  const registrar = async () => {
    if (!nome.trim() || !email.trim()) {
      setError("Informe o nome e o e-mail do responsável.");
      return;
    }
    setSalvando(true);
    setError("");
    try {
      const c = await registrarConsentimento({ responsavel_nome: nome.trim(), responsavel_email: email.trim() });
      setConsentimento(c);
      notify("Consentimento registrado.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível registrar o consentimento.");
    } finally {
      setSalvando(false);
    }
  };

  if (consentimento === null) return null;
  return (
    <Card>
      <SectionTitle title="Consentimento do responsável (LGPD)" />
      {consentimento === "ausente" ? (
        <>
          <p className="muted">
            Para usar a plataforma, registre o nome e o e-mail do responsável que autoriza o uso dos
            seus dados de estudo.
          </p>
          <div className="form-grid">
            <label>
              Nome do responsável
              <input value={nome} onChange={(e) => setNome(e.target.value)} />
            </label>
            <label>
              E-mail do responsável
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
          </div>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <Button icon={ShieldCheck} disabled={salvando} onPress={registrar}>
            {salvando ? "Registrando..." : "Registrar consentimento"}
          </Button>
        </>
      ) : (
        <p>
          <Badge>Consentimento registrado</Badge> por {consentimento.responsavel_nome} em{" "}
          {new Date(consentimento.aceito_em).toLocaleDateString("pt-BR")}.
        </p>
      )}
    </Card>
  );
}

function CustoEAuditoria({ notify }: { notify: (s: string) => void }) {
  const [custo, setCusto] = useState<CustoUsoAPI | null>(null);
  const [logs, setLogs] = useState<AuditLogAPI[] | null>(null);

  useEffect(() => {
    Promise.all([custoUso(), auditLog()])
      .then(([c, l]) => {
        setCusto(c);
        setLogs(l);
      })
      .catch(() => notify("Não foi possível carregar custo e auditoria da escola."));
  }, []);

  return (
    <>
      <Card>
        <SectionTitle title="Custo e uso da IA este mês" />
        {!custo ? (
          <p className="muted">Carregando...</p>
        ) : (
          <div className="form-grid">
            <div>
              <strong>{custo.tokens_llm.toLocaleString("pt-BR")}</strong>
              <p className="muted">tokens de correção</p>
            </div>
            <div>
              <strong>{custo.chamadas_ocr.toLocaleString("pt-BR")}</strong>
              <p className="muted">leituras de foto (OCR)</p>
            </div>
            <div>
              <strong>
                {custo.custo_estimado.toLocaleString("pt-BR", { style: "currency", currency: "USD" })}
              </strong>
              <p className="muted">custo estimado ({custo.mes_referencia})</p>
            </div>
          </div>
        )}
      </Card>
      <Card>
        <SectionTitle title="Registro de auditoria" />
        {!logs ? (
          <p className="muted">Carregando...</p>
        ) : !logs.length ? (
          <p className="muted">Nenhum registro ainda.</p>
        ) : (
          logs.slice(0, 20).map((l) => (
            <div className="material-row" key={l.id}>
              <div className="activity-info">
                <strong>{l.acao}</strong>
                <span>
                  {l.entidade} · {new Date(l.criado_em).toLocaleString("pt-BR")}
                </span>
              </div>
            </div>
          ))
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
