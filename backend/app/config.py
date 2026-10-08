import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 120
    # opcional: sem ela a API sobe normalmente, so as rotas de OCR falham
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    # onde ficam as fotos originais das redacoes (Submissao.conteudo_bruto aponta pra ca)
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# o SDK do Google le essa variavel direto do os.environ (nao do nosso objeto
# settings), entao precisamos propaga-la manualmente apos carregar o .env
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS)
