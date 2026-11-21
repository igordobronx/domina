import { useEffect, useState } from "react";
import { BookOpen, CheckCheck, Dumbbell, Target, TrendingDown, TrendingUp } from "lucide-react";
import { Progress } from "../components/ui";
import { RealSparkline } from "../components/Chart";
import { HABILIDADE_NOME } from "./Learning";
import {
  dominioDoAluno,
  evolucaoDoAluno,
  praticaDoAluno,
  type DominioAPI,
  type EvolucaoMateriaAPI,
  type PraticaAPI,
} from "../services/api";

const ATENCAO = 50; // abaixo disso a competencia aparece em amarelo ("precisa de atencao")

// Turmas (professor/gestor): resumo completo do mapa de dominio de um aluno.
// So mostra as materias que quem esta vendo leciona (o backend ja filtra).
export function ResumoDominioAluno({ alunoId }: { alunoId: string }) {
  const [dados, setDados] = useState<{
    dominio: DominioAPI[];
    evolucao: EvolucaoMateriaAPI[];
    pratica: PraticaAPI[];
  } | null>(null);
  const [erro, setErro] = useState(false);

  useEffect(() => {
    Promise.all([
      dominioDoAluno(alunoId),
      evolucaoDoAluno(alunoId).catch(() => []),
      praticaDoAluno(alunoId).catch(() => []),
    ])
      .then(([dominio, evolucao, pratica]) => setDados({ dominio, evolucao, pratica }))
      .catch(() => setErro(true));
  }, [alunoId]);

  if (erro) return <p className="muted">Não foi possível carregar o domínio deste aluno.</p>;
  if (!dados) return <p className="muted">Carregando...</p>;

  const competencias = dados.dominio.filter((d) => d.num_evidencias > 0);
  const { evolucao, pratica } = dados;
  if (!competencias.length && !evolucao.length && !pratica.length)
    return <p className="muted">Ainda sem correções aprovadas nas matérias que você leciona para este aluno.</p>;

  const totalAtividades = evolucao.reduce((s, e) => s + e.num_atividades, 0);
  const media = totalAtividades
    ? Math.round(evolucao.reduce((s, e) => s + e.media_percentual * e.num_atividades, 0) / totalAtividades)
    : null;
  const respondidos = pratica.reduce((s, p) => s + p.respondidos, 0);
  const acertos = pratica.reduce((s, p) => s + p.acertos, 0);
  const ordenadas = [...competencias].sort((a, b) => b.percentual_dominio - a.percentual_dominio);
  const forte = ordenadas.length > 1 ? ordenadas[0] : null;
  const fraca = ordenadas.length > 1 ? ordenadas[ordenadas.length - 1] : null;
  const praticaDe = (codigo: string) => pratica.find((p) => p.habilidade_codigo === codigo);
  const nome = (d: DominioAPI) => HABILIDADE_NOME[d.habilidade_codigo] ?? d.tema;
  const porMateria = [...new Set(competencias.map((d) => d.materia))];

  return (
    <div className="resumo-aluno">
      <div className="resumo-numeros">
        <div>
          <Target size={16} />
          <strong>{media != null ? `${media}%` : "--"}</strong>
          <span>Média nas correções aprovadas</span>
        </div>
        <div>
          <CheckCheck size={16} />
          <strong>{totalAtividades}</strong>
          <span>Atividades corrigidas</span>
        </div>
        <div>
          <Dumbbell size={16} />
          <strong>{respondidos ? `${acertos}/${respondidos}` : "--"}</strong>
          <span>Exercícios certos</span>
        </div>
      </div>

      {(forte || fraca) && (
        <div className="resumo-destaques">
          {forte && (
            <p className="resumo-forte">
              <TrendingUp size={15} /> <b>Ponto forte:</b> {forte.habilidade_codigo} · {nome(forte)} ({Math.round(forte.percentual_dominio)}%)
            </p>
          )}
          {fraca && (
            <p className="resumo-fraco">
              <TrendingDown size={15} /> <b>Precisa de atenção:</b> {fraca.habilidade_codigo} · {nome(fraca)} ({Math.round(fraca.percentual_dominio)}%)
            </p>
          )}
        </div>
      )}

      {evolucao.length > 0 && (
        <div className="resumo-bloco">
          <h4><BookOpen size={15} /> Por matéria</h4>
          {evolucao.map((e) => (
            <div key={e.materia_id} className="resumo-materia">
              <div className="resumo-linha">
                <strong>{e.materia}</strong>
                <span className="resumo-pct">{Math.round(e.media_percentual)}%</span>
              </div>
              <Progress value={e.media_percentual} label={e.materia} />
              <p className="tiny muted">{e.num_atividades} atividade(s) corrigida(s) e aprovada(s)</p>
              {e.historico.length > 1 && (
                <div className="resumo-grafico"><RealSparkline pontos={e.historico} /></div>
              )}
            </div>
          ))}
        </div>
      )}

      {porMateria.map((materia) => (
        <div key={materia} className="resumo-bloco">
          <h4><Target size={15} /> Competências · {materia}</h4>
          <div className="resumo-competencias">
            {competencias
              .filter((d) => d.materia === materia)
              .sort((a, b) => a.habilidade_codigo.localeCompare(b.habilidade_codigo))
              .map((d) => {
                const p = praticaDe(d.habilidade_codigo);
                const baixo = d.percentual_dominio < ATENCAO;
                return (
                  <div key={d.tema_id} className={`resumo-competencia ${baixo ? "baixo" : ""}`}>
                    <div className="resumo-linha">
                      <span><b>{d.habilidade_codigo}</b> {nome(d)}</span>
                      <span className="resumo-pct">{Math.round(d.percentual_dominio)}%</span>
                    </div>
                    <Progress value={d.percentual_dominio} label={d.tema} amber={baixo} />
                    <p className="tiny muted">
                      {d.num_evidencias} correção(ões) aprovada(s)
                      {p ? ` · prática: ${p.acertos} de ${p.respondidos} certos` : " · sem prática ainda"}
                    </p>
                  </div>
                );
              })}
          </div>
        </div>
      ))}

      <p className="tiny muted">
        O domínio é uma estimativa feita só com correções aprovadas pelo professor. Não é nota oficial.
      </p>
    </div>
  );
}
