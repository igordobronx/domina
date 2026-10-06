from pydantic import BaseModel

class OCRResponse(BaseModel):
    texto_extraido: str 