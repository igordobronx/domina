from sqlalchemy.orm import Session

from app.models.usuario import AuditLog


def registrar(db: Session, usuario_id, acao: str, entidade: str, entidade_id) -> None:
    db.add(AuditLog(usuario_id=usuario_id, acao=acao, entidade=entidade, entidade_id=entidade_id))
