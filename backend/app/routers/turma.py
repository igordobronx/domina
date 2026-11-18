import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import escola_do_escopo, get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.auditoria import registrar
from app.models.usuario import Materia, ProfessorMateria, Turma, Usuario, UsuarioTurma
from app.routers.submissoes import _na_turma, _professor_da_turma
from app.schemas.turma import (
    CriarTurmaRequest, DefinirMateriasRequest, MatricularRequest, MembroTurmaResponse, ProfessorMateriaResponse,
    TurmaResponse,
)

router = APIRouter(prefix="/turmas", tags=["turmas"])


def _so_gestor(usuario: Usuario) -> None:
    if usuario.perfil != PerfilEnum.GESTOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "somente gestores podem gerenciar turmas")


@router.post("", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
def criar_turma(payload: CriarTurmaRequest, usuario_atual: Usuario = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    _so_gestor(usuario_atual)

    turma = Turma(nome=payload.nome, ano=payload.ano, escola_id=usuario_atual.escola_id)
    db.add(turma)
    db.commit()
    db.refresh(turma)
    return turma


# literal: GET /turmas/minhas antes de um eventual GET /turmas/{turma_id} evitaria o mesmo
# problema de roteamento ja visto em /submissoes/minhas; nao ha essa rota ainda, mas o padrao se mantem
@router.get("/minhas", response_model=list[TurmaResponse])
def minhas_turmas(escola_id: uuid.UUID | None = None, usuario_atual: Usuario = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    # gestor: todas as da propria escola. admin: as da escola pedida (?escola_id=)
    if usuario_atual.perfil in (PerfilEnum.GESTOR, PerfilEnum.ADMIN):
        turmas = db.query(Turma).filter_by(escola_id=escola_do_escopo(db, usuario_atual, escola_id))
    elif usuario_atual.perfil == PerfilEnum.PROFESSOR:
        turma_ids = [
            ut.turma_id for ut in
            db.query(UsuarioTurma).filter_by(usuario_id=usuario_atual.id, papel=UsuarioTurmaPapelEnum.PROFESSOR)
        ]
        turmas = db.query(Turma).filter(Turma.id.in_(turma_ids))
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores usam esta rota.")
    return list(turmas)


# literal: GET /turmas/minhas fica antes e nao conflita com estas, que tem 2 segmentos
@router.get("/{turma_id}/membros", response_model=list[MembroTurmaResponse])
def membros_turma(turma_id: uuid.UUID, usuario_atual: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    turma = db.get(Turma, turma_id)
    if not turma or turma.escola_id != usuario_atual.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if usuario_atual.perfil not in (PerfilEnum.GESTOR, PerfilEnum.PROFESSOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem os membros da turma.")

    linhas = (
        db.query(Usuario, UsuarioTurma.papel)
        .join(UsuarioTurma, UsuarioTurma.usuario_id == Usuario.id)
        .filter(UsuarioTurma.turma_id == turma_id)
    )
    return [
        MembroTurmaResponse(id=u.id, nome=u.nome, email=u.email, papel=papel.value)
        for u, papel in linhas
    ]


@router.post("/{turma_id}/matricular", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
def matricular(turma_id: uuid.UUID, payload: MatricularRequest, usuario_atual: Usuario = Depends(get_current_user),
                db: Session = Depends(get_db)):
    turma = db.get(Turma, turma_id)
    if not turma or turma.escola_id != usuario_atual.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if usuario_atual.perfil == PerfilEnum.PROFESSOR:
        # professor matricula so ALUNOS e so nas turmas em que ele da aula
        if payload.papel != "ALUNO" or not _professor_da_turma(db, usuario_atual, turma.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "O professor só matricula alunos nas próprias turmas.")
    else:
        _so_gestor(usuario_atual)

    aluno_ou_professor = db.get(Usuario, payload.usuario_id)
    if not aluno_ou_professor or aluno_ou_professor.escola_id != usuario_atual.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado.")
    if aluno_ou_professor.perfil != PerfilEnum(payload.papel):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Papel não corresponde ao perfil do usuário.")

    if _na_turma(db, aluno_ou_professor.id, turma.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Usuário já matriculado nesta turma.")

    db.add(UsuarioTurma(usuario_id=aluno_ou_professor.id, turma_id=turma.id,
                         papel=UsuarioTurmaPapelEnum(payload.papel)))
    db.commit()
    return turma


# quem leciona qual materia nesta turma: so o gestor define; o professor so ve as dele
@router.get("/{turma_id}/materias-dos-professores", response_model=list[ProfessorMateriaResponse])
def materias_dos_professores(turma_id: uuid.UUID, usuario_atual: Usuario = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    turma = db.get(Turma, turma_id)
    if not turma or turma.escola_id != usuario_atual.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if usuario_atual.perfil not in (PerfilEnum.GESTOR, PerfilEnum.PROFESSOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem isto.")
    q = db.query(ProfessorMateria).filter_by(turma_id=turma.id)
    if usuario_atual.perfil == PerfilEnum.PROFESSOR:
        q = q.filter_by(usuario_id=usuario_atual.id)
    return [ProfessorMateriaResponse(professor_id=r.usuario_id, materia_id=r.materia_id) for r in q]


@router.put("/{turma_id}/professores/{professor_id}/materias", response_model=list[ProfessorMateriaResponse])
def definir_materias_do_professor(turma_id: uuid.UUID, professor_id: uuid.UUID, payload: DefinirMateriasRequest,
                                  usuario_atual: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_gestor(usuario_atual)
    turma = db.get(Turma, turma_id)
    if not turma or turma.escola_id != usuario_atual.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    professor = db.get(Usuario, professor_id)
    if not professor or not _professor_da_turma(db, professor, turma.id) or professor.escola_id != turma.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professor não encontrado nesta turma.")
    ids = set(payload.materia_ids)
    achadas = {m for (m,) in db.query(Materia.id).filter(Materia.id.in_(ids), Materia.escola_id == usuario_atual.escola_id)}
    if achadas != ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    db.query(ProfessorMateria).filter_by(usuario_id=professor_id, turma_id=turma.id).delete()
    for materia_id in ids:
        db.add(ProfessorMateria(usuario_id=professor_id, turma_id=turma.id, materia_id=materia_id))
    registrar(db, usuario_atual.id, "EDITAR", "ProfessorMateria", professor_id)
    db.commit()
    return [ProfessorMateriaResponse(professor_id=professor_id, materia_id=m) for m in ids]
