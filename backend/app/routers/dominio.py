import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.models.usuario import DominioAluno, Tema, Usuario, UsuarioTurma
from app.schemas.dominio import DominioResponse

router = APIRouter(tags=["dominio"])


def _compartilha_turma(db: Session, professor_id, aluno_id) -> bool:
    turmas_professor = {
        ut.turma_id for ut in
        db.query(UsuarioTurma).filter_by(usuario_id=professor_id, papel=UsuarioTurmaPapelEnum.PROFESSOR)
    }
    turmas_aluno = {
        ut.turma_id for ut in
        db.query(UsuarioTurma).filter_by(usuario_id=aluno_id, papel=UsuarioTurmaPapelEnum.ALUNO)
    }
    return bool(turmas_professor & turmas_aluno)


def _dominio_de(db: Session, aluno_id) -> list[DominioResponse]:
    registros = (
        db.query(DominioAluno, Tema).join(Tema, Tema.id == DominioAluno.tema_id)
        .filter(DominioAluno.aluno_id == aluno_id).order_by(Tema.habilidade_codigo)
    )
    return [
        DominioResponse(
            tema_id=d.tema_id, tema=t.nome, habilidade_codigo=t.habilidade_codigo,
            percentual_dominio=float(d.percentual_dominio), num_evidencias=d.num_evidencias,
        )
        for d, t in registros
    ]


@router.get("/dominio/meu", response_model=list[DominioResponse])
def meu_dominio(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")
    return _dominio_de(db, usuario.id)


@router.get("/alunos/{aluno_id}/dominio", response_model=list[DominioResponse])
def dominio_do_aluno(aluno_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    aluno = db.get(Usuario, aluno_id)
    if not aluno or aluno.perfil != PerfilEnum.ALUNO or aluno.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
    if usuario.perfil == PerfilEnum.PROFESSOR and not _compartilha_turma(db, usuario.id, aluno.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado.")
    elif usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem domínio de alunos.")
    return _dominio_de(db, aluno.id)
