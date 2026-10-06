# pyrefly: ignore [missing-import]
from google.cloud import vision

def extract_text(image_bytes: bytes) -> str:

    #recebe os bites de uma imagem e envia para o google vision api extrair o texto
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_bytes)
    
    #chamada para deteccao de texto na foto
    response = client.text_detection(image=image)

    #tratamenteo de erros returnados dentro do payload da Vision API
    if response.error.message:
        raise Exception(
            f"Erro na extração do textoi via Vision API: {response.error.message}"
        )

    #primeiro elemento nas anotações contem todo o texto consolidado;
    if response.text_annotations:
        return response.text_annotations[0].description

    return ""