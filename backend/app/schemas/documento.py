import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enum import StatusProcessamentoEnum, TipoDocumentoEnum


class DocumentoBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    materia_id: uuid.UUID
    materia_nome: str = ""
    nome_arquivo: str
    tipo: TipoDocumentoEnum
    status_processamento: StatusProcessamentoEnum
    ativo: bool = True  # false = tirado de uso: a IA nao usa e o treino ignora, mas o arquivo fica guardado
    detalhe: str | None = None  # motivo quando a IA nao conseguiu ler o arquivo
    tamanho_bytes: int | None = None
    enviado_por_nome: str = ""
    pode_baixar: bool = False  # false nos enviados antes de o arquivo ser guardado com caminho
    criado_em: datetime


class MemoriaIAResponse(BaseModel):
    trechos_de_material: int
    correcoes_aprendidas: int
    instrucoes: int = 0
    revisadas: int = 0
    iguais: int = 0
    proximas: int = 0
    longe: int = 0
    concordancia: int | None = None  # % de notas iguais ou proximas; nulo = ainda sem revisoes
    concordancia_recente: int | None = None  # so das ultimas 20
    exercicios_aprendidos: int = 0
    vies: int | None = None  # media de (nota do professor - nota da IA) em %; negativo = professor mais rigoroso
    nivel: str = "SEM_TREINO"  # SEM_TREINO | APRENDENDO | QUASE | PRONTA
    falta: list[str] = []  # o que ainda falta para a IA ficar pronta, em frases simples
    evolucao: list[dict] = []  # concordancia a cada 10 revisadas, da mais antiga para a mais nova


class ErroDaIA(BaseModel):
    submissao_id: uuid.UUID
    atividade: str
    nota_ia: float
    nota_professor: float | None
    motivo: str | None = None
    explicacao_ruim: bool = False


class InstrucaoRequest(BaseModel):
    texto: str = Field(min_length=5, max_length=2000)


class InstrucaoResponse(BaseModel):
    id: uuid.UUID
    materia_id: uuid.UUID
    texto: str
    criado_em: datetime


class SugestaoInstrucao(BaseModel):
    texto: str
    vezes: int  # em quantas correcoes o professor deu esse mesmo motivo
    correcao_ids: list[uuid.UUID]


class DispensarSugestaoRequest(BaseModel):
    correcao_ids: list[uuid.UUID] = Field(min_length=1, max_length=200)


class ItemAprendido(BaseModel):
    tipo: Literal["CORRECAO", "EXERCICIO"]
    id: uuid.UUID
    titulo: str
    trecho: str
    em_uso: bool
    erro: float  # 0 = sem erro conhecido; maior = a IA errou mais


class EmUsoRequest(BaseModel):
    em_uso: bool
