"""So para os testes: liga um professor a uma materia numa turma (o gestor faz isso pela tela de turmas)."""
from app.database import SessionLocal
from app.models.usuario import ProfessorMateria, Usuario
import uuid


def vincular(email: str, turma_id, materia_id) -> None:
    with SessionLocal() as db:
        uid = db.query(Usuario).filter_by(email=email).one().id
        chave = dict(usuario_id=uid, turma_id=uuid.UUID(str(turma_id)), materia_id=uuid.UUID(str(materia_id)))
        if not db.query(ProfessorMateria).filter_by(**chave).first():
            db.add(ProfessorMateria(**chave))
            db.commit()
