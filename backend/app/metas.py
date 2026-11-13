"""Metas e niveis. O progresso e CALCULADO dos dados reais (envios, notas aprovadas, dominio); so a
conclusao fica gravada (MetaConcluida). O nivel tambem e calculado: soma dos pontos das metas
concluidas, entao editar/arquivar uma meta nunca deixa o nivel de alguem inconsistente."""
import logging
from datetime import date, datetime, time

from sqlalchemy import Date as SADate, and_, cast, func, or_
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.enum import PerfilEnum, StatusCorrecaoEnum
from app.models.usuario import (
    Atividade, Correcao, DominioAluno, Meta, MetaConcluida, Submissao, Tema, Usuario, UsuarioTurma,
)

logger = logging.getLogger("domina.metas")

TIPOS_PERCENTUAIS = ("NOTA_ATIVIDADE", "MEDIA_MATERIA", "DOMINIO_COMPETENCIA")
# (pontos minimos, nome): o nivel e a posicao + 1
NIVEIS = [(0, "Iniciante"), (20, "Aprendiz"), (50, "Explorador"), (100, "Estudante dedicado"),
          (180, "Veterano"), (300, "Mestre"), (500, "Lenda")]


def nivel_de(pontos: int) -> dict:
    i = max(k for k, (minimo, _) in enumerate(NIVEIS) if pontos >= minimo)
    return {
        "nivel": i + 1, "nome": NIVEIS[i][1], "pontos": pontos, "pontos_nivel_atual": NIVEIS[i][0],
        "pontos_proximo": NIVEIS[i + 1][0] if i + 1 < len(NIVEIS) else None,
    }


def pontos_do_aluno(db: Session, aluno_id) -> int:
    # inclui metas arquivadas depois: o que o aluno ja ganhou nao se perde
    return int(db.query(func.coalesce(func.sum(Meta.pontos), 0)).join(MetaConcluida, MetaConcluida.meta_id == Meta.id)
               .filter(MetaConcluida.aluno_id == aluno_id).scalar())


def metas_do_aluno(db: Session, aluno: Usuario) -> list[Meta]:
    """Metas ativas que valem para o aluno: da escola toda, das turmas dele ou so dele."""
    turmas = [t for (t,) in db.query(UsuarioTurma.turma_id).filter_by(usuario_id=aluno.id)]
    return list(db.query(Meta).filter(
        Meta.escola_id == aluno.escola_id, Meta.ativa.is_(True),
        or_(and_(Meta.turma_id.is_(None), Meta.aluno_id.is_(None)), Meta.turma_id.in_(turmas), Meta.aluno_id == aluno.id),
    ).order_by(Meta.inicio.desc()))


def progresso(db: Session, meta: Meta, aluno_id) -> float:
    """Quanto o aluno ja fez, na mesma unidade de meta.alvo (quantidade ou percentual)."""
    if meta.tipo == "DOMINIO_COMPETENCIA":  # acumulado, nao depende do periodo
        d = (db.query(DominioAluno.percentual_dominio).join(Tema, Tema.id == DominioAluno.tema_id)
             .filter(DominioAluno.aluno_id == aluno_id, Tema.materia_id == meta.materia_id,
                     Tema.atividade_id.is_(None), Tema.habilidade_codigo == meta.competencia).scalar())
        return float(d or 0)

    q = db.query(Submissao, Atividade).join(Atividade, Atividade.id == Submissao.atividade_id).filter(
        Submissao.aluno_id == aluno_id, Submissao.texto_confirmado.isnot(None),
        Submissao.criado_em >= datetime.combine(meta.inicio, time.min))
    if meta.fim:
        q = q.filter(Submissao.criado_em <= datetime.combine(meta.fim, time.max))
    if meta.materia_id:
        q = q.filter(Atividade.materia_id == meta.materia_id)

    if meta.tipo == "ENTREGAS":
        return float(q.count())
    if meta.tipo == "ENTREGAS_NO_PRAZO":
        return float(q.filter(Atividade.prazo.isnot(None), cast(Submissao.criado_em, SADate) <= Atividade.prazo).count())

    # NOTA_ATIVIDADE / MEDIA_MATERIA: percentual da nota aprovada sobre o valor da atividade
    pcts = [float(c.nota_professor) / float(a.valor_total or 1000) * 100
            for s, a in q.all() for c in [db.query(Correcao).filter_by(submissao_id=s.id).first()]
            if c and c.status == StatusCorrecaoEnum.APROVADA and c.nota_professor is not None]
    if not pcts:
        return 0.0
    return max(pcts) if meta.tipo == "NOTA_ATIVIDADE" else sum(pcts) / len(pcts)


def avaliar_metas(db: Session, aluno_id) -> list[Meta]:
    """Registra as metas que o aluno acabou de cumprir (sem commit). Repetir a chamada nao duplica."""
    aluno = db.get(Usuario, aluno_id)
    if not aluno or aluno.perfil != PerfilEnum.ALUNO:
        return []
    feitas = {m for (m,) in db.query(MetaConcluida.meta_id).filter_by(aluno_id=aluno_id)}
    hoje, novas = date.today(), []
    for meta in metas_do_aluno(db, aluno):
        if meta.id in feitas or meta.inicio > hoje:
            continue
        if meta.tipo == "DOMINIO_COMPETENCIA" and meta.fim and hoje > meta.fim:
            continue
        if progresso(db, meta, aluno_id) >= float(meta.alvo):
            db.add(MetaConcluida(meta_id=meta.id, aluno_id=aluno_id))
            novas.append(meta)
    db.flush()
    return novas


def avaliar_seguro(aluno_id) -> None:
    """Chamada depois de um envio/aprovacao: sessao propria e nunca derruba a requisicao."""
    try:
        with SessionLocal() as db:
            avaliar_metas(db, aluno_id)
            db.commit()
    except Exception:
        logger.exception("falha ao avaliar metas")
