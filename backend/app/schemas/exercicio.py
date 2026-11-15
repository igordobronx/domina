import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TipoExercicio = Literal["OBJETIVO", "DISCURSIVO"]


class ExercicioRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    assunto: str = Field(min_length=1, max_length=200)  # o "tema" da tela
    materia_id: uuid.UUID
    turma_id: uuid.UUID
    tipo: TipoExercicio
    enunciado: str = Field(min_length=1, max_length=10_000)
    alternativas: list[str] | None = None
    resposta_correta: int | None = None  # indice da alternativa certa (objetivo)
    resposta_exemplo: str | None = Field(default=None, max_length=10_000)
    explicacao: str | None = Field(default=None, max_length=5_000)
    gerado_por_ia: bool = False  # o professor usou a IA para criar (vira um selo para o aluno)

    @model_validator(mode="after")
    def _confere_tipo(self):
        if self.tipo == "OBJETIVO":
            alts = [a.strip() for a in (self.alternativas or [])]
            if len(alts) < 2 or len(alts) > 6 or any(not a for a in alts):
                raise ValueError("Exercício objetivo precisa de 2 a 6 alternativas, todas preenchidas.")
            if self.resposta_correta is None or not 0 <= self.resposta_correta < len(alts):
                raise ValueError("Marque qual alternativa é a correta.")
            self.alternativas, self.resposta_exemplo = alts, None
        else:
            if not (self.resposta_exemplo or "").strip():
                raise ValueError("Exercício discursivo precisa de uma resposta de exemplo (escreva ou peça para a IA).")
            self.alternativas, self.resposta_correta = None, None
        return self


class ExercicioProfessorResponse(BaseModel):
    """O que o professor ve: tudo, mais quantos alunos fizeram."""
    id: uuid.UUID
    titulo: str
    assunto: str
    materia_id: uuid.UUID
    materia_nome: str
    turma_id: uuid.UUID
    turma_nome: str
    tipo: TipoExercicio
    enunciado: str
    alternativas: list[str] | None
    resposta_correta: int | None
    resposta_exemplo: str | None
    explicacao: str | None
    gerado_por_ia: bool
    criado_em: datetime | None
    respostas: int = 0
    acertos: int = 0


class ExercicioAlunoResponse(BaseModel):
    """O que o aluno ve: o gabarito/resposta de exemplo so aparece depois que ele responde."""
    id: uuid.UUID
    titulo: str
    assunto: str
    materia_nome: str
    professor_nome: str
    tipo: TipoExercicio
    enunciado: str
    alternativas: list[str] | None
    gerado_por_ia: bool
    criado_em: datetime | None
    minha_resposta: str | None = None
    correta: bool | None = None
    resposta_correta: int | None = None
    resposta_exemplo: str | None = None
    explicacao: str | None = None


class ResponderRequest(BaseModel):
    resposta: str = Field(min_length=1, max_length=10_000)  # objetivo: o indice ("0", "1"...); discursivo: o texto


class SugerirRequest(BaseModel):
    materia_id: uuid.UUID
    assunto: str = Field(min_length=1, max_length=200)
    tipo: TipoExercicio
    quantidade: int = Field(default=3, ge=1, le=5)
    instrucoes: str | None = Field(default=None, max_length=1_000)  # ex.: "nível fácil", "com gráfico"


class SugerirRespostaRequest(BaseModel):
    materia_id: uuid.UUID
    assunto: str | None = Field(default=None, max_length=200)
    enunciado: str = Field(min_length=1, max_length=10_000)


class SugestaoRespostaResponse(BaseModel):
    resposta_exemplo: str
