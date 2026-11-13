"""Niveis e metas. Professor/gestor criam; o aluno cumpre. Quem ve o que (decidido AQUI):
- ALUNO: so as metas que valem para ele e o proprio nivel. Nunca ve o ranking.
- PROFESSOR: cria metas para as proprias turmas ou para um aluno delas; ve o ranking das suas turmas.
- GESTOR: cria para qualquer turma/aluno da escola ou para a escola toda; ve o ranking da escola.
"""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import exigir_perfil
from app.database import get_db
from app.metas import avaliar_metas, metas_do_aluno, nivel_de, pontos_do_aluno, progresso
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.models.usuario import Materia, Meta, MetaConcluida, Turma, Usuario, UsuarioTurma
from app.schemas.metas import (
    MetaAlunoResponse, MetaEditRequest, MetaRequest, MetaResponse, MinhasMetasResponse, NivelResponse, RankingItem,
)

router = APIRouter(tags=["metas"])
EQUIPE = exigir_perfil(PerfilEnum.PROFESSOR, PerfilEnum.GESTOR)
APENAS_ALUNO = exigir_perfil(PerfilEnum.ALUNO)


def _turmas_do_professor(db: Session, usuario: Usuario) -> set[uuid.UUID]:
    return {t for (t,) in db.query(UsuarioTurma.turma_id).filter_by(usuario_id=usuario.id, papel=UsuarioTurmaPapelEnum.PROFESSOR)}


def _alunos_das_turmas(db: Session, turmas) -> list[Usuario]:
    return list(db.query(Usuario).join(UsuarioTurma, UsuarioTurma.usuario_id == Usuario.id).filter(
        UsuarioTurma.turma_id.in_(list(turmas)), UsuarioTurma.papel == UsuarioTurmaPapelEnum.ALUNO,
    ).distinct().order_by(Usuario.nome))


def _alunos_da_escola(db: Session, escola_id) -> list[Usuario]:
    return list(db.query(Usuario).filter_by(escola_id=escola_id, perfil=PerfilEnum.ALUNO).order_by(Usuario.nome))


def _escopo(meta: Meta) -> str:
    return "ALUNO" if meta.aluno_id else "TURMA" if meta.turma_id else "ESCOLA"


def _pode_editar(usuario: Usuario, meta: Meta) -> bool:
    return usuario.perfil == PerfilEnum.GESTOR or meta.criado_por == usuario.id


def _resposta(db: Session, usuario: Usuario, meta: Meta) -> MetaResponse:
    if meta.aluno_id:
        nome, alvo = db.get(Usuario, meta.aluno_id).nome, 1
    elif meta.turma_id:
        nome, alvo = db.get(Turma, meta.turma_id).nome, len(_alunos_das_turmas(db, [meta.turma_id]))
    else:
        nome, alvo = "Escola toda", len(_alunos_da_escola(db, meta.escola_id))
    return MetaResponse(
        id=meta.id, titulo=meta.titulo, descricao=meta.descricao, tipo=meta.tipo, alvo=float(meta.alvo),
        materia_id=meta.materia_id, competencia=meta.competencia, pontos=meta.pontos, inicio=meta.inicio, fim=meta.fim,
        escopo=_escopo(meta), escopo_nome=nome, alunos_alvo=alvo,
        concluidos=db.query(func.count(MetaConcluida.aluno_id)).filter_by(meta_id=meta.id).scalar(),
        pode_editar=_pode_editar(usuario, meta),
    )


def _minha(db: Session, usuario: Usuario, meta_id: uuid.UUID) -> Meta:
    meta = db.get(Meta, meta_id)
    if not meta or not meta.ativa or meta.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meta não encontrada.")
    if not _pode_editar(usuario, meta):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só quem criou a meta (ou o gestor) pode mexer nela.")
    return meta


@router.post("/metas", response_model=MetaResponse, status_code=status.HTTP_201_CREATED)
def criar_meta(payload: MetaRequest, usuario: Usuario = Depends(EQUIPE), db: Session = Depends(get_db)):
    professor = usuario.perfil == PerfilEnum.PROFESSOR
    if payload.aluno_id:
        aluno = db.get(Usuario, payload.aluno_id)
        if not aluno or aluno.perfil != PerfilEnum.ALUNO or aluno.escola_id != usuario.escola_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
        if professor and not {t for (t,) in db.query(UsuarioTurma.turma_id).filter_by(usuario_id=aluno.id)} & _turmas_do_professor(db, usuario):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")  # nao e aluno dele
    elif payload.turma_id:
        turma = db.get(Turma, payload.turma_id)
        if not turma or turma.escola_id != usuario.escola_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
        if professor and turma.id not in _turmas_do_professor(db, usuario):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Você não leciona na turma {turma.nome}.")
    elif professor:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o gestor cria metas para a escola toda.")
    if payload.materia_id:
        materia = db.get(Materia, payload.materia_id)
        if not materia or materia.escola_id != usuario.escola_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
        if payload.tipo == "DOMINIO_COMPETENCIA" and not materia.tipo.value.startswith("REDACAO"):
            raise HTTPException(422, "Domínio por competência só existe em matéria de redação.")

    meta = Meta(
        escola_id=usuario.escola_id, criado_por=usuario.id, titulo=payload.titulo.strip(),
        descricao=(payload.descricao or "").strip() or None, tipo=payload.tipo, alvo=payload.alvo,
        materia_id=payload.materia_id, competencia=payload.competencia, pontos=payload.pontos,
        inicio=payload.inicio or date.today(), fim=payload.fim, turma_id=payload.turma_id, aluno_id=payload.aluno_id,
    )
    db.add(meta)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "Meta", meta.id)
    db.commit()
    return _resposta(db, usuario, meta)


@router.get("/metas", response_model=list[MetaResponse])
def listar_metas(usuario: Usuario = Depends(EQUIPE), db: Session = Depends(get_db)):
    q = db.query(Meta).filter(Meta.escola_id == usuario.escola_id, Meta.ativa.is_(True))
    if usuario.perfil == PerfilEnum.PROFESSOR:
        turmas = _turmas_do_professor(db, usuario)
        meus_alunos = [a.id for a in _alunos_das_turmas(db, turmas)] if turmas else []
        q = q.filter(or_(Meta.criado_por == usuario.id, Meta.turma_id.in_(list(turmas)), Meta.aluno_id.in_(meus_alunos),
                         (Meta.turma_id.is_(None)) & (Meta.aluno_id.is_(None))))
    return [_resposta(db, usuario, m) for m in q.order_by(Meta.inicio.desc())]


@router.put("/metas/{meta_id}", response_model=MetaResponse)
def editar_meta(meta_id: uuid.UUID, payload: MetaEditRequest, usuario: Usuario = Depends(EQUIPE), db: Session = Depends(get_db)):
    meta = _minha(db, usuario, meta_id)
    if payload.titulo is not None:
        meta.titulo = payload.titulo.strip()
    if "descricao" in payload.model_fields_set:
        meta.descricao = (payload.descricao or "").strip() or None
    if "fim" in payload.model_fields_set:
        if payload.fim and payload.fim < meta.inicio:
            raise HTTPException(422, "O fim não pode ser antes do início.")
        meta.fim = payload.fim
    if payload.alvo is not None or payload.pontos is not None:
        if db.query(MetaConcluida).filter_by(meta_id=meta.id).first():
            raise HTTPException(status.HTTP_409_CONFLICT,
                                "Alguém já concluiu esta meta: só título, descrição e fim podem mudar. Crie uma nova meta.")
        if payload.alvo is not None:
            meta.alvo = payload.alvo
        if payload.pontos is not None:
            meta.pontos = payload.pontos
    registrar(db, usuario.id, "EDITAR", "Meta", meta.id)
    db.commit()
    return _resposta(db, usuario, meta)


@router.delete("/metas/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_meta(meta_id: uuid.UUID, usuario: Usuario = Depends(EQUIPE), db: Session = Depends(get_db)):
    meta = _minha(db, usuario, meta_id)
    meta.ativa = False  # arquiva: os pontos de quem ja concluiu continuam
    registrar(db, usuario.id, "ARQUIVAR", "Meta", meta.id)
    db.commit()


@router.get("/metas/minhas", response_model=MinhasMetasResponse)
def minhas_metas(usuario: Usuario = Depends(APENAS_ALUNO), db: Session = Depends(get_db)):
    avaliar_metas(db, usuario.id)  # rede de seguranca: garante o estado certo mesmo se algum gancho falhar
    db.commit()
    feitas = {m.meta_id: m.concluida_em for m in db.query(MetaConcluida).filter_by(aluno_id=usuario.id)}
    hoje, metas = date.today(), []
    for m in metas_do_aluno(db, usuario):
        if m.id in feitas:
            st = "CONCLUIDA"
        elif m.inicio > hoje:
            st = "FUTURA"
        elif m.fim and m.fim < hoje:
            st = "ENCERRADA"
        else:
            st = "EM_ANDAMENTO"
        metas.append(MetaAlunoResponse(
            id=m.id, titulo=m.titulo, descricao=m.descricao, tipo=m.tipo, alvo=float(m.alvo),
            progresso=min(round(progresso(db, m, usuario.id), 1), float(m.alvo)) if st != "FUTURA" else 0,
            pontos=m.pontos, inicio=m.inicio, fim=m.fim, status=st, concluida_em=feitas.get(m.id),
        ))
    return MinhasMetasResponse(nivel=NivelResponse(**nivel_de(pontos_do_aluno(db, usuario.id))), metas=metas)


# ranking por PONTOS (nunca por nota), so para quem acompanha os alunos
@router.get("/metas/ranking", response_model=list[RankingItem])
def ranking(turma_id: uuid.UUID | None = None, usuario: Usuario = Depends(EQUIPE), db: Session = Depends(get_db)):
    if usuario.perfil == PerfilEnum.PROFESSOR:
        turmas = _turmas_do_professor(db, usuario)
        if turma_id is not None and turma_id not in turmas:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
        alunos = _alunos_das_turmas(db, [turma_id] if turma_id else turmas) if turmas else []
    elif turma_id is not None:
        turma = db.get(Turma, turma_id)
        if not turma or turma.escola_id != usuario.escola_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
        alunos = _alunos_das_turmas(db, [turma_id])
    else:
        alunos = _alunos_da_escola(db, usuario.escola_id)
    pontos = dict(db.query(MetaConcluida.aluno_id, func.sum(Meta.pontos)).join(Meta, Meta.id == MetaConcluida.meta_id)
                  .filter(MetaConcluida.aluno_id.in_([a.id for a in alunos])).group_by(MetaConcluida.aluno_id).all())
    qtd = dict(db.query(MetaConcluida.aluno_id, func.count(MetaConcluida.meta_id))
               .filter(MetaConcluida.aluno_id.in_([a.id for a in alunos])).group_by(MetaConcluida.aluno_id).all())
    itens = []
    for a in alunos:
        n = nivel_de(int(pontos.get(a.id, 0)))
        itens.append(RankingItem(aluno_id=a.id, nome=a.nome, pontos=n["pontos"], nivel=n["nivel"], nome_nivel=n["nome"],
                                 metas_concluidas=int(qtd.get(a.id, 0))))
    return sorted(itens, key=lambda i: (-i.pontos, i.nome))
