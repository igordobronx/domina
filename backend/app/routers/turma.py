from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.models.usuario import Turma, Usuario, UsuarioTurma
from app.routers.submissoes import _na_turma
from app.schemas.turma import CriarTurmaRequest, MatricularRequest, TurmaResponse

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
def minhas_turmas(usuario_atual: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario_atual.perfil == PerfilEnum.GESTOR:
        turmas = db.query(Turma).filter_by(escola_id=usuario_atual.escola_id)
    elif usuario_atual.perfil == PerfilEnum.PROFESSOR:
        turma_ids = [
            ut.turma_id for ut in
            db.query(UsuarioTurma).filter_by(usuario_id=usuario_atual.id, papel=UsuarioTurmaPapelEnum.PROFESSOR)
        ]
        turmas = db.query(Turma).filter(Turma.id.in_(turma_ids))
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores usam esta rota.")
    return list(turmas)


@router.post("/{turma_id}/matricular", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
def matricular(turma_id, payload: MatricularRequest, usuario_atual: Usuario = Depends(get_current_user),
                db: Session = Depends(get_db)):
    _so_gestor(usuario_atual)

    turma = db.get(Turma, turma_id)
    if not turma or turma.escola_id != usuario_atual.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")

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
