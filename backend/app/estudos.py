"""Geracao de exercicios de pratica (plano de estudo) pelo Claude Haiku, a partir do dominio
real do aluno. Mesmo padrao do app/correcao.py: prompt -> JSON tipado pelo Pydantic. Usa o
Haiku (nao o Sonnet da correcao) porque isto e pratica, nao avaliacao -- nao precisa do
raciocinio mais forte, e sai mais barato/rapido.
"""
from pydantic import BaseModel, Field

from app.config import settings
from app.llm.claude import gerar_json
from app.schemas.dominio import DominioResponse

PROMPT = """Você é um professor de redação do ENEM. Crie exercícios de prática rápida (múltipla
escolha) para UM aluno específico, com base no desempenho real dele nas competências do ENEM
listadas abaixo (da mais fraca para a mais forte).

Para CADA competência da lista, na mesma ordem, crie um exercício de múltipla escolha (4
alternativas, exatamente 1 correta) que treine especificamente aquela competência. Seja concreto
e prático: apresente uma situação (um trecho de redação, uma tese, um conectivo, uma proposta de
intervenção incompleta) e peça para o aluno identificar ou corrigir algo nela. Não faça pergunta
teórica genérica como "o que é uma boa redação".

Competências do aluno (código, nome, domínio estimado atual):
{competencias}

Responda em JSON com esta estrutura, um exercício por competência, na mesma ordem recebida:
{{
  "exercicios": [
    {{
      "habilidade_codigo": "C1",
      "titulo": "título curto do exercício",
      "enunciado": "a pergunta, com o contexto necessário",
      "opcoes": ["alternativa A", "alternativa B", "alternativa C", "alternativa D"],
      "resposta_correta": 0,
      "explicacao": "por que essa é a correta e as outras não"
    }}
  ]
}}"""


class ExercicioGerado(BaseModel):
    habilidade_codigo: str
    titulo: str
    enunciado: str
    opcoes: list[str] = Field(min_length=4, max_length=4)
    resposta_correta: int = Field(ge=0, le=3)
    explicacao: str


class _RespostaIA(BaseModel):
    exercicios: list[ExercicioGerado]


# ponytail: cache em memoria (sem TTL/eviction) so pra nao gerar de novo (~30s no Gemini) a cada
# vez que o aluno abre a tela com o mesmo perfil de dominio; muda a chave, muda a geracao.
# Se algum dia houver mais de 1 worker, isso precisa ir pro banco/Redis.
_cache: dict[tuple, list[ExercicioGerado]] = {}


def gerar_exercicios(
    aluno_id, competencias: list[DominioResponse], forcar: bool = False,
) -> list[ExercicioGerado]:
    chave = (str(aluno_id), tuple((c.habilidade_codigo, round(c.percentual_dominio)) for c in competencias))
    if not forcar and chave in _cache:
        return _cache[chave]

    texto = "\n".join(
        f"- {c.habilidade_codigo} ({c.tema}): {round(c.percentual_dominio)}% de domínio estimado"
        for c in competencias
    )
    resultado, _ = gerar_json(
        PROMPT.format(competencias=texto), _RespostaIA, model=settings.ANTHROPIC_MODEL_HAIKU,
    )
    exercicios = resultado.exercicios
    _cache[chave] = exercicios
    return exercicios
