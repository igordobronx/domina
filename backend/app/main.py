import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.routers import agente, calendario, compliance, correcoes, documento, dominio, estudos, evolucao, escolas, health, auth, logs, painel, questoes, ocr, submissoes, usuario, turma
from app.auth.security import decode_access_token
from app.database import Base, engine
from app.logs import configurar_logging, ip_ctx, ip_do_cliente, novo_request_id, request_id_ctx
from app.seguranca import ACESSO_NEGADO, NAO_AUTENTICADO, registrar_seguranca
from app.models import usuario as _  # garante que os modelos estão registrados antes do create_all

# Postgres: o esquema vem do Alembic (python migrar.py). O create_all fica so no sqlite de dev/testes.
if engine.dialect.name == "sqlite":
    Base.metadata.create_all(bind=engine)

configurar_logging()
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
app.include_router(logs.router)
app.include_router(documento.router)
app.include_router(dominio.router)
app.include_router(estudos.router)
app.include_router(evolucao.router)
app.include_router(compliance.router)
app.include_router(agente.router)

logger = logging.getLogger(__name__)
acesso = logging.getLogger("domina.acesso")


def _usuario_do_token(request: Request) -> str | None:
    # so le o "sub" do JWT (assinatura validada); nao consulta o banco e nunca grava o token
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    try:
        return decode_access_token(auth[7:]).get("sub")
    except Exception:
        return None


# ACCESS LOG: uma linha JSON por requisicao, no stdout. Sem corpo, sem query string, sem token.
@app.middleware("http")
async def access_log(request: Request, call_next):
    request_id_ctx.set(novo_request_id())
    ip_ctx.set(ip_do_cliente(request))
    inicio = time.perf_counter()
    status_code = 500  # se call_next estourar, o erro sobe e o handler abaixo responde 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id_ctx.get()
        return response
    finally:
        rota = request.scope.get("route")
        caminho = rota.path if rota else request.url.path  # modelo "/eventos/{evento_id}": sem ids no log
        usuario_id = _usuario_do_token(request)
        acesso.info("%s %s %s", request.method, caminho, status_code, extra={"campos": {
            "metodo": request.method, "rota": caminho, "status": status_code,
            "ms": round((time.perf_counter() - inicio) * 1000, 1), "ip": ip_ctx.get(), "usuario_id": usuario_id,
        }})
        # 401/403 de qualquer rota viram evento de seguranca (o login tem o seu proprio LOGIN_FALHA)
        if status_code in (401, 403) and caminho != "/auth/login":
            await run_in_threadpool(
                registrar_seguranca, NAO_AUTENTICADO if status_code == 401 else ACESSO_NEGADO,
                uuid.UUID(usuario_id) if usuario_id else None, None, f"{request.method} {caminho}",
            )


# sem isto, um erro nao tratado (ex.: violacao de constraint no banco) escapa para fora do
# CORSMiddleware e o navegador mostra soh "Failed to fetch", sem nenhuma mensagem util.
@app.exception_handler(Exception)
async def erro_nao_tratado(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("erro nao tratado em %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erro interno. Tente de novo em instantes."})

# tela de testes do OCR + correcao (mesma origem da API, sem CORS). Abrir em /laboratorio/
app.mount("/laboratorio", StaticFiles(directory=Path(__file__).parent / "static" / "laboratorio", html=True), name="laboratorio")
