import logging
from functools import lru_cache

from google import genai
from google.genai import errors, types

from app.config import settings

logger = logging.getLogger(__name__)

# cota estourada, sobrecarga, tempo esgotado: vale tentar o modelo reserva
ERROS_DE_CAPACIDADE = {429, 503, 504}

# o texto vai para correcao da C1 (norma culta): o modelo NAO pode consertar
# os erros do aluno, senao a nota sai mais alta do que deveria
PROMPT = """Transcreva exatamente o texto da redação nesta imagem (manuscrito ou digitado).
Regras:
- Copie palavra por palavra, mantendo as quebras de linha.
- NÃO corrija ortografia, acentuação, pontuação nem gramática. Erros do aluno ficam como estão.
- Palavra que não der para ler: escreva [ilegível]. Não complete de memória nem adivinhe.
- Não transcreva o campo NOME nem outro dado do aluno no cabeçalho, a numeração
  das linhas, palavras riscadas e as instruções impressas do formulário.
- Responda só com o texto transcrito, sem comentários. Se não houver redação, responda vazio."""


class TextoPublicado(Exception):
    # o Google bloqueia (RECITATION) transcricao de texto que ja esta publicado na
    # internet, ex.: redacao nota 1000. Em envio de aluno real e sinal de copia.
    pass


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    # cria o cliente uma vez so. Teto de 60s por tentativa e 2 tentativas:
    # sem isso, com o Gemini sobrecarregado, uma foto chegou a levar 3 minutos
    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=60_000, retry_options=types.HttpRetryOptions(attempts=2)),
    )


def _gerar(model: str, image_bytes: bytes, mime_type: str):
    return _client().models.generate_content(
        model=model,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT],
        # raciocinio "low": transcrever nao precisa pensar muito; cai de ~20s para ~4s
        config=types.GenerateContentConfig(
            temperature=0,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )


def extract_text(image_bytes: bytes, mime_type: str) -> str:
    # recebe os bytes de uma imagem e pede ao Gemini a transcricao da redacao.
    # chamada BLOQUEANTE: so chame de rota sincrona (def), nunca de async def
    # ponytail: reserva simples; com faturamento ativo a cota deixa de ser problema
    try:
        response = _gerar(settings.GEMINI_MODEL, image_bytes, mime_type)
    except errors.APIError as e:
        if e.code not in ERROS_DE_CAPACIDADE:
            raise
        logger.warning("Gemini %s indisponivel (%s), usando %s", settings.GEMINI_MODEL, e.code, settings.GEMINI_MODEL_RESERVA)
        response = _gerar(settings.GEMINI_MODEL_RESERVA, image_bytes, mime_type)
    if response.candidates and response.candidates[0].finish_reason == types.FinishReason.RECITATION:
        raise TextoPublicado()
    return (response.text or "").strip()
