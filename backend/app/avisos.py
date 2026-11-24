"""Notificacoes (o sino do topo). Dois jeitos de nascer:
- evento: acontece uma acao (atividade nova, correcao aprovada...) e a rota chama `tentar(db, ...)`;
- alerta por tempo: prazo chegando, feriado amanha, sequencia em risco... `gerar_alertas` confere quando
  a pessoa abre o app (a cada poucos minutos), sem tarefa agendada. `chave` impede repetir o mesmo alerta.
Nada aqui pode derrubar a requisicao: `tentar` engole o erro (e desfaz so o aviso)."""
import logging
import time
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.feriados import feriados
from app.gamificacao import FUSO, dia_local, hoje_local, xp_do_aluno
from app.metas import metas_do_aluno, nivel_de
from app.models.enum import PerfilEnum, StatusCorrecaoEnum, UsuarioTurmaPapelEnum
from app.models.usuario import (
    Atividade, Aviso, Correcao, Evento, Meta, MetaConcluida, Submissao, Usuario, UsuarioTurma,
)

logger = logging.getLogger(__name__)

JANELA_RECENTE = 7  # dias: conquista/meta mais antiga que isso nao vira aviso (evita enxurrada no 1o acesso)
INTERVALO = 300  # s entre duas conferencias de alerta da mesma pessoa
_ultima: dict = {}


def avisar(db: Session, usuario_id, tipo: str, texto: str, destino: str | None = None,
           chave: str | None = None, submissao_id=None, lido: bool = False) -> bool:
    """Cria o aviso (sem commit). Com `chave`, so cria se essa pessoa ainda nao recebeu esse alerta."""
    if chave and db.query(Aviso.id).filter_by(usuario_id=usuario_id, chave=chave).first():
        return False
    db.add(Aviso(usuario_id=usuario_id, tipo=tipo, texto=texto[:255], destino=destino, chave=chave,
                 submissao_id=submissao_id, lido=lido))
    return True


def acumular(db: Session, usuario_id, tipo: str, chave: str, destino: str, um: str, varios: str) -> None:
    """Varios eventos iguais viram um aviso so enquanto nao foi lido ("5 novos envios em ...")."""
    a = db.query(Aviso).filter_by(usuario_id=usuario_id, chave=chave, lido=False).first()
    if a:
        a.qtd += 1
        a.texto = varios.format(n=a.qtd)[:255]
        a.criado_em = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        db.add(Aviso(usuario_id=usuario_id, tipo=tipo, texto=um[:255], destino=destino, chave=chave))


def tentar(db: Session, fn, *args) -> None:
    try:
        fn(db, *args)
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("falha ao criar aviso")


def _alunos_da_turma(db: Session, turma_id) -> list[Usuario]:
    return (db.query(Usuario).join(UsuarioTurma, UsuarioTurma.usuario_id == Usuario.id)
            .filter(UsuarioTurma.turma_id == turma_id, UsuarioTurma.papel == UsuarioTurmaPapelEnum.ALUNO).all())


# ---------- eventos (chamados pelas rotas) ----------

def atividade_nova(db: Session, atividade: Atividade) -> None:
    for aluno in _alunos_da_turma(db, atividade.turma_id):
        avisar(db, aluno.id, "ATIVIDADE_NOVA", f"Nova atividade: “{atividade.titulo[:150]}”.", "atividades")


def exercicio_novo(db: Session, exercicio, alunos: list[Usuario]) -> None:
    titulo = exercicio.titulo or exercicio.assunto or "exercício"
    for aluno in alunos:
        avisar(db, aluno.id, "EXERCICIO_NOVO", f"Novo exercício de prática: “{titulo[:150]}”.", "estudos")


def envio_novo(db: Session, submissao: Submissao, quem_enviou) -> None:
    """Aluno enviou: avisa o professor que criou a atividade (agrupado por atividade)."""
    atividade = db.get(Atividade, submissao.atividade_id)
    dono = atividade.criado_por
    if not dono or dono == quem_enviou:
        return
    aluno = db.get(Usuario, submissao.aluno_id)
    titulo = atividade.titulo[:120]
    acumular(db, dono, "ENVIO", f"envio:{atividade.id}", "revisoes",
             f"{aluno.nome.split()[0]} enviou “{titulo}”.", f"{{n}} novos envios em “{titulo}”.")


def ia_corrigiu(db: Session, submissao: Submissao, status: StatusCorrecaoEnum) -> None:
    atividade = db.get(Atividade, submissao.atividade_id)
    if not atividade.criado_por:
        return
    titulo = atividade.titulo[:120]
    if status == StatusCorrecaoEnum.REQUER_ATENCAO:
        acumular(db, atividade.criado_por, "IA_CORRIGIU", f"iaaten:{atividade.id}", "revisoes",
                 f"A IA corrigiu um envio de “{titulo}” e pede a sua atenção.",
                 f"A IA corrigiu {{n}} envios de “{titulo}” que pedem a sua atenção.")
    else:
        acumular(db, atividade.criado_por, "IA_CORRIGIU", f"ia:{atividade.id}", "revisoes",
                 f"A IA corrigiu um envio de “{titulo}”. Falta a sua revisão.",
                 f"A IA corrigiu {{n}} envios de “{titulo}”. Falta a sua revisão.")


def corrigida(db: Session, submissao: Submissao, atividade: Atividade) -> None:
    avisar(db, submissao.aluno_id, "CORRIGIDA", f"Sua atividade “{atividade.titulo[:150]}” foi corrigida. "
           "Veja a nota e as marcações do professor.", "atividades", submissao_id=submissao.id)


# ---------- alertas por tempo (conferidos ao abrir o app) ----------

def gerar_alertas(db: Session, usuario: Usuario, agora: float | None = None) -> None:
    agora = agora or time.monotonic()
    if agora - _ultima.get(usuario.id, -INTERVALO) < INTERVALO:
        return
    _ultima[usuario.id] = agora
    try:
        hoje = hoje_local()
        _calendario(db, usuario, hoje)
        if usuario.perfil == PerfilEnum.ALUNO:
            _do_aluno(db, usuario, hoje)
        elif usuario.perfil == PerfilEnum.PROFESSOR:
            _do_professor(db, usuario, hoje)
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("falha ao gerar alertas")


def _turmas(db: Session, usuario: Usuario) -> list:
    return [t for (t,) in db.query(UsuarioTurma.turma_id).filter_by(usuario_id=usuario.id)]


def _calendario(db: Session, u: Usuario, hoje: date) -> None:
    amanha = hoje + timedelta(days=1)
    for dia, nome in feriados(amanha.year):
        if dia == amanha:
            avisar(db, u.id, "FERIADO", f"Amanhã é feriado: {nome}.", "calendario", chave=f"feriado:{dia}")
    if u.escola_id is None:
        return
    turmas = _turmas(db, u)
    for ev in db.query(Evento).filter(Evento.escola_id == u.escola_id, Evento.inicio == amanha):
        if ev.turma_id is None or ev.turma_id in turmas:
            avisar(db, u.id, "EVENTO", f"Amanhã: {ev.titulo[:150]}.", "calendario", chave=f"evento:{ev.id}")


def _do_aluno(db: Session, u: Usuario, hoje: date) -> None:
    recente = hoje - timedelta(days=JANELA_RECENTE)
    feitas = {m: dia_local(q) for m, q in db.query(MetaConcluida.meta_id, MetaConcluida.concluida_em).filter_by(aluno_id=u.id)}
    for meta in metas_do_aluno(db, u):
        if meta.id in feitas:
            if feitas[meta.id] >= recente:
                avisar(db, u.id, "META", f"Meta batida: {meta.titulo[:120]} (+{meta.pontos} XP).", "metas", chave=f"meta:{meta.id}")
        elif meta.fim and 0 <= (meta.fim - hoje).days <= 3:
            avisar(db, u.id, "META", f"A meta “{meta.titulo[:120]}” termina em {(meta.fim - hoje).days} dia(s).",
                   "metas", chave=f"metafim:{meta.id}")

    r = xp_do_aluno(db, u.id, hoje)
    for c in r["conquistas"]:
        if c["conquistada_em"] and c["conquistada_em"] >= hoje - timedelta(days=3):
            avisar(db, u.id, "CONQUISTA", f"Conquista desbloqueada: {c['nome']}!", "evolucao", chave=f"conquista:{c['codigo']}")

    n = nivel_de(r["xp"])
    vistos = [int(k.split(":")[1]) for (k,) in db.query(Aviso.chave).filter(Aviso.usuario_id == u.id, Aviso.chave.like("nivel:%"))]
    if not vistos:  # primeira conferencia: so guarda o nivel de hoje, sem avisar de tudo que ja passou
        avisar(db, u.id, "MARCADOR", "nivel", chave=f"nivel:{n['nivel']}", lido=True)
    elif n["nivel"] > max(vistos):
        avisar(db, u.id, "NIVEL", f"Você subiu para o nível {n['nivel']}: {n['nome']}!", "evolucao", chave=f"nivel:{n['nivel']}")

    s = r["sequencia"]
    if s["atual"] >= 3 and not s["estudou_hoje"] and datetime.now(FUSO).hour >= 18:
        avisar(db, u.id, "SEQUENCIA", f"Sua sequência de {s['atual']} dias está em risco. Estude hoje para não perdê-la.",
               "estudos", chave=f"sequencia:{hoje}")

    enviadas = {a for (a,) in db.query(Submissao.atividade_id).filter(
        Submissao.aluno_id == u.id, Submissao.texto_confirmado.isnot(None))}
    for a in db.query(Atividade).filter(Atividade.turma_id.in_(_turmas(db, u) or [None]), Atividade.arquivada.is_(False),
                                        Atividade.prazo.isnot(None)):
        if a.id in enviadas:
            continue
        d = (a.prazo - hoje).days
        t = a.titulo[:120]
        if d in (1, 2):
            avisar(db, u.id, "PRAZO", f"A atividade “{t}” vence {'amanhã' if d == 1 else 'em 2 dias'}.", "atividades", chave=f"prazo:{a.id}:{d}")
        elif d == 0:
            avisar(db, u.id, "PRAZO", f"A atividade “{t}” vence hoje.", "atividades", chave=f"prazo:{a.id}:0")
        elif d == -1:
            avisar(db, u.id, "PRAZO", f"O prazo de “{t}” acabou ontem. Ainda dá para enviar.", "atividades", chave=f"vencida:{a.id}")


def _do_professor(db: Session, u: Usuario, hoje: date) -> None:
    for a in db.query(Atividade).filter(Atividade.criado_por == u.id, Atividade.arquivada.is_(False),
                                        Atividade.prazo < hoje, Atividade.prazo >= hoje - timedelta(days=JANELA_RECENTE)):
        enviaram = {s for (s,) in db.query(Submissao.aluno_id).filter(
            Submissao.atividade_id == a.id, Submissao.texto_confirmado.isnot(None))}
        faltam = [x for x in _alunos_da_turma(db, a.turma_id) if x.id not in enviaram]
        if faltam:
            avisar(db, u.id, "SEM_ENVIO", f"O prazo de “{a.titulo[:120]}” acabou: {len(faltam)} aluno(s) não enviaram.",
                   "revisoes", chave=f"semenvio:{a.id}")
    limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=3)
    parados = (db.query(func.count(Submissao.id)).join(Atividade, Atividade.id == Submissao.atividade_id)
               .join(Correcao, Correcao.submissao_id == Submissao.id)
               .filter(Atividade.criado_por == u.id, Submissao.criado_em < limite,
                       Correcao.status.in_([StatusCorrecaoEnum.PENDENTE, StatusCorrecaoEnum.REQUER_ATENCAO])).scalar())
    if parados:
        ano, semana, _ = hoje.isocalendar()
        avisar(db, u.id, "PARADOS", f"{parados} envio(s) esperam a sua revisão há mais de 3 dias.", "revisoes",
               chave=f"parados:{ano}-{semana}")
