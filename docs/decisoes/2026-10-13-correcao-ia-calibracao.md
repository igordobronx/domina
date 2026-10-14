# Correção por IA: onde estamos e o que falta decidir (13/10/2026)

## O que já funciona
- **Laboratório** (`/laboratorio/` no backend): o professor envia a foto da redação, confere o texto
  lido pela IA e gera a nota nas 5 competências. A nota fica pendente até ele aprovar (RN-01).
- **OCR** com Gemini (`gemini-3.5-flash`, reserva `gemini-3.5-flash-lite`).
- **Correção** com Gemini (`backend/app/correcao.py`). Prompt v2 com os descritores oficiais
  do INEP para cada nível (0 a 200) de cada competência.

## Teste com redação real
Redação do Igor no ENEM 2023, nota oficial **880**.

| Versão | Total | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|---|
| v1 + lite (reserva) | 600 | 120 | 120 | 120 | 120 | 120 |
| v2 + flash | 680 | 80 | 160 | 120 | 120 | 200 |
| v2 + lite | 680 | 120 | 160 | 120 | 120 | 160 |

- A v2 melhorou: as competências deixaram de ficar todas em 120.
- A IA ainda está **mais rígida que a banca**, principalmente na C1. Parte dos desvios que ela
  conta são erros de leitura do OCR, não do aluno.
- Não vamos ajustar o prompt para acertar uma redação só. Isso decora um caso e piora os outros.

## Próximo passo: calibração
Corrigir de 30 a 50 redações com nota oficial por competência e medir, para cada competência,
o erro médio e se a IA erra sempre para o mesmo lado (viés). Esse número também responde, no
pitch, "como vocês validaram a acurácia". Fonte candidata: corpus público **Essay-BR**
(redações no estilo ENEM com nota por competência). A licença ainda precisa ser conferida.

## Decisão em aberto: prompt, RAG ou fine-tuning
Conversa marcada com o Igor. Opções:

1. **Prompt com exemplos (few-shot):** colocar 3 a 5 redações já corrigidas, de níveis
   diferentes, como referência. É o mais barato e o primeiro a testar.
2. **RAG:** buscar, para cada redação, as redações corrigidas mais parecidas (mesmo tema ou
   mesmo tipo de erro) e mostrar ao modelo junto com a nota do professor. Serve quando houver
   uma base grande de redações corrigidas.
3. **Fine-tuning:** treinar um modelo com milhares de pares redação × nota do professor.
   É caro e exige muitos dados. Faz sentido depois do piloto, com os pares `nota_ia` ×
   `nota_professor` que o sistema já guarda (RF-22).

Ordem sugerida: calibração para medir, depois few-shot. RAG e fine-tuning só se os números
mostrarem que o few-shot não basta.
