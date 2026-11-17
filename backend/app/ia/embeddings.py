"""Texto -> vetor, para achar trechos parecidos pelo SENTIDO (nao so pelas mesmas palavras).

Hoje usa o Gemini por API. Devolve None quando nao da (sem chave, IA_EMBEDDINGS=local, API
fora do ar): quem chama cai para a busca por palavras em memoria.py. Trocar por um modelo
aberto rodando no servidor do Domina depois e mexer so aqui.
"""
import logging

from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

LOTE = 50  # a API aceita varios textos por chamada; lote pequeno para nao estourar o limite


def embutir(textos: list[str], consulta: bool = False) -> list[list[float]] | None:
    if settings.IA_EMBEDDINGS != "gemini" or not settings.GEMINI_API_KEY or not textos:
        return None
    from app.ocr.gemini import _client

    config = types.EmbedContentConfig(
        task_type="RETRIEVAL_QUERY" if consulta else "RETRIEVAL_DOCUMENT", output_dimensionality=768,
    )
    try:
        vetores = []
        for i in range(0, len(textos), LOTE):
            r = _client().models.embed_content(
                model=settings.GEMINI_MODEL_EMBEDDING, contents=textos[i:i + LOTE], config=config,
            )
            vetores += [list(e.values) for e in r.embeddings]
        return vetores
    except Exception:
        logger.warning("embeddings indisponiveis; usando busca por palavras", exc_info=True)
        return None
