"""O que o professor leciona (materia por turma, definido pelo gestor). Gestor/admin: sem limite."""
from sqlalchemy.orm import Session

from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.models.usuario import ProfessorMateria, Usuario, UsuarioTurma


def materias_do_professor(db: Session, professor_id, turma_ids=None) -> set:
    q = db.query(ProfessorMateria.materia_id).filter(ProfessorMateria.usuario_id == professor_id)
    if turma_ids is not None:
        q = q.filter(ProfessorMateria.turma_id.in_(list(turma_ids)))
    return {m for (m,) in q}


def materias_visiveis_do_aluno(db: Session, usuario: Usuario, aluno_id):
    """Materias de que `usuario` pode ver estatistica deste aluno. None = todas (gestor)."""
    if usuario.perfil != PerfilEnum.PROFESSOR:
        return None
    turmas_do_aluno = [t for (t,) in db.query(UsuarioTurma.turma_id).filter_by(
        usuario_id=aluno_id, papel=UsuarioTurmaPapelEnum.ALUNO)]
    return materias_do_professor(db, usuario.id, turmas_do_aluno)


def leciona(db: Session, usuario: Usuario, turma_id, materia_id) -> bool:
    """Professor so cria atividade/exercicio de uma materia que ele da naquela turma. Gestor/admin: sempre."""
    if usuario.perfil != PerfilEnum.PROFESSOR:
        return True
    return db.query(ProfessorMateria).filter_by(
        usuario_id=usuario.id, turma_id=turma_id, materia_id=materia_id).first() is not None
