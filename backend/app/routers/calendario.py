"""Calendario da escola. Fonte unica: a tabela `evento` (+ prazos das atividades + feriados).

Quem ve o que (decidido AQUI, no backend):
- ALUNO/PROFESSOR: eventos da escola toda + os das proprias turmas, e os prazos das proprias turmas.
- GESTOR/ADMIN: tudo da escola (o admin informa escola_id).
- Lembrete PESSOAL do aluno (evento criado por um aluno): so o proprio aluno ve, edita e apaga.
"""
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.dependencies import escola_do_escopo, exigir_perfil, get_current_user
from app.database import get_db
from app.feriados import feriados
from app.models.enum import PerfilEnum
from app.metas import metas_do_aluno
from app.models.usuario import Atividade, Evento, MetaConcluida, Turma, Usuario, UsuarioTurma
from app.routers.metas import metas_da_equipe
from app.schemas.calendario import EventoRequest, ItemCalendario

router = APIRouter(tags=["calendario"])
GERENTES = (PerfilEnum.GESTOR, PerfilEnum.ADMIN)
PODE_CRIAR = exigir_perfil(PerfilEnum.ALUNO, PerfilEnum.PROFESSOR, PerfilEnum.GESTOR, PerfilEnum.ADMIN)


def _escola(db: Session, usuario: Usuario, escola_id: uuid.UUID | None) -> uuid.UUID:
    if usuario.perfil in GERENTES:
        return escola_do_escopo(db, usuario, escola_id)
    return usuario.escola_id


def _minhas_turmas(db: Session, usuario: Usuario) -> set[uuid.UUID]:
    return {t for (t,) in db.query(UsuarioTurma.turma_id).filter_by(usuario_id=usuario.id)}


def _pode_mexer(usuario: Usuario, evento: Evento) -> bool:
    # professor e aluno so mexem no que eles mesmos criaram
    return usuario.perfil in GERENTES or evento.criado_por == usuario.id


def _de_alunos(db: Session):
    # ponytail: "pessoal" = criado por um aluno (sem coluna nova nem migration); se um dia o professor
    # tambem quiser lembrete pessoal, vira uma coluna `pessoal` em `evento`.
    return db.query(Usuario.id).filter(Usuario.perfil == PerfilEnum.ALUNO)


@router.get("/calendario", response_model=list[ItemCalendario])
def ver_calendario(
    de: date = Query(default_factory=lambda: date.today().replace(day=1)),
    ate: date | None = None,
    escola_id: uuid.UUID | None = None,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ate = ate or de + timedelta(days=42)
    if ate < de or (ate - de).days > 400:
        raise HTTPException(422, "Período inválido (máximo de ~13 meses).")
    escola = _escola(db, usuario, escola_id)
    gerente = usuario.perfil in GERENTES
    turmas = None if gerente else _minhas_turmas(db, usuario)
    nomes = {t.id: t.nome for t in db.query(Turma).filter_by(escola_id=escola)}

    eventos = db.query(Evento).filter(
        Evento.escola_id == escola, Evento.inicio <= ate,
        or_(Evento.fim >= de, (Evento.fim.is_(None)) & (Evento.inicio >= de)),
    )
    if turmas is not None:
        eventos = eventos.filter(or_(Evento.turma_id.is_(None), Evento.turma_id.in_(turmas)))
    # lembrete pessoal de aluno: so o dono ve (nem colega, nem professor, nem gestor)
    eventos = eventos.filter(or_(Evento.criado_por == usuario.id, ~Evento.criado_por.in_(_de_alunos(db))))
    itens = [ItemCalendario(
        id=f"evento:{e.id}", origem="evento", titulo=e.titulo, descricao=e.descricao, tipo=e.tipo,
        inicio=e.inicio, fim=e.fim, turma_id=e.turma_id, turma=nomes.get(e.turma_id),
        editavel=_pode_mexer(usuario, e),
    ) for e in eventos]

    prazos = db.query(Atividade).join(Turma, Turma.id == Atividade.turma_id).filter(
        Turma.escola_id == escola, Atividade.arquivada.is_(False), Atividade.prazo >= de, Atividade.prazo <= ate)
    if turmas is not None:
        prazos = prazos.filter(Atividade.turma_id.in_(turmas))
    itens += [ItemCalendario(
        id=f"prazo:{a.id}", origem="prazo", titulo=f"Entrega: {a.titulo}", tipo="ENTREGA",
        inicio=a.prazo, turma_id=a.turma_id, turma=nomes.get(a.turma_id),
    ) for a in prazos]

    # fim das metas (aluno: so as dele que ainda nao concluiu; professor/gestor: as que enxergam)
    if usuario.perfil == PerfilEnum.ALUNO:
        feitas = {m for (m,) in db.query(MetaConcluida.meta_id).filter_by(aluno_id=usuario.id)}
        metas = [m for m in metas_do_aluno(db, usuario) if m.id not in feitas]
    elif usuario.perfil in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        metas = metas_da_equipe(db, usuario).all()
    else:
        metas = []  # admin nao tem metas (sao da escola)
    itens += [ItemCalendario(
        id=f"meta:{m.id}", origem="meta", titulo=f"Fim da meta: {m.titulo}", descricao=f"Vale {m.pontos} pontos",
        tipo="META", inicio=m.fim, turma_id=m.turma_id, turma=nomes.get(m.turma_id),
    ) for m in metas if m.fim and de <= m.fim <= ate]

    for ano in range(de.year, ate.year + 1):
        itens += [ItemCalendario(id=f"feriado:{d}", origem="feriado", titulo=n, tipo="FERIADO", inicio=d)
                  for d, n in feriados(ano) if de <= d <= ate]
    return sorted(itens, key=lambda i: (i.inicio, i.titulo))


def _validar_turma(db: Session, usuario: Usuario, escola: uuid.UUID, turma_id: uuid.UUID | None) -> None:
    if turma_id is None:
        if usuario.perfil == PerfilEnum.PROFESSOR:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Professor cria eventos só para as suas turmas.")
        return
    turma = db.get(Turma, turma_id)
    if not turma or turma.escola_id != escola:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if usuario.perfil == PerfilEnum.PROFESSOR and turma_id not in _minhas_turmas(db, usuario):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")


@router.post("/eventos", response_model=ItemCalendario, status_code=status.HTTP_201_CREATED)
def criar_evento(payload: EventoRequest, escola_id: uuid.UUID | None = None,
                 usuario: Usuario = Depends(PODE_CRIAR), db: Session = Depends(get_db)):
    escola = _escola(db, usuario, escola_id)
    if usuario.perfil == PerfilEnum.ALUNO:
        payload.turma_id = None  # lembrete pessoal: nunca vai para turma nenhuma
    _validar_turma(db, usuario, escola, payload.turma_id)
    e = Evento(escola_id=escola, criado_por=usuario.id, titulo=payload.titulo.strip(), descricao=payload.descricao,
               tipo=payload.tipo, inicio=payload.inicio, fim=payload.fim, turma_id=payload.turma_id)
    db.add(e)
    db.commit()
    return _item(db, usuario, e)


def _item(db: Session, usuario: Usuario, e: Evento) -> ItemCalendario:
    turma = db.get(Turma, e.turma_id) if e.turma_id else None
    return ItemCalendario(id=f"evento:{e.id}", origem="evento", titulo=e.titulo, descricao=e.descricao, tipo=e.tipo,
                          inicio=e.inicio, fim=e.fim, turma_id=e.turma_id, turma=turma.nome if turma else None,
                          editavel=_pode_mexer(usuario, e))


def _evento_do_usuario(db: Session, usuario: Usuario, evento_id: uuid.UUID) -> Evento:
    e = db.get(Evento, evento_id)
    # evento de outra escola = 404 (nao revela que existe), igual ao resto do RBAC
    alheio_pessoal = e and e.criado_por != usuario.id and db.query(Usuario.perfil).filter_by(
        id=e.criado_por).scalar() == PerfilEnum.ALUNO  # lembrete pessoal de outro = nao existe
    if not e or alheio_pessoal or (usuario.perfil != PerfilEnum.ADMIN and e.escola_id != usuario.escola_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento não encontrado.")
    if not _pode_mexer(usuario, e):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não pode alterar este evento.")
    return e


@router.put("/eventos/{evento_id}", response_model=ItemCalendario)
def editar_evento(evento_id: uuid.UUID, payload: EventoRequest,
                  usuario: Usuario = Depends(PODE_CRIAR), db: Session = Depends(get_db)):
    e = _evento_do_usuario(db, usuario, evento_id)
    if usuario.perfil == PerfilEnum.ALUNO:
        payload.turma_id = None
    _validar_turma(db, usuario, e.escola_id, payload.turma_id)
    e.titulo, e.descricao, e.tipo = payload.titulo.strip(), payload.descricao, payload.tipo
    e.inicio, e.fim, e.turma_id = payload.inicio, payload.fim, payload.turma_id
    db.commit()
    return _item(db, usuario, e)


@router.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_evento(evento_id: uuid.UUID, usuario: Usuario = Depends(PODE_CRIAR), db: Session = Depends(get_db)):
    db.delete(_evento_do_usuario(db, usuario, evento_id))
    db.commit()
