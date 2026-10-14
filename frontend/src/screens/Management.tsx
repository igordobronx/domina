import { useState } from "react";
import { BookOpen, Check, Plus, Users } from "lucide-react";
import type { DemoState } from "../types";
import { Badge, Button, Card, SectionTitle } from "../components/ui";

export function Classes({ state }: { state: DemoState }) {
  const [opened, setOpened] = useState(false);
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">APRENDER JUNTOS</div>
          <h1>Minhas turmas</h1>
          <p>Uma visão próxima de cada jornada de aprendizagem.</p>
        </div>
      </div>
      <Card>
        <div className="class-summary">
          <span className="class-icon">
            <Users size={30} />
          </span>
          <div>
            <h2>Pré-ENEM A</h2>
            <p>2026 · Escola Horizonte · Turma demonstrativa</p>
          </div>
          <Badge tone="neutral">1 aluna</Badge>
        </div>
        <div className="stats-grid compact-stats">
          <div>
            <strong>
              {state.activities.filter((a) => a.status === "pendente").length}
            </strong>
            <p>atividade em revisão</p>
          </div>
          <div>
            <strong>
              {state.activities.filter((a) => a.status === "aprovada").length}
            </strong>
            <p>atividade corrigida</p>
          </div>
          <div>
            <strong>67%</strong>
            <p>domínio ilustrativo</p>
          </div>
        </div>
        <Button variant="secondary" onPress={() => setOpened(!opened)}>
          {opened ? "Ocultar alunos" : "Ver alunos da turma"}
        </Button>
        {opened && (
          <div className="student-table">
            <div className="avatar">AS</div>
            <div>
              <strong>{state.name}</strong>
              <p className="muted">Redação ENEM e Matemática</p>
            </div>
            <Badge>Ativa</Badge>
          </div>
        )}
      </Card>
      <div className="info-banner">
        <BookOpen size={22} />
        <p>
          O cadastro real de turmas, convites e vínculos será conectado à API da
          escola. Esta tela apresenta uma turma de demonstração.
        </p>
      </div>
    </>
  );
}
export function Materials({
  state,
  update,
  notify,
}: {
  state: DemoState;
  update: (fn: (s: DemoState) => DemoState) => void;
  notify: (s: string) => void;
}) {
  const [adding, setAdding] = useState(false),
    [name, setName] = useState(""),
    [subject, setSubject] = useState("Redação ENEM"),
    [file, setFile] = useState<File | null>(null),
    [error, setError] = useState("");
  const add = () => {
    if (!name.trim() || !file) {
      setError("Informe um título e selecione o documento.");
      return;
    }
    update((s) => ({
      ...s,
      materials: [
        ...s.materials,
        {
          id: crypto.randomUUID(),
          name: name.trim(),
          subject,
          approved: false,
          fileName: file.name,
        },
      ],
    }));
    setAdding(false);
    setName("");
    setFile(null);
    setError("");
    notify(
      "Material adicionado à demonstração. Nenhum arquivo foi enviado ao servidor.",
    );
  };
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">A BASE DE UM BOM APRENDIZADO</div>
          <h1>Materiais e critérios</h1>
          <p>O conteúdo da escola orienta cada correção.</p>
        </div>
        <Button icon={Plus} onPress={() => setAdding(!adding)}>
          {adding ? "Fechar formulário" : "Adicionar material"}
        </Button>
      </div>
      {adding && (
        <Card>
          <SectionTitle title="Novo material" />
          <div className="form-grid">
            <label>
              Título
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex.: Rubrica de argumentação"
              />
            </label>
            <label>
              Matéria
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              >
                <option>Redação ENEM</option>
                <option>Matemática</option>
              </select>
            </label>
            <label>
              Documento (até 10 MB)
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (
                    f &&
                    (f.size > 10 * 1024 * 1024 ||
                      !/\.(pdf|docx|txt)$/i.test(f.name))
                  ) {
                    setFile(null);
                    setError("Escolha PDF, DOCX ou TXT com até 10 MB.");
                    e.target.value = "";
                  } else {
                    setFile(f || null);
                    setError("");
                  }
                }}
              />
            </label>
          </div>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <Button onPress={add}>Salvar material demonstrativo</Button>
        </Card>
      )}
      <Card>
        {state.materials.map((m) => (
          <div className="material-row" key={m.id}>
            <div className="activity-icon">
              <BookOpen size={21} />
            </div>
            <div className="activity-info">
              <strong>{m.name}</strong>
              <span>
                {m.subject} · {m.fileName}
              </span>
            </div>
            <Badge tone={m.approved ? "green" : "amber"}>
              {m.approved ? "Base aprovada" : "Aguardando integração"}
            </Badge>
          </div>
        ))}
      </Card>
      <div className="info-banner">
        <Check size={22} />
        <p>
          A extração de temas e a aprovação de critérios dependem do
          processamento real. Os materiais adicionados aqui ficam como registros
          locais; não entram nas correções.
        </p>
      </div>
    </>
  );
}
