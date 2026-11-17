import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.ia import memoria, registro
from app.models.enum import PerfilEnum, TipoDocumentoEnum
from app.models.usuario import DocumentoBase, IaTrecho, Materia, Usuario
from app.schemas.documento import DocumentoBaseResponse, InstrucaoRequest, InstrucaoResponse, MemoriaIAResponse

router = APIRouter(tags=["documentos"])

MAX_DOCUMENTO_BYTES = 20 * 1024 * 1024  # 20 MB: apostila/rubrica em PDF cabe com folga


@router.get("/materias/{materia_id}/documentos", response_model=list[DocumentoBaseResponse])
def listar_documentos(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    q = db.query(DocumentoBase).filter_by(materia_id=materia_id)
    if usuario.perfil == PerfilEnum.PROFESSOR:
        # o treino e de cada professor: ele ve o que ELE enviou e o que o gestor enviou para a escola
        gestores = db.query(Usuario.id).filter(Usuario.perfil == PerfilEnum.GESTOR)
        q = q.filter(or_(DocumentoBase.enviado_por == usuario.id, DocumentoBase.enviado_por.in_(gestores)))
    return q.order_by(DocumentoBase.criado_em.desc()).all()


# RF-13: professor/gestor sobe material de apoio (apostila, rubrica, gabarito) de uma materia da escola.
# Na mesma chamada a IA le o arquivo e guarda os trechos na memoria da materia (app/ia/memoria.py):
# o material ja vale para a proxima correcao/exercicio. Se nao der para ler, fica ERRO com o motivo.
# ponytail: leitura dentro da requisicao (PDF grande demora alguns segundos); fila se virar problema
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
        tamanho_bytes=len(conteudo),
        caminho=str(caminho),
    )
    db.add(documento)
    db.flush()
    memoria.indexar_documento(db, documento)
    registro.gravar(db, materia_id=materia.id, professor_id=usuario.id)  # leitura de foto/PDF escaneado
    db.commit()
    db.refresh(documento)
    return documento


@router.get("/materias/{materia_id}/ia", response_model=MemoriaIAResponse)
def ver_memoria_da_ia(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Quanto a IA ja aprendeu nesta materia: trechos de material e correcoes aprovadas."""
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem a memória da IA.")
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return memoria.resumo(db, materia_id, usuario.id)


# "Treinar IA" > Escrever instrucoes: o professor escreve direto para a IA o jeito dele ("sempre
# exija a verificacao final", "nao desconte erro de acento"). Valem sempre, em toda correcao e
# exercicio daquela materia (app/ia/memoria.py > instrucoes_de). So o professor/gestor mexe.
def _materia_de_quem_ensina(db: Session, usuario: Usuario, materia_id) -> Materia:
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores ensinam a IA.")
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return materia


@router.get("/materias/{materia_id}/instrucoes", response_model=list[InstrucaoResponse])
def listar_instrucoes(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    return [InstrucaoResponse(id=t.id, materia_id=t.materia_id, texto=t.texto, criado_em=t.criado_em)
            for t in memoria.instrucoes_de(db, materia_id, usuario.id)]


@router.post("/materias/{materia_id}/instrucoes", response_model=InstrucaoResponse, status_code=status.HTTP_201_CREATED)
def criar_instrucao(materia_id: uuid.UUID, payload: InstrucaoRequest,
                    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    materia = _materia_de_quem_ensina(db, usuario, materia_id)
    if len(memoria.instrucoes_de(db, materia.id, usuario.id)) >= memoria.MAX_INSTRUCOES:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            f"Você já tem {memoria.MAX_INSTRUCOES} instruções nesta matéria. Apague alguma antes.")
    texto = payload.texto.strip()
    trecho = IaTrecho(materia_id=materia.id, professor_id=usuario.id, origem=memoria.INSTRUCAO,
                      titulo="Instrução do professor", texto=texto)
    db.add(trecho)
    db.commit()
    db.refresh(trecho)
    return InstrucaoResponse(id=trecho.id, materia_id=trecho.materia_id, texto=trecho.texto, criado_em=trecho.criado_em)


@router.delete("/materias/{materia_id}/instrucoes/{instrucao_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_instrucao(materia_id: uuid.UUID, instrucao_id: uuid.UUID,
                     usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    trecho = db.get(IaTrecho, instrucao_id)
    # so apaga a PROPRIA instrucao (a do gestor vale para a escola e e dele)
    if not trecho or trecho.origem != memoria.INSTRUCAO or trecho.materia_id != materia_id or trecho.professor_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Instrução não encontrada.")
    db.delete(trecho)
    db.commit()
