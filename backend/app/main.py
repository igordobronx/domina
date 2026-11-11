import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import agente, calendario, compliance, correcoes, documento, dominio, estudos, evolucao, escolas, health, auth, painel, questoes, ocr, submissoes, usuario, turma
from app.database import Base, engine
from app.models import usuario as _  # garante que os modelos estão registrados antes do create_all

# Postgres: o esquema vem do Alembic (python migrar.py). O create_all fica so no sqlite de dev/testes.
if engine.dialect.name == "sqlite":
    Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # diz ao navegador que apenas chamadas vindas das URL's listadas  na variavel origins tem permissao p acessar aa api
    allow_credentials=True, # autoriza o envio de cookies de sessao ou cabeçalho Authorization com token JWT nas requisições
    allow_methods=["*"], #permite todos os verbos get, post, put, pathc etc
    allow_headers=["*"], #permite qqrl cabeçalho enviado pelo frontend
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(ocr.router)
app.include_router(submissoes.router)
app.include_router(correcoes.router)
app.include_router(escolas.router)
app.include_router(painel.router)
app.include_router(questoes.router)
app.include_router(usuario.router)
app.include_router(turma.router)
app.include_router(calendario.router)
app.include_router(documento.router)
app.include_router(dominio.router)
app.include_router(estudos.router)
app.include_router(evolucao.router)
app.include_router(compliance.router)
app.include_router(agente.router)

logger = logging.getLogger(__name__)


# sem isto, um erro nao tratado (ex.: violacao de constraint no banco) escapa para fora do
# CORSMiddleware e o navegador mostra soh "Failed to fetch", sem nenhuma mensagem util.
@app.exception_handler(Exception)
async def erro_nao_tratado(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("erro nao tratado em %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erro interno. Tente de novo em instantes."})

# tela de testes do OCR + correcao (mesma origem da API, sem CORS). Abrir em /laboratorio/
app.mount("/laboratorio", StaticFiles(directory=Path(__file__).parent / "static" / "laboratorio", html=True), name="laboratorio")
