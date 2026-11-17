from pydantic import BaseModel, EmailStr, ConfigDict, Field
import uuid
from typing import Literal

class VinculoTurma(BaseModel):
    """Uma turma do usuario; no professor, as materias que ele leciona NESTA turma (aluno: vazio)."""
    turma_id: uuid.UUID
    materia_ids: list[uuid.UUID] = Field(default_factory=list)


class DefinirVinculosRequest(BaseModel):
    turmas: list[VinculoTurma]


class EditarUsuarioRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    email: EmailStr


class NovaSenhaRequest(BaseModel):
    senha: str = Field(min_length=6)


class AtivoRequest(BaseModel):
    ativo: bool


class CriarUsuarioRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str = Field(min_length=6)
    perfil: Literal["ALUNO", "PROFESSOR", "GESTOR"]  # ADMIN nunca se cria pela API
    escola_id: uuid.UUID | None = None  # so o administrador informa; os outros usam a propria escola
    turma_id: uuid.UUID | None = None  # opcional: ja matricula o professor/aluno nesta turma
    turmas: list[VinculoTurma] | None = None  # varias turmas (e materias por turma, no professor)

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: str
    perfil: str
    escola_nome: str
    ativo: bool = True
    turmas: list[str] = Field(default_factory=list)  # nomes das turmas, para a lista de pessoas
