import os

# testes nunca chamam a API de embeddings: a memoria da IA usa a busca por palavras
os.environ.setdefault("IA_EMBEDDINGS", "local")
