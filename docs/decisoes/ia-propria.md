# IA própria do Domina (16/11/2026)

**Ideia:** a IA corrige e cria exercícios **do jeito do professor**. Sem material do professor, ela usa
a inteligência do próprio modelo (redação ENEM pelo prompt v14, matemática pelo gabarito). Com
material, ela segue o que o professor mandou. Vale para qualquer matéria (redação, matemática,
teoria musical...).

## Parte 1: memória do professor (RAG) — FEITA
Código em `backend/app/ia/` e tabela `ia_trecho` (migration 0019).

1. **Aprender (material):** o professor sobe o arquivo em Materiais (`POST /materias/{id}/documentos`).
   Na hora a IA lê (PDF, foto, DOCX, TXT; PDF escaneado e foto são lidos pelo Gemini), corta em trechos e guarda. O documento fica "A IA já aprendeu"
   ou mostra o motivo de não ter lido (ex.: PDF que é só imagem).
2. **Aprender (correções):** toda vez que o professor **aprova** uma correção, ela vira um exemplo:
   resposta do aluno, nota que ele deu e se ele mudou a nota da IA. Quando ele muda uma nota, a
   tela de revisão abre o campo "Ensine a IA: por que você mudou a nota?" (opcional, o aluno não
   vê; `correcao.motivo_mudanca`). O exemplo diz para a IA que ela ERROU ali e o porquê.
   **A memória é de cada professor:** o jeito de corrigir de um não vale para outro. Material
   enviado pelo gestor vale para todos os professores da matéria.
3. **Usar:** ao corrigir ou sugerir exercício, o Domina busca na matéria os trechos e os exemplos
   mais parecidos e coloca no pedido para o modelo (`memoria.contexto_do_professor`).
   - Matérias com gabarito (exatas e teóricas): material + correções aprovadas daquele professor.
   - Matéria teórica (`MATERIA_DISCURSIVA`): a IA compara o conteúdo da resposta, não as palavras.
   - Redação ENEM: base = prompt v14; entra só o **material** do professor como complemento.
     Correções aprovadas não entram como exemplo na redação (mudaria a nota calibrada sem teste).
     Desligar: `IA_MEMORIA_NA_REDACAO=false`.
   - Exercícios ("Pedir para a IA" e "IA sugere uma resposta"): material do professor.
4. **Busca:** por sentido (embeddings do Gemini, `IA_EMBEDDINGS=gemini`, usa a `GEMINI_API_KEY`);
   se a chave faltar ou a API cair, busca por palavras. A memória nunca derruba a correção.
5. `GET /materias/{id}/ia` diz quanto a IA já aprendeu (trechos e correções).
6. `Correcao.versao_prompt` ganha `+memoria` quando a memória foi usada (dá para auditar).

## Material de treino da nossa IA — FEITO (16/11)
Objetivo do usuário: no futuro **tudo** é feito pela IA do Domina, nada por outra IA. Até lá, o que
Claude/Gemini respondem e a correção final do professor viram o material para ela aprender.

- Tabela `ia_chamada` (migration 0020), código em `backend/app/ia/registro.py`. Cada pedido ao
  modelo e a resposta ficam guardados por tarefa: `corrigir_redacao`, `corrigir_gabarito`,
  `corrigir_gabarito_teorica`, `criar_exercicios`, `resposta_de_exemplo`, `exercicios_de_reforco`,
  `ler_redacao`, `ler_folha_exatas`, `ler_material`. Só texto (foto não é copiada). Uma linha a
  mais no mesmo salvamento: não deixa lento nem gasta chave. Desligar: `IA_GUARDAR_TREINO=false`.
- A correção fica ligada à chamada (`correcao_id`): o exemplo de treino é a resposta do modelo
  **com a nota final do professor por cima** (e o motivo, quando ele mudou).
- **Ciclo, sem perder nada que a IA não aprendeu** (`backend/exportar_treino.py`):
  1. `python exportar_treino.py exportar treino.jsonl` grava o arquivo e marca o que entrou.
     Não apaga nada. Cada exemplo tem um `peso`: 1.0 para correção aprovada pelo professor,
     0.5 para correção que só a IA fez. A de peso 0.5 não é marcada: quando o professor aprovar,
     ela sai de novo com a nota dele (o `id` da linha deixa trocar a versão antiga).
  2. Treinar e conferir o modelo.
  3. `python exportar_treino.py apagar-treinados` apaga só o que foi marcado no passo 1.
  Nada é apagado por tempo nem sozinho.
- Ainda não registra os passos do agente (`app/agente.py`), só as correções que ele dispara.
- Atenção (avisado ao usuário): os termos de uso do Claude e do Gemini limitam usar as respostas
  deles para treinar modelo concorrente; conferir antes de treinar. A correção final do
  professor é dado do Domina.

## Tela "Treinar IA" — FEITA (16/11)
Menu do professor (era "Materiais e critérios"), mesmo padrão da tela de Exercícios: escolhe a
matéria e depois **Enviar arquivo** ou **Escrever instruções** (texto livre, ex.: "sempre exijo a
verificação final"). Instrução vale SEMPRE naquela matéria (não depende de parecer com o pedido) e
é a parte mais forte do contexto. Ele vê por matéria quanto a IA já aprendeu e a lista do que
enviou/escreveu, e pode apagar as próprias instruções. O que ele envia vale na hora para a correção por
API e fica guardado (tabela `ia_trecho`, nunca apagada) para a nossa IA usar quando assumir:
`python exportar_treino.py materiais materiais.jsonl` exporta essa base.

## Ainda não feito (próximos passos)
- **Parte 2, camada única:** uma interface só (`app/ia`) para "corrigir" e "gerar", para trocar
  Claude/Gemini por um modelo aberto (Qwen, Llama, Gemma) sem mexer no resto do app. Hoje o modelo
  ainda é chamado em `app/llm/claude.py` e `app/ocr/gemini.py`.
- **Parte 3, ajuste fino por matéria:** só quando houver muitas correções aprovadas. Os exemplos
  já ficam guardados em `ia_trecho` (origem `CORRECAO`), que é o dado de treino.
- Apagar material, aprender também com os
  exercícios discursivos que o professor marca Certo/Parcial/Errado, mostrar na tela quanto a IA
  aprendeu, e medir o custo dos embeddings em `custo_uso`.
- Busca em memória aguenta milhares de trechos por matéria; acima disso, trocar por pgvector.
- O aluno pode enviar a prova em **PDF** (cada página vira uma folha, como foto; `ler_folhas`).
- O modelo do app não mudou (Sonnet 5.5, Haiku 5.5 e Gemini). O usuário não quer o Fable no app.
- O embedding do Gemini (`gemini-embedding-001`) e a leitura de material por foto **não foram testados com chave real** (o ambiente
  de desenvolvimento não tem chave); os testes usam a busca por palavras.
