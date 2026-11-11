"""Resumo financeiro e de consumo por instituicao (gestor: so a propria; admin: qualquer uma + total)."""
import os
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.auth.dependencies import escola_do_escopo, exigir_perfil
from app.database import get_db
from app.models.enum import PerfilEnum, TipoEnvioEnum
from app.models.usuario import (
    AgenteExecucao, CustoUso, DocumentoBase, Escola, Materia, Submissao, Tema, Turma, Usuario,
)
from app.schemas.painel import ResumoEscola, ResumoPlataforma

router = APIRouter(prefix="/painel", tags=["painel"])


def _periodo(mes: str | None) -> tuple[str, datetime, datetime]:
    mes = mes or date.today().strftime("%Y-%m")
    try:
        inicio = datetime.strptime(mes, "%Y-%m")
    except ValueError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "mes deve ser AAAA-MM.")
    fim = datetime(inicio.year + inicio.month // 12, inicio.month % 12 + 1, 1)
    return mes, inicio, fim


def _resumo(db: Session, escola: Escola, mes: str, inicio: datetime, fim: datetime) -> ResumoEscola:
    de_alunos = Usuario.escola_id == escola.id
    contar = lambda perfil: db.query(func.count(Usuario.id)).filter(de_alunos, Usuario.perfil == perfil).scalar()
    no_mes = (Submissao.criado_em >= inicio, Submissao.criado_em < fim)

    envios = db.query(Submissao).join(Usuario, Usuario.id == Submissao.aluno_id).filter(de_alunos)
    alunos_ativos = (
        db.query(func.count(distinct(Submissao.aluno_id)))
        .join(Usuario, Usuario.id == Submissao.aluno_id).filter(de_alunos, *no_mes).scalar()
    )
    execucoes = (
        db.query(func.count(AgenteExecucao.id))
        .join(Submissao, Submissao.id == AgenteExecucao.submissao_id)
        .join(Usuario, Usuario.id == Submissao.aluno_id)
        .filter(de_alunos, AgenteExecucao.criado_em >= inicio, AgenteExecucao.criado_em < fim).scalar()
    )
    uso = db.query(CustoUso).filter_by(escola_id=escola.id, mes_referencia=mes).first()

    # ponytail: soma o tamanho dos arquivos um a um (ok para o piloto); guardar o tamanho na
    # tabela se o numero de envios crescer muito
    armazenamento = db.query(func.coalesce(func.sum(DocumentoBase.tamanho_bytes), 0)).join(
        Materia, Materia.id == DocumentoBase.materia_id).filter(Materia.escola_id == escola.id).scalar()
    figuras = db.query(Tema.imagem).join(Materia, Materia.id == Tema.materia_id).filter(
        Materia.escola_id == escola.id, Tema.imagem.isnot(None))
    for (caminho,) in figuras:
        if os.path.isfile(caminho):
            armazenamento += os.path.getsize(caminho)
    for s in envios.filter(Submissao.tipo_envio != TipoEnvioEnum.TEXTO):
        if os.path.isfile(s.conteudo_bruto):
            armazenamento += os.path.getsize(s.conteudo_bruto)

    receita = float(escola.plano_fixo) + float(escola.valor_por_aluno) * alunos_ativos
    custo = float(uso.custo_estimado) if uso else 0.0
    return ResumoEscola(
        escola_id=escola.id, escola_nome=escola.nome, ativa=escola.ativa, mes=mes,
        alunos_cadastrados=contar(PerfilEnum.ALUNO), professores=contar(PerfilEnum.PROFESSOR),
        turmas=db.query(func.count(Turma.id)).filter(Turma.escola_id == escola.id).scalar(),
        alunos_ativos=alunos_ativos,
        submissoes=envios.filter(*no_mes).count(), execucoes_agente=execucoes,
        tokens_llm=uso.tokens_llm if uso else 0, chamadas_ocr=uso.chamadas_ocr if uso else 0,
        armazenamento_bytes=int(armazenamento),
        receita=round(receita, 2), custo_ia=round(custo, 4), margem=round(receita - custo, 2),
    )


@router.get("/escola", response_model=ResumoEscola)
def resumo_da_escola(
    escola_id: uuid.UUID | None = None, mes: str | None = None,
    usuario: Usuario = Depends(exigir_perfil(PerfilEnum.GESTOR, PerfilEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    # gestor: a escola vem do token, nunca do pedido. admin: ?escola_id= obrigatorio.
    escola = db.get(Escola, escola_do_escopo(db, usuario, escola_id))
    return _resumo(db, escola, *_periodo(mes))


@router.get("/plataforma", response_model=ResumoPlataforma)
def resumo_da_plataforma(
    mes: str | None = None, usuario: Usuario = Depends(exigir_perfil(PerfilEnum.ADMIN)),
    db: Session = Depends(get_db),
):
    periodo = _periodo(mes)
    escolas = [_resumo(db, e, *periodo) for e in db.query(Escola).order_by(Escola.nome) if e.ativa]
    campos = ("alunos_cadastrados", "professores", "turmas", "alunos_ativos", "submissoes",
              "execucoes_agente", "tokens_llm", "chamadas_ocr", "armazenamento_bytes", "receita", "custo_ia", "margem")
    totais = {c: round(sum(getattr(e, c) for e in escolas), 4) for c in campos}
    return ResumoPlataforma(mes=periodo[0], escolas_ativas=len(escolas), totais=totais, escolas=escolas)
