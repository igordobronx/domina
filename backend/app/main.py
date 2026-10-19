from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import documento, dominio, health, auth, ocr, submissoes, usuario, turma
from app.database import Base, engine
from app.models import usuario as _  # garante que os modelos estão registrados antes do create_all

Base.metadata.create_all(bind=engine)  # cria as tabelas se nao existirem (prototipo: sem Alembic por enquanto)

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]

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
app.include_router(usuario.router)
app.include_router(turma.router)
app.include_router(documento.router)
app.include_router(dominio.router)

# tela de testes do OCR + correcao (mesma origem da API, sem CORS). Abrir em /laboratorio/
app.mount("/laboratorio", StaticFiles(directory=Path(__file__).parent / "static" / "laboratorio", html=True), name="laboratorio")
