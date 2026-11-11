from pydantic import BaseModel, EmailStr, ConfigDict, Field
import uuid
from typing import Literal

class CriarUsuarioRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str = Field(min_length=6)
    perfil: Literal["ALUNO", "PROFESSOR", "GESTOR"]  # ADMIN nunca se cria pela API
    escola_id: uuid.UUID | None = None  # so o administrador informa; os outros usam a propria escola
    turma_id: uuid.UUID | None = None  # opcional: ja matricula o professor/aluno nesta turma

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: str
    perfil: str
    escola_nome: str
