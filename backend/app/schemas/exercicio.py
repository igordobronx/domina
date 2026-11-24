import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TipoExercicio = Literal["OBJETIVO", "DISCURSIVO"]
Resultado = Literal["CERTA", "PARCIAL", "ERRADA"]


class QuestaoExercicio(BaseModel):
    """Uma questao do exercicio (enunciado + gabarito). O exercicio pode ter varias."""
    tipo: TipoExercicio
    enunciado: str = Field(min_length=1, max_length=10_000)
    alternativas: list[str] | None = None
    resposta_correta: int | None = None  # indice da alternativa certa (objetivo)
    resposta_exemplo: str | None = Field(default=None, max_length=10_000)
    # varias respostas de exemplo (discursivo); se vier, vale esta lista e resposta_exemplo vira a 1a
    respostas_exemplo: list[str] | None = Field(default=None, max_length=5)
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
            self.alternativas, self.resposta_exemplo, self.respostas_exemplo = alts, None, None
        else:
            lista = self.respostas_exemplo if self.respostas_exemplo is not None else [self.resposta_exemplo or ""]
            lista = [x.strip() for x in lista if x and x.strip()]
            if any(len(x) > 10_000 for x in lista):
                raise ValueError("Resposta de exemplo longa demais.")
            if not lista:
                raise ValueError("Exercício discursivo precisa de uma resposta de exemplo (escreva ou peça para a IA).")
            self.respostas_exemplo, self.resposta_exemplo = lista, lista[0]
            self.alternativas, self.resposta_correta = None, None
        return self


class ExercicioRequest(QuestaoExercicio):
    titulo: str = Field(min_length=1, max_length=200)
    assunto: str = Field(min_length=1, max_length=200)  # o "tema" da tela
    materia_id: uuid.UUID
    turma_id: uuid.UUID
    # so para estes alunos da turma; vazio/nulo = a turma toda
    aluno_ids: list[uuid.UUID] | None = None


class ExercicioLoteRequest(ExercicioRequest):
    """Criar o mesmo exercicio em varias turmas: vira um exercicio separado por turma.
    Com aluno_ids, os alunos podem ser de turmas diferentes: cada turma recebe a sua copia so com
    os alunos dela, e turma sem nenhum aluno escolhido fica de fora."""
    turma_id: uuid.UUID | None = None
    turma_ids: list[uuid.UUID] = Field(min_length=1)
    # questoes alem da principal (a de cima): o exercicio fica com varias, todas no mesmo grupo
    mais_questoes: list[QuestaoExercicio] = Field(default_factory=list, max_length=19)


class RespostaAlunoResponse(BaseModel):
    """Uma linha da tela "Ver respostas": cada aluno que deve fazer o exercicio, fez ou nao."""
    aluno_id: uuid.UUID
    nome: str
    fez: bool
    resposta: str | None = None
    correta: bool | None = None
    resultado: Resultado | None = None
    comentario: str | None = None
    respondido_em: datetime | None = None


class AvaliarRespostaRequest(BaseModel):
    # so os campos enviados mudam; resultado=null desfaz a correcao (so no discursivo)
    resultado: Resultado | None = None
    comentario: str | None = Field(default=None, max_length=5_000)


class ResumoAlunoResponse(BaseModel):
    """Resumo da turma por aluno, nos exercicios deste professor."""
    aluno_id: uuid.UUID
    nome: str
    total: int  # exercicios para ele
    feitos: int
    acertos: int
    parciais: int
    corrigidos: int  # com certo/errado definido (objetivo sempre; discursivo quando o professor marca)


class ExercicioProfessorResponse(BaseModel):
    """O que o professor ve: tudo, mais quantos alunos fizeram."""
    id: uuid.UUID
    titulo: str
    assunto: str
    materia_id: uuid.UUID
    materia_nome: str
    turma_id: uuid.UUID
    turma_nome: str
    aluno_ids: list[uuid.UUID] | None = None  # nulo = turma toda
    alunos_nomes: list[str] = []
    tipo: TipoExercicio
    enunciado: str
    alternativas: list[str] | None
    resposta_correta: int | None
    resposta_exemplo: str | None
    respostas_exemplo: list[str] = []
    explicacao: str | None
    gerado_por_ia: bool
    criado_em: datetime | None
    respostas: int = 0
    acertos: int = 0
    alunos_alvo: int = 0  # quantos alunos devem fazer (turma toda ou os escolhidos)
    grupo_id: uuid.UUID | None = None  # questoes do mesmo exercicio dividem o grupo
    ordem: int = 0


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
    resultado: Resultado | None = None
    comentario: str | None = None  # do professor
    resposta_correta: int | None = None
    resposta_exemplo: str | None = None
    respostas_exemplo: list[str] = []
    explicacao: str | None = None
    grupo_id: uuid.UUID | None = None
    ordem: int = 0


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
