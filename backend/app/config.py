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
    # nota da redacao (app/correcao.py): o Gemini divergia demais do corretor humano do INEP,
    # a nota da redacao passou a ser pelo Claude. OCR da foto e exatas continuam no Gemini.
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-5-5"
    # mais barato/rapido: gera os exercicios de pratica (app/estudos.py), que nao precisam do
    # raciocinio mais forte do Sonnet -- so a nota da redacao usa o Sonnet
    ANTHROPIC_MODEL_HAIKU: str = "claude-haiku-5-5"
    # so preciso numa chave de avaliacao gratuita (tipo "sk-ant-usr-..."), que vale pra
    # qualquer workspace da conta e exige dizer qual usar. Uma chave normal de workspace
    # (tipo "sk-ant-api03-...") nao precisa disso
    ANTHROPIC_WORKSPACE_ID: str | None = None
    # onde ficam as fotos originais das redacoes (Submissao.conteudo_bruto aponta pra ca)
    UPLOAD_DIR: str = "uploads"
    # dominios que podem chamar a API (separados por virgula) -- em produção, acrescentar a
    # URL do frontend (ex.: https://domina.vercel.app) sem remover as de localhost
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
