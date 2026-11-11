"""Figura anexada a uma questao de exatas (ex.: estruturas quimicas com pKa).

A figura faz parte do enunciado: o aluno ve, e o corretor (Gemini) recebe junto com a questao.
Nao passa por OCR -- o modelo le a imagem direto.
"""
import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.enum import PerfilEnum
from app.models.usuario import Atividade, Tema, Turma, Usuario
from app.routers.ocr import ler_imagem
from app.routers.submissoes import _gestor_da_escola, _na_turma, _professor_da_turma

router = APIRouter(tags=["questoes"])


def _questao(db: Session, atividade_id: uuid.UUID, codigo: str) -> tuple[Atividade, Tema]:
    atividade = db.get(Atividade, atividade_id)
    tema = (
        db.query(Tema).filter_by(atividade_id=atividade_id, habilidade_codigo=codigo.upper()).first()
        if atividade else None
    )
    if not tema:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Questão não encontrada.")
    return atividade, tema


def _pode_editar(db: Session, atividade: Atividade, usuario: Usuario) -> None:
    # mesma regra de criar a atividade: professor da turma ou gestor da escola (outros: 404)
    turma = db.get(Turma, atividade.turma_id)
    if not turma or turma.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Questão não encontrada.")
    if usuario.perfil == PerfilEnum.PROFESSOR and not _professor_da_turma(db, usuario, turma.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores editam questões.")


def _apagar_arquivo(caminho: str | None) -> None:
    if caminho:
        Path(caminho).unlink(missing_ok=True)


@router.post("/atividades/{atividade_id}/questoes/{codigo}/imagem", status_code=status.HTTP_204_NO_CONTENT)
def anexar_figura(atividade_id: uuid.UUID, codigo: str, file: UploadFile,
                  usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    atividade, tema = _questao(db, atividade_id, codigo)
    _pode_editar(db, atividade, usuario)
    conteudo = ler_imagem(file)  # so imagem, ate 10 MB
    sufixo = Path(file.filename or "").suffix.lower()[:10] or ".img"
    caminho = Path(settings.UPLOAD_DIR) / f"{uuid.uuid4()}{sufixo}"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo)
    _apagar_arquivo(tema.imagem)  # trocar a figura nao deixa a antiga orfa
    tema.imagem = str(caminho)
    db.commit()


@router.delete("/atividades/{atividade_id}/questoes/{codigo}/imagem", status_code=status.HTTP_204_NO_CONTENT)
def remover_figura(atividade_id: uuid.UUID, codigo: str,
                   usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    atividade, tema = _questao(db, atividade_id, codigo)
    _pode_editar(db, atividade, usuario)
    _apagar_arquivo(tema.imagem)
    tema.imagem = None
    db.commit()


@router.get("/atividades/{atividade_id}/questoes/{codigo}/imagem")
def ver_figura(atividade_id: uuid.UUID, codigo: str,
               usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    atividade, tema = _questao(db, atividade_id, codigo)
    turma = db.get(Turma, atividade.turma_id)
    # quem ve: professor/aluno da turma ou gestor da escola
    if not turma or not (_na_turma(db, usuario.id, turma.id) or _gestor_da_escola(db, usuario, turma.id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Questão não encontrada.")
    if not tema.imagem or not Path(tema.imagem).exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Esta questão não tem figura.")
    mime, _ = mimetypes.guess_type(tema.imagem)
    return FileResponse(tema.imagem, media_type=mime or "image/jpeg")
