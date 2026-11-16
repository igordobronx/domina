from pydantic import BaseModel, Field

from app.schemas.submissao import CorrecaoResponse


class AgenteRequest(BaseModel):
    tema: str | None = Field(default=None, max_length=500)
    refazer: bool = False  # sem isso, um envio que o agente ja tratou devolve o resultado salvo


class ExercicioResumo(BaseModel):
    # so titulo e competencia: o gabarito/explicacao NAO podem ir para o aluno antes dele responder
    habilidade_codigo: str
    titulo: str


class AgenteResponse(BaseModel):
    # cada passo: {"tipo": "pensamento"|"ferramenta"|"aviso", ...} (ver app/agente.py)
    passos: list[dict]
    mensagem_aluno: str | None = None
    resumo_professor: str | None = None
    exercicios: list[ExercicioResumo] | None = None
    modelo_usado: str
    correcao: CorrecaoResponse | None = None
