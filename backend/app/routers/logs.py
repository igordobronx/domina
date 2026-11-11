"""Consulta dos logs.

- /logs/seguranca e /logs/integridade: SO o administrador da plataforma.
- /logs/auditoria: o admin ve todas as escolas (com IP); o gestor ve so a propria (sem IP). Filtro no backend.
- Quem consulta tambem fica registrado na auditoria (acao CONSULTAR): ver o log e uma acao auditavel.
Somente leitura: nao ha rota para editar ou apagar log (a retencao roda como job, fora da API).
"""
import uuid
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auditoria import registrar, verificar_auditoria
from app.auth.dependencies import escola_do_escopo, exigir_perfil
from app.database import get_db
from app.models.enum import PerfilEnum
from app.models.usuario import AuditLog, Escola, EventoSeguranca, Usuario
from app.schemas.logs import AuditoriaResponse, EventoSegurancaResponse, IntegridadeResponse
from app.seguranca import verificar_cadeia

router = APIRouter(prefix="/logs", tags=["logs"])
so_admin = Depends(exigir_perfil(PerfilEnum.ADMIN))
admin_ou_gestor = Depends(exigir_perfil(PerfilEnum.ADMIN, PerfilEnum.GESTOR))


def _periodo(consulta, coluna, de: date | None, ate: date | None):
    if de:
        consulta = consulta.filter(coluna >= datetime.combine(de, time.min))
    if ate:
        consulta = consulta.filter(coluna < datetime.combine(ate + timedelta(days=1), time.min))
    return consulta


@router.get("/seguranca", response_model=list[EventoSegurancaResponse])
def logs_seguranca(
    tipo: str | None = None, ip: str | None = None, de: date | None = None, ate: date | None = None,
    limite: int = Query(100, ge=1, le=500), pular: int = Query(0, ge=0),
    usuario: Usuario = so_admin, db: Session = Depends(get_db),
):
    q = _periodo(db.query(EventoSeguranca, Usuario.nome).outerjoin(Usuario, Usuario.id == EventoSeguranca.usuario_id),
                 EventoSeguranca.criado_em, de, ate)
    if tipo:
        q = q.filter(EventoSeguranca.tipo == tipo)
    if ip:
        q = q.filter(EventoSeguranca.ip == ip)
    linhas = q.order_by(EventoSeguranca.criado_em.desc(), EventoSeguranca.seq.desc()).offset(pular).limit(limite).all()
    registrar(db, usuario.id, "CONSULTAR", "LogSeguranca", usuario.id)
    db.commit()
    return [EventoSegurancaResponse(
        seq=e.seq, criado_em=e.criado_em, tipo=e.tipo, usuario=nome, email_tentado=e.email_tentado,
        ip=e.ip, request_id=e.request_id, detalhe=e.detalhe,
    ) for e, nome in linhas]


@router.get("/auditoria", response_model=list[AuditoriaResponse])
def logs_auditoria(
    acao: str | None = None, escola_id: uuid.UUID | None = None, de: date | None = None, ate: date | None = None,
    limite: int = Query(100, ge=1, le=500), pular: int = Query(0, ge=0),
    usuario: Usuario = admin_ou_gestor, db: Session = Depends(get_db),
):
    q = _periodo(
        db.query(AuditLog, Usuario.nome, Escola.nome)
        .outerjoin(Usuario, Usuario.id == AuditLog.usuario_id).outerjoin(Escola, Escola.id == AuditLog.escola_id),
        AuditLog.criado_em, de, ate,
    )
    if usuario.perfil == PerfilEnum.GESTOR:
        # gestor: sempre a propria escola, mesmo que mande outro escola_id (escola_do_escopo da 404)
        q = q.filter(AuditLog.escola_id == escola_do_escopo(db, usuario, escola_id))
    elif escola_id:
        q = q.filter(AuditLog.escola_id == escola_id)
    if acao:
        q = q.filter(AuditLog.acao == acao)
    linhas = q.order_by(AuditLog.criado_em.desc(), AuditLog.seq.desc()).offset(pular).limit(limite).all()
    registrar(db, usuario.id, "CONSULTAR", "LogAuditoria", usuario.id)
    db.commit()
    admin = usuario.perfil == PerfilEnum.ADMIN
    return [AuditoriaResponse(
        seq=a.seq, criado_em=a.criado_em, usuario=nome, escola=escola, acao=a.acao, entidade=a.entidade,
        entidade_id=a.entidade_id, resultado=a.resultado,
        ip=a.ip if admin else None, request_id=a.request_id if admin else None,
    ) for a, nome, escola in linhas]


@router.get("/integridade", response_model=IntegridadeResponse)
def integridade(usuario: Usuario = so_admin, db: Session = Depends(get_db)):
    s_ok, s_msg = verificar_cadeia(db)
    a_ok, a_msg = verificar_auditoria(db)
    registrar(db, usuario.id, "VERIFICAR_INTEGRIDADE", "Log", usuario.id, resultado="OK" if s_ok and a_ok else "ALERTA")
    db.commit()
    return IntegridadeResponse(seguranca_ok=s_ok, seguranca=s_msg, auditoria_ok=a_ok, auditoria=a_msg)
