from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings

# o texto vai para correcao da C1 (norma culta): o modelo NAO pode consertar
# os erros do aluno, senao a nota sai mais alta do que deveria
PROMPT = """Transcreva exatamente o texto manuscrito desta imagem de redação.
Regras:
- Copie palavra por palavra, mantendo as quebras de linha.
- NÃO corrija ortografia, acentuação, pontuação nem gramática. Erros do aluno ficam como estão.
- Palavra que não der para ler: escreva [ilegível].
- Ignore rabiscos, numeração de linhas e cabeçalho impresso da folha.
- Responda só com o texto transcrito, sem comentários. Se não houver texto, responda vazio."""


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    # cria o cliente uma vez so
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def extract_text(image_bytes: bytes, mime_type: str) -> str:
    # recebe os bytes de uma imagem e pede ao Gemini a transcricao do manuscrito.
    # chamada BLOQUEANTE: so chame de rota sincrona (def), nunca de async def
    response = _client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT],
        config=types.GenerateContentConfig(temperature=0),
    )
    return (response.text or "").strip()
