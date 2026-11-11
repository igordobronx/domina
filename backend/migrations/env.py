"""Alembic usa o mesmo banco e os mesmos modelos do app (app.database / app.models)."""
from alembic import context

from app.database import Base, engine
from app.models import usuario as _  # noqa: F401 -- registra os modelos no metadata

target_metadata = Base.metadata


def run_migrations_online() -> None:
    with engine.connect() as connection:
        # render_as_batch: ALTER TABLE tambem funciona no sqlite (usado em dev/testes)
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
