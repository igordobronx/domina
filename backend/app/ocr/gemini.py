import io
import logging
from functools import lru_cache

import httpx
from google import genai
from google.genai import errors, types
from PIL import Image, ImageOps

from app.config import settings

logger = logging.getLogger(__name__)

# cota estourada, sobrecarga, tempo esgotado: vale tentar o modelo reserva
ERROS_DE_CAPACIDADE = {429, 503, 504}

# foto de celular (12 MP) fazia o Gemini levar minutos ou estourar o tempo;
# com 1600 px ele leu em ~6s e ficou ate mais fiel aos erros do aluno
LADO_MAXIMO = 1600

# o texto vai para correcao da C1 (norma culta): o modelo NAO pode consertar
# os erros do aluno, senao a nota sai mais alta do que deveria
PROMPT = """Transcreva exatamente o texto da redação nesta imagem (manuscrito ou digitado).
Regras:
- Copie palavra por palavra, mantendo as quebras de linha.
- NÃO corrija ortografia, acentuação, pontuação, concordância nem escolha de palavras.
  Erros do aluno ficam como estão: se está escrito "a mãe brasileiro é abandonado",
  transcreva "a mãe brasileiro é abandonado"; se está "engravidez", não troque por "gravidez".
  Não troque uma palavra por sinônimo que pareça fazer mais sentido. A transcrição
  será usada para avaliar a escrita do aluno, então qualquer correção prejudica a avaliação.
- Palavra que não der para ler: escreva [ilegível]. Não complete de memória nem adivinhe.
- Trecho rasurado ou riscado: pule por completo, sem tentar decifrar o que está embaixo
  e sem deixar marcador. Se a rasura estiver entre parênteses, pule os parênteses também.
- Transcreva só as linhas da redação. Não transcreva nada do cabeçalho (nome, CPF,
  data de nascimento, inscrição, assinatura, códigos), a numeração das linhas
  e as instruções impressas do formulário.
- Responda só com o texto transcrito, sem comentários. Se não houver redação, responda vazio."""


class TextoPublicado(Exception):
    # o Google bloqueia (RECITATION) transcricao de texto que ja esta publicado na
    # internet, ex.: redacao nota 1000. Em envio de aluno real e sinal de copia.
    pass


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    # cria o cliente uma vez so. Uma tentativa de ate 45s; falhou, vai pro reserva:
    # sem isso, com o Gemini sobrecarregado, uma foto chegou a levar 3 minutos
    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=45_000, retry_options=types.HttpRetryOptions(attempts=1)),
    )


def reduzir(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    # so a copia que vai ao Gemini e reduzida; a foto original fica salva inteira
    try:
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(image_bytes)))  # desvira foto de celular
    except Exception:
        return image_bytes, mime_type  # formato que o Pillow nao abre (ex.: HEIC): o Gemini le direto
    im.thumbnail((LADO_MAXIMO, LADO_MAXIMO))
    saida = io.BytesIO()
    im.convert("RGB").save(saida, "JPEG", quality=85)
    return saida.getvalue(), "image/jpeg"


def gerar(contents, config: types.GenerateContentConfig):
    # chama o modelo principal; se ele estiver sem cota/sobrecarregado, o reserva.
    # devolve (resposta, modelo_usado). Usado pelo OCR e pela correcao.
    # chamada BLOQUEANTE: so chame de rota sincrona (def), nunca de async def
    # ponytail: reserva simples; com faturamento ativo a cota deixa de ser problema
    try:
        return _client().models.generate_content(model=settings.GEMINI_MODEL, contents=contents, config=config), settings.GEMINI_MODEL
    except (errors.APIError, httpx.TimeoutException) as e:
        # timeout do lado do cliente (httpx) nao vira APIError, por isso entra aqui tambem
        if isinstance(e, errors.APIError) and e.code not in ERROS_DE_CAPACIDADE:
            raise
        logger.warning("Gemini %s indisponivel (%r), usando %s", settings.GEMINI_MODEL, e, settings.GEMINI_MODEL_RESERVA)
        modelo = settings.GEMINI_MODEL_RESERVA
        return _client().models.generate_content(model=modelo, contents=contents, config=config), modelo


def extract_text(image_bytes: bytes, mime_type: str) -> str:
    # recebe os bytes de uma imagem e pede ao Gemini a transcricao da redacao
    image_bytes, mime_type = reduzir(image_bytes, mime_type)
    response, _ = gerar(
        [types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT],
        # raciocinio "minimal": transcrever nao precisa pensar; na redacao real
        # caiu de 68s ("low") para 6s com a mesma fidelidade
        types.GenerateContentConfig(temperature=0, thinking_config=types.ThinkingConfig(thinking_level="minimal")),
    )
    if response.candidates and response.candidates[0].finish_reason == types.FinishReason.RECITATION:
        raise TextoPublicado()
    return (response.text or "").strip()
