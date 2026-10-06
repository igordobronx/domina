from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from app.ocr.vision import extract_text
from app.schemas.ocr import OCRResponse

router = APIRouter(prefix="/ocr", tags=["ocr"])

@router.post("/extract", response_model=OCRResponse)
async def extract_text_from_image(file: UploadFile, current_user: Usuario = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado precisa ser uma iamgem JPEG, PNG etc."
        )

    try:
        #le os bytes do arquivo ASSINCRONAMENTE
        image_bytes = await file.read()

        #processa os bytes com o visionAPI
        texto_extraido = extract_text(image_bytes)

        return OCRResponse(texto_extraido=texto_extraido)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"falha ao processar o OCR da imagem: {str(e)}",
        )
