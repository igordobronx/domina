# IA própria: na gaveta (decisão de 18/11/2026)

**Decisão:** terminar o produto com Claude e Gemini; o plano da IA própria só volta depois, com uso real das escolas.
O que não espera (serve ao produto de qualquer jeito): tirar nome e CPF do que `ia_chamada` guarda, e a porta única de modelos (`app/llm`), padrão Claude/Gemini.

## Arquitetura combinada (forma A)
- "Agente da escola" = **configuração**, não máquina: memória (RAG) isolada por escola e professor, instruções, critérios, métricas. Um modelo base compartilhado.
- Depois, com dados: camada LoRA **por tarefa/matéria** (redação ENEM, exatas, geração de questões); a identidade da escola fica no RAG. Camada por escola foi descartada (MLOps pesado, escola nova nasce sem dado).
- RAG guarda conhecimento (apostila, rubrica, gabarito, correções aprovadas); LoRA guarda o jeito de corrigir.
- Modelo fica em serviço separado atrás de fila; Claude/Gemini de reserva automática. Degraus: 0 API, 1 teste no Mac, 2 GPU sob demanda, 3 GPU fixa, 4 várias.
- GPU só compensa a partir de certo volume: comparar custo de API por correção × aluguel mensal, com dados da `ia_chamada`.

## Modelos candidatos (pesquisa de 18/11/2026, links NÃO conferidos)
- **Qwen3** (Apache 2.0): 4B para provar no Mac, 14B candidato de produção. Qwen3.5-9B se quiser visão junto. Ministral 3 e Phi-4 como alternativas; Gemma 4 e Llama 3.x descartados por ora.
- Não existe benchmark público de correção de redação ENEM: o teste é nosso (53 redações INEP + 80 da segunda base + correções aprovadas; medir QWK e erro médio por competência contra a nota oficial e o Claude).
- OCR segue separado (texto transcrito é editável e indexável). Hoje o Domina não marca o erro na foto, só no texto.
- Conferir licença na página do modelo no Hugging Face antes de usar.

## Riscos a testar
Notas de redação concentradas no meio (regressão à média); falso erro em exatas quando o aluno usa outro caminho válido; LGPD (contrato com o provedor da GPU, sem logs, camadas criptografadas).
