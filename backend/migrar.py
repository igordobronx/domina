"""Aplica as migracoes do Alembic. Banco que ja existia (criado pelo create_all antigo) e marcado
como 0001 antes, para o Alembic nao tentar recriar as tabelas.

    cd backend && python migrar.py
"""
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import engine

cfg = Config("alembic.ini")
tabelas = inspect(engine).get_table_names()
if "usuario" in tabelas and "alembic_version" not in tabelas:
    command.stamp(cfg, "0001")
command.upgrade(cfg, "head")
