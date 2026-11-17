import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.enum import PerfilEnum, TipoDocumentoEnum
from app.lecionados import materias_do_professor
from app.models.usuario import DocumentoBase, Materia, Usuario
from app.schemas.documento import DocumentoBaseResponse

router = APIRouter(tags=["documentos"])

MAX_DOCUMENTO_BYTES = 20 * 1024 * 1024  # 20 MB: apostila/rubrica em PDF cabe com folga
EXTENSOES = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".webp"}


def _so_equipe(usuario: Usuario) -> None:
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores usam os materiais.")


def _materia_da_escola(db: Session, usuario: Usuario, materia_id) -> Materia:
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return materia


def _visiveis(db: Session, usuario: Usuario):
    """Gestor ve os materiais da escola toda; professor so os que ele mesmo enviou."""
    q = (db.query(DocumentoBase, Materia, Usuario)
         .join(Materia, Materia.id == DocumentoBase.materia_id)
         .join(Usuario, Usuario.id == DocumentoBase.enviado_por)
         .filter(Materia.escola_id == usuario.escola_id, DocumentoBase.ativo.is_(True)))
    if usuario.perfil == PerfilEnum.PROFESSOR:
        q = q.filter(DocumentoBase.enviado_por == usuario.id)
    return q


def _resposta(d: DocumentoBase, m: Materia, u: Usuario) -> DocumentoBaseResponse:
    return DocumentoBaseResponse(
        id=d.id, materia_id=d.materia_id, materia_nome=m.nome, nome_arquivo=d.nome_arquivo, tipo=d.tipo,
        status_processamento=d.status_processamento, tamanho_bytes=d.tamanho_bytes, enviado_por_nome=u.nome,
        pode_baixar=bool(d.caminho), criado_em=d.criado_em,
    )


@router.get("/documentos", response_model=list[DocumentoBaseResponse])
def listar_documentos(materia_id: uuid.UUID | None = None, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    _so_equipe(usuario)
    q = _visiveis(db, usuario)
    if materia_id:
        q = q.filter(DocumentoBase.materia_id == materia_id)
    return [_resposta(d, m, u) for d, m, u in q.order_by(DocumentoBase.criado_em.desc()).all()]


@router.get("/materias/{materia_id}/documentos", response_model=list[DocumentoBaseResponse])
def listar_documentos_da_materia(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    _so_equipe(usuario)
    _materia_da_escola(db, usuario, materia_id)
    return listar_documentos(materia_id, usuario, db)


# RF-13: professor/gestor sobe material de apoio (apostila, rubrica, gabarito) vinculado a uma materia da escola.
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
    _so_equipe(usuario)
    materia = _materia_da_escola(db, usuario, materia_id)
    if usuario.perfil == PerfilEnum.PROFESSOR and materia.id not in materias_do_professor(db, usuario.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Você não leciona {materia.nome}.")

    sufixo = Path(file.filename or "").suffix.lower()
    if sufixo not in EXTENSOES:
        raise HTTPException(422, "Envie PDF, DOCX, TXT ou imagem (PNG, JPG, WEBP).")
    conteudo = file.file.read(MAX_DOCUMENTO_BYTES + 1)
    if len(conteudo) > MAX_DOCUMENTO_BYTES:
        raise HTTPException(413, "Arquivo maior que 20 MB.")
    if not conteudo:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Arquivo vazio.")

    nome_no_disco = f"{uuid.uuid4()}{sufixo}"
    caminho = Path(settings.UPLOAD_DIR) / nome_no_disco
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo)

    documento = DocumentoBase(
        materia_id=materia.id,
        enviado_por=usuario.id,
        nome_arquivo=file.filename or nome_no_disco,
        tipo=tipo,
        tamanho_bytes=len(conteudo),
        caminho=nome_no_disco,
    )
    db.add(documento)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "DocumentoBase", documento.id)
    db.commit()
    db.refresh(documento)
    return _resposta(documento, materia, usuario)


def _meu_documento(db: Session, usuario: Usuario, documento_id: uuid.UUID):
    _so_equipe(usuario)
    linha = _visiveis(db, usuario).filter(DocumentoBase.id == documento_id).first()
    if not linha:  # de outra escola, de outro professor ou arquivado = nao existe
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Material não encontrado.")
    return linha


@router.get("/documentos/{documento_id}/arquivo")
def baixar_documento(documento_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    d, _, _ = _meu_documento(db, usuario, documento_id)
    arquivo = Path(settings.UPLOAD_DIR) / (d.caminho or "")
    if not d.caminho or not arquivo.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "O arquivo deste material não está disponível.")
    return FileResponse(arquivo, filename=d.nome_arquivo)


# excluir = arquivar: o registro e o arquivo ficam (um material ja usado para treinar a IA nao some)
@router.delete("/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(documento_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    d, _, _ = _meu_documento(db, usuario, documento_id)
    d.ativo = False
    registrar(db, usuario.id, "ARQUIVAR", "DocumentoBase", d.id)
    db.commit()
