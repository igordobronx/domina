"""XP, sequencia de dias e conquistas do aluno (docs/decisoes/gamificacao-niveis-e-metas.md).

Nada disso e gravado: o XP e CALCULADO na hora a partir do que o aluno ja fez (envios confirmados,
correcoes aprovadas, exercicios respondidos e metas cumpridas). Assim o passado conta sozinho e
nada fica inconsistente. As contas ficam numa funcao pura (montar_xp), facil de testar.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    FUSO = ZoneInfo("America/Sao_Paulo")
except Exception:  # sistema sem base de fusos: Brasilia nao tem horario de verao desde 2019
    FUSO = timezone(timedelta(hours=-3))


def dia_local(dt: datetime) -> date:
    """O banco grava UTC (server_default now()). O dia de estudo/prazo e o dia em Brasilia."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(FUSO).date()


def hoje_local() -> date:
    return datetime.now(FUSO).date()

# valores combinados com o usuario em 18/11/2026
XP_ENVIO = 10
XP_NO_PRAZO = 5
XP_APROVADA = 5
XP_NOTA_ALTA = 10          # nota aprovada >= 80%
NOTA_ALTA_PCT = 80
XP_RESPONDER = 2
XP_ACERTAR = 3
TETO_EXERCICIOS_DIA = 30   # evita subir de nivel so gerando exercicios da IA
XP_SEQUENCIA = 15          # a cada 7 dias seguidos
DIAS_SEQUENCIA = 7
XP_CONQUISTA = 20

# (codigo, nome, descricao, alvo)
CONQUISTAS = [
    ("PRIMEIRO_PASSO", "Primeiro passo", "Enviou a primeira atividade", 1),
    ("PONTUAL", "Pontual", "5 atividades enviadas no prazo", 5),
    ("REDATOR", "Redator", "5 redações enviadas", 5),
    ("NOTA_900", "Nota 900+", "Redação aprovada com 900 ou mais", 1),
    ("MAO_NA_MASSA", "Mão na massa", "20 exercícios respondidos", 20),
    ("CERTEIRO", "Certeiro", "50 exercícios certos", 50),
    ("CONSTANCIA", "Constância", "7 dias seguidos estudando", 7),
    ("IMPARAVEL", "Imparável", "30 dias seguidos estudando", 30),
    ("META_BATIDA", "Meta batida", "Cumpriu a primeira meta", 1),
]


@dataclass
class Envio:
    data: date
    titulo: str
    no_prazo: bool
    redacao: bool


@dataclass
class Aprovacao:  # so correcao APROVADA pelo professor; nota da IA nunca entra aqui
    data: date
    titulo: str
    pct: float
    redacao: bool
    nota: float


@dataclass
class Resposta:
    data: date
    correta: bool  # "Parcial" do professor conta como respondida, nao como acerto


@dataclass
class MetaFeita:
    data: date
    titulo: str
    pontos: int


def _sequencias(dias: list[date]) -> list[tuple[date, int]]:
    """Para cada dia de estudo (em ordem), quantos dias seguidos ele completa."""
    out, anterior, n = [], None, 0
    for dia in dias:
        n = n + 1 if anterior and dia - anterior == timedelta(days=1) else 1
        out.append((dia, n))
        anterior = dia
    return out


def _quando_atinge(datas: list[date], alvo: int) -> date | None:
    """Data em que a contagem chega no alvo (datas em qualquer ordem)."""
    datas = sorted(datas)
    return datas[alvo - 1] if len(datas) >= alvo else None


def montar_xp(envios: list[Envio], aprovacoes: list[Aprovacao], respostas: list[Resposta],
              metas: list[MetaFeita], hoje: date) -> dict:
    hist: list[dict] = []

    def ganha(dia: date, xp: int, motivo: str) -> None:
        if xp:
            hist.append({"data": dia, "xp": xp, "motivo": motivo})

    for e in envios:
        if e.no_prazo:
            ganha(e.data, XP_ENVIO + XP_NO_PRAZO, f"Enviou “{e.titulo}” no prazo")
        else:
            ganha(e.data, XP_ENVIO, f"Enviou “{e.titulo}”")
    for a in aprovacoes:
        if a.pct >= NOTA_ALTA_PCT:
            ganha(a.data, XP_APROVADA + XP_NOTA_ALTA, f"Professor aprovou “{a.titulo}” com {NOTA_ALTA_PCT}% ou mais")
        else:
            ganha(a.data, XP_APROVADA, f"Professor aprovou “{a.titulo}”")

    # exercicios: um item por dia, com teto diario
    por_dia: dict[date, list[Resposta]] = defaultdict(list)
    for r in respostas:
        por_dia[r.data].append(r)
    for dia, rs in por_dia.items():
        bruto = sum(XP_RESPONDER + (XP_ACERTAR if r.correta else 0) for r in rs)
        certos = sum(1 for r in rs if r.correta)
        ganha(dia, min(bruto, TETO_EXERCICIOS_DIA),
              f"{len(rs)} exercício{'s' if len(rs) > 1 else ''} respondido{'s' if len(rs) > 1 else ''}, {certos} certo{'s' if certos != 1 else ''}")

    for m in metas:
        ganha(m.data, m.pontos, f"Meta cumprida: “{m.titulo}”")

    # sequencia de dias: dia de estudo = enviou atividade ou respondeu exercicio
    dias = sorted({e.data for e in envios} | set(por_dia))
    seq = _sequencias(dias)
    for dia, n in seq:
        if n % DIAS_SEQUENCIA == 0:
            ganha(dia, XP_SEQUENCIA, f"{n} dias seguidos estudando")
    melhor = max((n for _, n in seq), default=0)
    atual = seq[-1][1] if seq and seq[-1][0] >= hoje - timedelta(days=1) else 0

    def dia_da_sequencia(alvo: int) -> date | None:
        return next((dia for dia, n in seq if n >= alvo), None)

    # conquistas: (progresso, data em que foi conquistada)
    estado = {
        "PRIMEIRO_PASSO": (len(envios), _quando_atinge([e.data for e in envios], 1)),
        "PONTUAL": (sum(e.no_prazo for e in envios), _quando_atinge([e.data for e in envios if e.no_prazo], 5)),
        "REDATOR": (sum(e.redacao for e in envios), _quando_atinge([e.data for e in envios if e.redacao], 5)),
        "NOTA_900": (sum(1 for a in aprovacoes if a.redacao and a.nota >= 900),
                     _quando_atinge([a.data for a in aprovacoes if a.redacao and a.nota >= 900], 1)),
        "MAO_NA_MASSA": (len(respostas), _quando_atinge([r.data for r in respostas], 20)),
        "CERTEIRO": (sum(r.correta for r in respostas), _quando_atinge([r.data for r in respostas if r.correta], 50)),
        "CONSTANCIA": (melhor, dia_da_sequencia(7)),
        "IMPARAVEL": (melhor, dia_da_sequencia(30)),
        "META_BATIDA": (len(metas), _quando_atinge([m.data for m in metas], 1)),
    }
    conquistas = []
    for codigo, nome, descricao, alvo in CONQUISTAS:
        progresso, quando = estado[codigo]
        conquistas.append({"codigo": codigo, "nome": nome, "descricao": descricao, "alvo": alvo,
                           "progresso": min(int(progresso), alvo), "conquistada_em": quando})
        if quando:
            ganha(quando, XP_CONQUISTA, f"Conquista: {nome}")

    hist.sort(key=lambda h: h["data"], reverse=True)  # sort estavel: dentro do dia mantem a ordem acima
    return {
        "xp": sum(h["xp"] for h in hist),
        "historico": hist,
        "sequencia": {"atual": atual, "melhor": melhor, "estudou_hoje": bool(dias) and dias[-1] == hoje},
        "conquistas": conquistas,
    }


# ---------------- leitura do banco ----------------
def carregar_eventos(db, aluno_id):
    """Le do banco o que da XP. Envio: so confirmado e 1 por atividade (o primeiro). Aprovacao: so
    correcao APROVADA com nota do professor, 1 por atividade (a maior). Meta: inclui as arquivadas."""
    from app.models.enum import StatusCorrecaoEnum, TipoMateriaEnum
    from app.models.usuario import Atividade, Correcao, ExercicioResposta, Materia, Meta, MetaConcluida, Submissao

    redacoes = (TipoMateriaEnum.REDACAO_ENEM, TipoMateriaEnum.REDACAO_OUTRO_VESTIBULAR)
    # so as colunas necessarias (nunca o texto da redacao): o ranking chama isto para cada aluno
    linhas = (db.query(Submissao.criado_em, Atividade.id, Atividade.titulo, Atividade.prazo, Atividade.valor_total,
                       Materia.tipo, Correcao.status, Correcao.nota_professor)
              .join(Atividade, Atividade.id == Submissao.atividade_id)
              .join(Materia, Materia.id == Atividade.materia_id)
              .outerjoin(Correcao, Correcao.submissao_id == Submissao.id)
              .filter(Submissao.aluno_id == aluno_id, Submissao.texto_confirmado.isnot(None))
              .order_by(Submissao.criado_em).all())
    envios: dict = {}
    aprovacoes: dict = {}
    for criado_em, ativ_id, titulo, prazo, valor_total, tipo_materia, status, nota_professor in linhas:
        dia, redacao = dia_local(criado_em), tipo_materia in redacoes
        if ativ_id not in envios:
            envios[ativ_id] = Envio(dia, titulo, bool(prazo and dia <= prazo), redacao)
        if status == StatusCorrecaoEnum.APROVADA and nota_professor is not None:
            nota = float(nota_professor)
            pct = nota / float(valor_total or 1000) * 100
            if ativ_id not in aprovacoes or nota > aprovacoes[ativ_id].nota:
                aprovacoes[ativ_id] = Aprovacao(dia, titulo, pct, redacao, nota)

    respostas = [Resposta(dia_local(criado_em), bool(correta))
                 for criado_em, correta in db.query(ExercicioResposta.criado_em, ExercicioResposta.correta)
                 .filter(ExercicioResposta.aluno_id == aluno_id) if criado_em is not None]
    metas = [MetaFeita(dia_local(concluida_em), titulo, int(pontos))
             for concluida_em, titulo, pontos in db.query(MetaConcluida.concluida_em, Meta.titulo, Meta.pontos)
             .join(Meta, Meta.id == MetaConcluida.meta_id).filter(MetaConcluida.aluno_id == aluno_id)]
    return list(envios.values()), list(aprovacoes.values()), respostas, metas


def xp_do_aluno(db, aluno_id, hoje: date | None = None) -> dict:
    """Resultado completo de montar_xp para um aluno."""
    return montar_xp(*carregar_eventos(db, aluno_id), hoje or hoje_local())
