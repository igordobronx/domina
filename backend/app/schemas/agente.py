from pydantic import BaseModel, Field

from app.estudos import ExercicioGerado
from app.schemas.submissao import CorrecaoResponse


class AgenteRequest(BaseModel):
    tema: str | None = Field(default=None, max_length=500)


class AgenteResponse(BaseModel):
    # cada passo: {"tipo": "pensamento"|"ferramenta"|"aviso", ...} (ver app/agente.py)
    passos: list[dict]
    mensagem_aluno: str | None = None
    resumo_professor: str | None = None
    exercicios: list[ExercicioGerado] | None = None
    modelo_usado: str
    correcao: CorrecaoResponse | None = None
