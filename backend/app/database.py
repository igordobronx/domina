from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

#por padrao o sqlite imepde q mais de uma thread use a msm conexao
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False 
#como o fastapi é assyncrono com varias thread, esses argumentpos mudam o check
# se o database_url for do postgres o dicionario fica vazio {} e nao altera nada 


engine = create_engine(settings.DATABASE_URL, connect_args=connect_args) #conexao fisica com o database

#session local é uma conversa isolada com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
'''autocommit=False: Evita que alterações (como INSERT ou UPDATE) sejam salvas automaticamente sem você chamar explicitamente o db.commit().

autoflush=False: Impede que o SQLAlchemy envie alterações pendentes para o banco antes de realizar consultas, dando mais controle manual.

bind=engine: Amarra essa fábrica de sessões ao motor de banco configurado.'''


Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
#banco d dados assyncrono