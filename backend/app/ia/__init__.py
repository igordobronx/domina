"""IA propria do Domina: a camada que faz a IA trabalhar DO JEITO DO PROFESSOR.

Parte 1 (esta pasta, hoje): memoria por materia com principios de RAG.
- extracao.py   le o arquivo que o professor subiu (PDF, DOCX, TXT) e devolve o texto.
- embeddings.py transforma texto em vetor (Gemini) para achar trechos parecidos pelo sentido;
                sem chave, a busca cai para comparacao de palavras (funciona, so e mais simples).
- memoria.py    guarda trechos do material e as correcoes que o professor aprovou (tabela
                ia_trecho) e, na hora de corrigir ou gerar exercicio, busca os mais parecidos
                e monta o bloco de contexto que vai junto no prompt.

O modelo que escreve a resposta continua sendo Claude/Gemini por API (app/llm, app/ocr).
Proximos passos (ainda nao feitos): interface unica para trocar o modelo por um aberto e
ajuste fino por materia. Ver docs/decisoes/ia-propria.md.
"""
