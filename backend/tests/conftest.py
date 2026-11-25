import os

# testes nunca chamam a API de embeddings: a memoria da IA usa a busca por palavras
os.environ.setdefault("IA_EMBEDDINGS", "local")

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _sem_ia_de_subtopico(monkeypatch):
    # testes nunca chamam o Claude para identificar subtopicos
    monkeypatch.setattr("app.subtopicos.identificar", lambda materia, enunciados, *a, **k: [None] * len(enunciados))
