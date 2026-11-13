import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TipoMeta = Literal["ENTREGAS", "ENTREGAS_NO_PRAZO", "NOTA_ATIVIDADE", "MEDIA_MATERIA", "DOMINIO_COMPETENCIA"]


class MetaRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=150)
    descricao: str | None = Field(default=None, max_length=1000)
    tipo: TipoMeta
    alvo: float = Field(gt=0)  # quantidade (entregas) ou percentual de 1 a 100
    materia_id: uuid.UUID | None = None  # obrigatoria em MEDIA_MATERIA e DOMINIO_COMPETENCIA
    competencia: Literal["C1", "C2", "C3", "C4", "C5"] | None = None  # so DOMINIO_COMPETENCIA
    pontos: int = Field(ge=1, le=100)
    inicio: date | None = None  # padrao: hoje (a meta so conta o que acontece daqui pra frente)
    fim: date | None = None
    # escopo: aluno_id = individual; turma_id = turma; nenhum dos dois = escola toda (so gestor)
    turma_id: uuid.UUID | None = None
    aluno_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def coerente(self):
        if self.turma_id and self.aluno_id:
            raise ValueError("Escolha turma OU aluno, não os dois.")
        if self.inicio and self.fim and self.fim < self.inicio:
            raise ValueError("O fim não pode ser antes do início.")
        if self.tipo in ("NOTA_ATIVIDADE", "MEDIA_MATERIA", "DOMINIO_COMPETENCIA") and self.alvo > 100:
            raise ValueError("Nesta meta o alvo é um percentual (1 a 100).")
        if self.tipo in ("ENTREGAS", "ENTREGAS_NO_PRAZO") and (self.alvo != int(self.alvo) or self.alvo > 1000):
            raise ValueError("O alvo é um número inteiro de entregas.")
        if self.tipo in ("MEDIA_MATERIA", "DOMINIO_COMPETENCIA") and not self.materia_id:
            raise ValueError("Escolha a matéria desta meta.")
        if self.tipo == "DOMINIO_COMPETENCIA" and not self.competencia:
            raise ValueError("Escolha a competência (C1 a C5).")
        if self.tipo != "DOMINIO_COMPETENCIA":
            self.competencia = None
        return self


class MetaEditRequest(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    descricao: str | None = Field(default=None, max_length=1000)
    fim: date | None = None  # null explicito tira o fim
    # estes dois so mudam enquanto ninguem concluiu a meta (senao o nivel de alguem mudaria de repente)
    alvo: float | None = Field(default=None, gt=0)
    pontos: int | None = Field(default=None, ge=1, le=100)


class MetaResponse(BaseModel):  # visao do professor/gestor
    id: uuid.UUID
    titulo: str
    descricao: str | None
    tipo: str
    alvo: float
    materia_id: uuid.UUID | None
    competencia: str | None
    pontos: int
    inicio: date
    fim: date | None
    escopo: Literal["ESCOLA", "TURMA", "ALUNO"]
    escopo_nome: str
    alunos_alvo: int
    concluidos: int
    pode_editar: bool


class NivelResponse(BaseModel):
    nivel: int
    nome: str
    pontos: int
    pontos_nivel_atual: int
    pontos_proximo: int | None


class MetaAlunoResponse(BaseModel):  # visao do aluno
    id: uuid.UUID
    titulo: str
    descricao: str | None
    tipo: str
    alvo: float
    progresso: float
    pontos: int
    inicio: date
    fim: date | None
    status: Literal["FUTURA", "EM_ANDAMENTO", "CONCLUIDA", "ENCERRADA"]
    concluida_em: datetime | None = None


class MinhasMetasResponse(BaseModel):
    nivel: NivelResponse
    metas: list[MetaAlunoResponse]


class RankingItem(BaseModel):  # so professor/gestor veem: por pontos, nunca por nota
    aluno_id: uuid.UUID
    nome: str
    pontos: int
    nivel: int
    nome_nivel: str
    metas_concluidas: int
