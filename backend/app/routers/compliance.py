from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.enum import PerfilEnum
from app.models.usuario import AuditLog, ConsentimentoLGPD, CustoUso, Usuario
from app.schemas.compliance import AuditLogResponse, ConsentimentoRequest, ConsentimentoResponse, CustoUsoResponse

router = APIRouter(tags=["compliance"])


def _so_gestor(usuario: Usuario) -> None:
    if usuario.perfil != PerfilEnum.GESTOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só gestores acessam isto.")


# RN-21: consentimento do responsavel antes do aluno usar a plataforma (LGPD).
# ponytail: so registra o aceite; nao bloqueia envio de redacao sem ele ainda
@router.post("/consentimento", response_model=ConsentimentoResponse, status_code=status.HTTP_201_CREATED)
def registrar_consentimento(payload: ConsentimentoRequest, usuario: Usuario = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos registram consentimento.")
    if db.query(ConsentimentoLGPD).filter_by(aluno_id=usuario.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Consentimento já registrado.")

    consentimento = ConsentimentoLGPD(
        aluno_id=usuario.id, responsavel_nome=payload.responsavel_nome.strip(),
        responsavel_email=payload.responsavel_email,
    )
    db.add(consentimento)
    db.commit()
    db.refresh(consentimento)
    return consentimento


@router.get("/consentimento/meu", response_model=ConsentimentoResponse)
def meu_consentimento(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    consentimento = db.query(ConsentimentoLGPD).filter_by(aluno_id=usuario.id).first()
    if not consentimento:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nenhum consentimento registrado.")
    return consentimento


@router.get("/custo-uso", response_model=CustoUsoResponse)
def custo_uso_do_mes(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_gestor(usuario)
    mes = date.today().strftime("%Y-%m")
    uso = db.query(CustoUso).filter_by(escola_id=usuario.escola_id, mes_referencia=mes).first()
    if not uso:
        return CustoUsoResponse(mes_referencia=mes, tokens_llm=0, chamadas_ocr=0, custo_estimado=0.0)
    return uso


@router.get("/audit-log", response_model=list[AuditLogResponse])
def listar_auditoria(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_gestor(usuario)
    registros = (
        db.query(AuditLog).join(Usuario, Usuario.id == AuditLog.usuario_id)
        .filter(Usuario.escola_id == usuario.escola_id)
        .order_by(AuditLog.criado_em.desc()).limit(200)
    )
    return list(registros)
