import logging

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

from app.auth.dependencies import get_current_user
from app.config import settings
from app.models.usuario import Usuario
from app.ocr.gemini import TextoPublicado, extract_text
from app.schemas.ocr import OCRResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])

MAX_IMAGEM_BYTES = 10 * 1024 * 1024  # 10 MB: foto de celular cabe com folga


def ler_imagem(file: UploadFile) -> bytes:
    # valida e le o upload; usado aqui e no envio de redacao (routers/submissoes.py)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado precisa ser uma imagem (JPEG, PNG etc.).",
        )
    # le 1 byte a mais que o limite: se vier, o arquivo e grande demais
    image_bytes = file.file.read(MAX_IMAGEM_BYTES + 1)
    if len(image_bytes) > MAX_IMAGEM_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Imagem maior que 10 MB.",
        )
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio.")
    return image_bytes


def ocr(image_bytes: bytes, mime_type: str) -> str:
    # chama o Gemini e traduz falhas em respostas HTTP sem vazar detalhe interno
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY nao configurada")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR indisponível: servidor sem chave do Gemini configurada.",
        )
    try:
        texto = extract_text(image_bytes, mime_type)
    except TextoPublicado:
        raise HTTPException(
            422, "Este texto parece ser de uma redação já publicada; a leitura automática foi bloqueada. "
                 "Envie a sua própria redação ou digite o texto.",
        )
    except Exception:
        logger.exception("falha no OCR")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha ao ler o texto da imagem. Tente de novo ou envie outra foto.",
        )
    if not texto:
        raise HTTPException(422, "Não encontramos texto na imagem. Envie uma foto mais nítida da redação.")
    return texto


# rota sincrona (def): o FastAPI roda numa thread separada, entao a chamada
# bloqueante ao Gemini nao trava as outras requisicoes
@router.post("/extract", response_model=OCRResponse)
def extract_text_from_image(file: UploadFile, current_user: Usuario = Depends(get_current_user)):
    return OCRResponse(texto_extraido=ocr(ler_imagem(file), file.content_type))
