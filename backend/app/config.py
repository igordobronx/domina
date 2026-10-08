from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 120
    # OCR do manuscrito e feito pelo Gemini. Sem a chave a API sobe normalmente,
    # so as rotas de OCR respondem 503.
    # ponytail: plano gratis do Gemini pode usar os dados para treino (conflita com RN-21);
    # ativar faturamento no AI Studio antes de usar redacao de aluno real
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.5-flash"  # o 2.5 nao aceita mais contas novas
    # reserva quando o principal estoura cota (gratis: 20 chamadas/dia) ou esta sobrecarregado.
    # mais rapido, mas erra mais palavra em letra cursiva -- a confirmacao do aluno cobre
    GEMINI_MODEL_RESERVA: str = "gemini-3.5-flash-lite"
    # onde ficam as fotos originais das redacoes (Submissao.conteudo_bruto aponta pra ca)
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
