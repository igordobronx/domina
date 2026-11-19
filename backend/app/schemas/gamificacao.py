from datetime import date

from pydantic import BaseModel

from app.schemas.metas import NivelResponse


class XpItem(BaseModel):
    data: date
    xp: int
    motivo: str


class SequenciaResponse(BaseModel):
    atual: int
    melhor: int
    estudou_hoje: bool


class ConquistaResponse(BaseModel):
    codigo: str
    nome: str
    descricao: str
    alvo: int
    progresso: int
    conquistada_em: date | None


class MinhaGamificacaoResponse(BaseModel):
    nivel: NivelResponse  # "pontos" = XP total
    sequencia: SequenciaResponse
    conquistas: list[ConquistaResponse]
    historico: list[XpItem]  # mais recente primeiro (os ultimos 30)
