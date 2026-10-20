import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.enum import PerfilEnum, TipoDocumentoEnum
from app.models.usuario import DocumentoBase, Materia, Usuario
from app.schemas.documento import DocumentoBaseResponse

router = APIRouter(tags=["documentos"])

MAX_DOCUMENTO_BYTES = 20 * 1024 * 1024  # 20 MB: apostila/rubrica em PDF cabe com folga


@router.get("/materias/{materia_id}/documentos", response_model=list[DocumentoBaseResponse])
def listar_documentos(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return db.query(DocumentoBase).filter_by(materia_id=materia_id).order_by(DocumentoBase.criado_em.desc()).all()


# RF-13: professor/gestor sobe material de apoio (apostila, rubrica, gabarito) de uma materia da escola.
# ponytail: so grava o arquivo e cria o registro PENDENTE; extracao de conteudo fica pro P2/P3
@router.post("/materias/{materia_id}/documentos", response_model=DocumentoBaseResponse,
             status_code=status.HTTP_201_CREATED)
def enviar_documento(
    materia_id: uuid.UUID,
    file: UploadFile,
    tipo: TipoDocumentoEnum = Form(...),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores enviam material.")

    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")

    conteudo = file.file.read(MAX_DOCUMENTO_BYTES + 1)
    if len(conteudo) > MAX_DOCUMENTO_BYTES:
        raise HTTPException(413, "Arquivo maior que 20 MB.")
    if not conteudo:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Arquivo vazio.")

    sufixo = Path(file.filename or "").suffix.lower()[:10] or ".bin"
    caminho = Path(settings.UPLOAD_DIR) / f"{uuid.uuid4()}{sufixo}"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo)

    documento = DocumentoBase(
        materia_id=materia.id,
        enviado_por=usuario.id,
        nome_arquivo=file.filename or caminho.name,
        tipo=tipo,
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    return documento
