"""Material de treino da IA propria: guarda cada pedido feito ao modelo de fora (Claude/Gemini)
e o que ele respondeu, por tarefa (corrigir, criar exercicio, ler foto...).

Para que serve: quando o Domina tiver o seu proprio modelo, ele aprende a fazer TODAS as tarefas
a partir destes pares (pedido -> resposta), com a correcao final do professor por cima quando
existir (ver exportar_treino.py). Tambem serve para comparar um modelo novo com o atual.

Como funciona: app/llm/claude.py e app/ocr/gemini.py chamam anotar() a cada resposta; isso so
guarda na memoria do pedido HTTP atual. A rota que fez o pedido chama gravar(db) antes do commit
(com a materia/professor/correcao, quando souber). Nada aqui pode derrubar a rota.
"""
import logging
from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_tarefa: ContextVar[str] = ContextVar("ia_tarefa", default="outra")
_pendentes: ContextVar[list | None] = ContextVar("ia_pendentes", default=None)
MAX_PENDENTES = 50   # script fora de uma rota (calibracao) nunca chama gravar(): nao deixa crescer
MAX_TEXTO = 200_000  # letras guardadas por pedido/resposta


@contextmanager
def tarefa(nome: str):
    """Marca que as chamadas ao modelo feitas aqui dentro sao desta tarefa."""
    ficha = _tarefa.set(nome)
    try:
        yield
    finally:
        _tarefa.reset(ficha)


def anotar(modelo: str, entrada: str, saida: str, imagens: int = 0) -> None:
    try:
        from app.config import settings

        if not settings.IA_GUARDAR_TREINO:
            return
        lista = _pendentes.get()
        if lista is None:
            lista = []
            _pendentes.set(lista)
        if len(lista) < MAX_PENDENTES:
            lista.append(dict(tarefa=_tarefa.get(), modelo=modelo, entrada=entrada[:MAX_TEXTO],
                              saida=saida[:MAX_TEXTO], imagens=imagens))
    except Exception:
        logger.exception("falha ao anotar chamada de IA")


def gravar(db: Session, materia_id=None, professor_id=None, correcao_id=None) -> None:
    """Passa para o banco o que foi anotado neste pedido. Nao da commit: quem chama decide."""
    try:
        from app.models.usuario import IaChamada

        lista = _pendentes.get() or []
        for item in lista:
            db.add(IaChamada(**item, materia_id=materia_id, professor_id=professor_id, correcao_id=correcao_id))
        lista.clear()
    except Exception:
        logger.exception("falha ao gravar chamadas de IA")
