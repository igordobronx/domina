import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enum import TipoEnvioEnum


class SubmissaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    atividade_id: uuid.UUID
    aluno_id: uuid.UUID
    tipo_envio: TipoEnvioEnum
    texto_ocr: str | None
    texto_confirmado: str | None
    criado_em: datetime


class ConfirmarTextoRequest(BaseModel):
    # texto revisado pelo aluno; limite folgado (redacao ENEM tem ate 30 linhas)
    texto: str = Field(min_length=1, max_length=20_000)


class CorrigirRequest(BaseModel):
    # tema da proposta (a C2 depende dele); sem tema, usa o titulo da atividade
    tema: str | None = Field(default=None, max_length=500)


class CriterioResponse(BaseModel):
    codigo: str
    nome: str
    nota: float
    nota_professor: float | None
    justificativa: str


class CorrecaoResponse(BaseModel):
    id: uuid.UUID
    submissao_id: uuid.UUID
    nota_ia: float
    nota_professor: float | None
    revisado_por: uuid.UUID | None
    confianca: float
    status: str
    modelo_usado: str
    feedback: str | None
    criterios: list[CriterioResponse]


class NotaCriterioInput(BaseModel):
    # codigo livre: "C1".."C5" na redacao, "Q1".."Qn" em exatas (ver Tema.habilidade_codigo)
    codigo: str = Field(min_length=1, max_length=20)
    # faixa valida depende do criterio (200 fixo por competencia na redacao; valor_total /
    # num_questoes em exatas, que o professor define por atividade) -- o router confere isso,
    # pois so ele conhece a atividade.
    nota: float = Field(ge=0)


class AprovarRequest(BaseModel):
    # nota final por criterio (competencia da redacao OU questao de exatas), decidida pelo
    # professor (pode so confirmar a da IA ou mudar). Quantidade varia por materia/atividade;
    # o router confere que bate exatamente com os criterios desta correcao.
    notas: list[NotaCriterioInput] = Field(min_length=1)
    feedback: str | None = Field(default=None, max_length=2000)

    @field_validator("notas")
    @classmethod
    def sem_codigo_repetido(cls, v):
        codigos = [c.codigo for c in v]
        if len(set(codigos)) != len(codigos):
            raise ValueError("cada criterio deve aparecer uma unica vez")
        return v


class MateriaResponse(BaseModel):
    id: uuid.UUID
    nome: str
    tipo: str


class CriarMateriaRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    tipo: Literal["REDACAO_ENEM", "REDACAO_OUTRO_VESTIBULAR", "MATERIA_OBJETIVA", "MATERIA_DISCURSIVA"]


class QuestaoInput(BaseModel):
    enunciado: str = Field(min_length=1, max_length=2000)
    resposta_correta: str = Field(min_length=1, max_length=500)


class AlunoResumo(BaseModel):
    id: uuid.UUID
    nome: str


class QuestaoAtividadeResponse(BaseModel):
    codigo: str
    enunciado: str


class AtividadeResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    turma: str
    materia: str
    tipo: str
    alunos: list[AlunoResumo]
    # so preenchido para materias de exatas (ver Tema.atividade_id); sem gabarito, que e so do professor
    questoes: list[QuestaoAtividadeResponse] | None = None
    # pontuacao total da atividade; em exatas e dividida igualmente entre as questoes. Na
    # redacao e sempre 1000 (5 competencias x 0..200), fixo, nao vem do professor.
    valor_total: float = 1000


class CriarAtividadeRequest(BaseModel):
    materia_id: uuid.UUID
    turma_id: uuid.UUID
    titulo: str = Field(min_length=1, max_length=200)
    tipo: Literal["REDACAO", "PROVA_DISCURSIVA", "PROVA_OBJETIVA", "EXERCICIO"]
    # gabarito: obrigatorio quando a materia e MATERIA_OBJETIVA/MATERIA_DISCURSIVA (exatas),
    # ignorado para redacao (usa as competencias C1..C5 da materia, nao da atividade)
    questoes: list[QuestaoInput] | None = None
    # so para exatas: valor total da atividade, dividido igualmente entre as questoes
    # (ex.: 4 questoes, 1000 pontos -> 250 cada). Sem isso, assume 1000.
    valor_total: float | None = Field(default=None, gt=0, le=10_000)

class EnviarTextoRequest(BaseModel):
    atividade_id: uuid.UUID
    aluno_id: uuid.UUID | None = None
    texto: str = Field(min_length=1, max_length=20_000)

class SubmissaoRevisaoResponse(BaseModel):
    id: uuid.UUID
    atividade_id: uuid.UUID
    atividade_titulo: str
    materia: str
    aluno_id: uuid.UUID
    aluno_nome: str
    status: str  # AGUARDANDO_CORRECAO | status.value da correcao
    criado_em: datetime
    nota: float | None  # nota_professor, so se aprovada
    valor_total: float  # pontuacao total da atividade (ver AtividadeResponse.valor_total)


class MinhaSubmissaoResponse(BaseModel):
    id: uuid.UUID
    atividade_id: uuid.UUID
    atividade_titulo: str
    status: str  #aguardado correcao | status.value da correcao, so se existir
    criado_em: datetime
    # preenchido assim que existe correcao: nota_ia (provisoria) ate aprovar, nota_professor
    # (final) depois -- o aluno pode gerar e ver a propria correcao antes da aprovacao
    nota: float | None
    feedback: str | None
    criterios: list[CriterioResponse] | None = None  # idem; nota_professor vem nulo ate aprovar
