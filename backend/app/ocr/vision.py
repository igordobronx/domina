# pyrefly: ignore [missing-import]
from functools import lru_cache

from google.cloud import vision


@lru_cache(maxsize=1)
def _client() -> vision.ImageAnnotatorClient:
    # cria o cliente uma vez so (abrir conexao com o Google a cada foto e lento)
    return vision.ImageAnnotatorClient()


def extract_text(image_bytes: bytes) -> str:
    # recebe os bytes de uma imagem e envia para o google vision api extrair o texto.
    # chamada BLOQUEANTE: so chame de rota sincrona (def), nunca de async def

    image = vision.Image(content=image_bytes)

    # document_text_detection e o modo para texto denso/manuscrito (redacao);
    # text_detection e feito para texto solto em foto (placa, rotulo)
    response = _client().document_text_detection(
        image=image,
        image_context=vision.ImageContext(language_hints=["pt"]),
    )

    # tratamento de erros retornados dentro do payload da Vision API
    if response.error.message:
        raise RuntimeError(f"Vision API: {response.error.message}")

    return response.full_text_annotation.text
