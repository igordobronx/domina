import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.enum import PerfilEnum, TipoEnvioEnum
from app.models.usuario import Atividade, Submissao, Usuario, UsuarioTurma
from app.routers.ocr import ler_imagem, ocr
from app.schemas.submissao import ConfirmarTextoRequest, SubmissaoResponse

router = APIRouter(prefix="/submissoes", tags=["submissoes"])


# fluxo RF-11: aluno manda a foto -> OCR -> aluno confere/corrige o texto -> confirma.
# so depois de confirmada a submissao pode ir para a correcao por IA.
@router.post("/imagem", response_model=SubmissaoResponse, status_code=status.HTTP_201_CREATED)
def enviar_imagem(
    file: UploadFile,
    atividade_id: uuid.UUID = Form(...),
    aluno: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if aluno.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos enviam redação.")

    atividade = db.get(Atividade, atividade_id)
    na_turma = atividade and db.get(UsuarioTurma, (aluno.id, atividade.turma_id))
    if not na_turma:
        # mesma resposta para "nao existe" e "nao e da sua turma": nao revela atividades alheias
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")

    image_bytes = ler_imagem(file)
    texto = ocr(image_bytes, file.content_type)  # se o OCR falhar, nada e gravado

    # guarda a foto original (o professor pode querer ver ao revisar)
    # ponytail: disco local; trocar por bucket (GCS/S3) quando houver mais de um servidor
    sufixo = Path(file.filename or "").suffix.lower()[:10] or ".img"
    caminho = Path(settings.UPLOAD_DIR) / f"{uuid.uuid4()}{sufixo}"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(image_bytes)

    submissao = Submissao(
        atividade_id=atividade.id,
        aluno_id=aluno.id,
        tipo_envio=TipoEnvioEnum.IMAGEM,
        conteudo_bruto=str(caminho),
        texto_ocr=texto,
    )
    db.add(submissao)
    db.commit()
    db.refresh(submissao)
    return submissao


@router.get("/{submissao_id}", response_model=SubmissaoResponse)
def ver_submissao(
    submissao_id: uuid.UUID,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # o aluno dono ve (tela de confirmacao recarregada); professor da turma tambem
    submissao = db.get(Submissao, submissao_id)
    pode_ver = submissao and (
        submissao.aluno_id == usuario.id
        or (
            usuario.perfil == PerfilEnum.PROFESSOR
            and db.get(UsuarioTurma, (usuario.id, db.get(Atividade, submissao.atividade_id).turma_id))
        )
    )
    if not pode_ver:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submissão não encontrada.")
    return submissao


@router.put("/{submissao_id}/confirmar", response_model=SubmissaoResponse)
def confirmar_texto(
    submissao_id: uuid.UUID,
    payload: ConfirmarTextoRequest,
    aluno: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissao = db.get(Submissao, submissao_id)
    if not submissao or submissao.aluno_id != aluno.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submissão não encontrada.")
    if submissao.texto_confirmado is not None:
        # depois de confirmado o texto vai para correcao; mudar agora invalidaria a nota
        raise HTTPException(status.HTTP_409_CONFLICT, "Texto já confirmado.")

    texto = payload.texto.strip()
    if not texto:
        raise HTTPException(422, "Texto vazio.")

    submissao.texto_confirmado = texto
    db.commit()
    db.refresh(submissao)
    return submissao
