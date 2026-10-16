from pydantic import BaseModel, EmailStr, ConfigDict, Field
import uuid
from typing import Literal

class CriarUsuarioRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str = Field(min_length=6)
    perfil: Literal["ALUNO", "PROFESSOR"]  # ADMIN/GESTOR não se autocadastra

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: str
    perfil: str