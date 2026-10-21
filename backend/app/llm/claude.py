"""Chamada ao Claude para corrigir a redacao (app/correcao.py).

O Gemini divergia demais do corretor humano do INEP nas calibracoes; a nota da redacao
passou a vir do Claude. O OCR da foto e a correcao de exatas continuam no Gemini
(app/ocr/gemini.py, app/correcao_exatas.py) -- so esta parte trocou de provedor.
"""
import logging
from functools import lru_cache

import anthropic
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

NOME_TOOL = "responder_correcao"


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    headers = {}
    if settings.ANTHROPIC_WORKSPACE_ID:
        headers["anthropic-workspace-id"] = settings.ANTHROPIC_WORKSPACE_ID
    return anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY, timeout=45.0, max_retries=1, default_headers=headers,
    )


def gerar_json(
    prompt: str, schema: type[BaseModel], temperature: float = 0, model: str | None = None,
) -> tuple[BaseModel, str]:
    # forca o formato do schema via tool-use: o Claude nao tem "response_schema" nativo
    # como o Gemini. Estes modelos nao aceitam "temperature" nem tool_choice="tool"/"any"
    # (so "auto"); na pratica eles ainda chamam a tool de forma confiavel com "auto".
    modelo = model or settings.ANTHROPIC_MODEL
    response = _client().messages.create(
        model=modelo,
        # o modelo pensa por padrao (extended thinking) antes de preencher a tool; a etapa 1
        # (evidencias por competencia) tambem gera bastante texto -- 4096 cortava no meio
        max_tokens=16000,
        tools=[{
            "name": NOME_TOOL,
            "description": "Devolve o resultado da correcao no formato pedido.",
            "input_schema": schema.model_json_schema(),
        }],
        tool_choice={"type": "auto"},
        messages=[{"role": "user", "content": prompt}],
    )
    bloco = next(b for b in response.content if b.type == "tool_use")
    return schema.model_validate(bloco.input), modelo
