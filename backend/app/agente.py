"""Agente de correcao: o Claude recebe um objetivo e decide sozinho quais ferramentas usar.

Antes o fluxo era fixo no codigo (foto -> texto -> nota). Aqui o Claude e o "cerebro" e as
IAs que ja existiam (OCR, correcao da redacao, correcao de exatas, gerador de exercicios)
viram ferramentas dele. Ele olha o envio, escolhe o corretor certo, ve o historico do aluno,
decide se gera exercicios e se chama o professor. Cada passo fica gravado (com o motivo)
para o professor ver na tela.

As ferramentas em si ficam em app/routers/agente.py (elas mexem no banco); aqui fica so o loop.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Callable

from app.config import settings
from app.llm.claude import _client

logger = logging.getLogger(__name__)

MAX_PASSOS = 10  # trava de seguranca: o fluxo normal usa de 4 a 6 ferramentas

SISTEMA = """Você é o agente de correção do Domina, uma plataforma que ajuda escolas a corrigir
atividades (redação do ENEM e matemática) e a acompanhar cada aluno.

Seu objetivo: dado um envio de um aluno, deixar tudo pronto para o professor revisar e para o
aluno estudar. Você decide os passos usando as ferramentas. Um caminho típico:
1. Ler o envio (ler_envio) e verificar se o texto está legível e completo. Se o texto estiver
   ilegível, vazio ou claramente cortado (OCR ruim), use pedir_nova_foto e finalize sem corrigir.
2. Escolher o corretor certo para a matéria (corrigir_redacao_enem ou corrigir_exatas).
3. Consultar o histórico do aluno (consultar_historico_aluno) e comparar com a nota de agora.
4. Se for redação, gerar exercícios de reforço para as 1 a 3 competências mais fracas.
5. Sinalizar o professor (sinalizar_professor) quando houver motivo real: confiança baixa,
   queda grande em relação ao histórico, nota muito baixa, suspeita de fuga ao tema ou texto
   muito curto. Se não houver motivo, não sinalize.
6. Terminar SEMPRE com finalizar, com uma mensagem curta e motivadora ao aluno e um resumo
   para o professor.

Regras: a nota final é sempre do professor; a sua é provisória. Não invente notas: use só o
que as ferramentas devolverem. Em todo pedido de ferramenta, preencha "motivo" com uma frase
curta, em português simples, explicando por que você está fazendo aquele passo (o professor lê
isso na tela)."""


@dataclass
class Ferramenta:
    nome: str
    descricao: str
    propriedades: dict
    executar: Callable[[dict], dict]
    obrigatorias: list[str] = field(default_factory=list)

    def para_api(self) -> dict:
        propriedades = {
            "motivo": {"type": "string", "description": "Por que você está fazendo este passo (uma frase)."},
            **self.propriedades,
        }
        return {
            "name": self.nome,
            "description": self.descricao,
            "input_schema": {
                "type": "object",
                "properties": propriedades,
                "required": ["motivo", *self.obrigatorias],
            },
        }


class ErroFerramenta(Exception):
    """Erro esperado de uma ferramenta: volta para o agente como resultado com is_error."""


def _resumo(resultado: dict, limite: int = 600) -> str:
    texto = json.dumps(resultado, ensure_ascii=False)
    return texto if len(texto) <= limite else texto[:limite] + "..."


def rodar(pedido: str, ferramentas: list[Ferramenta], terminou: Callable[[], bool]) -> tuple[list[dict], str]:
    """Roda o loop ate o agente chamar a ferramenta de fim (terminou() vira True) ou parar.

    Devolve (passos, modelo). Cada passo e um dict que vai direto para o banco e para a tela.
    """
    modelo = settings.ANTHROPIC_MODEL
    por_nome = {f.nome: f for f in ferramentas}
    mensagens: list = [{"role": "user", "content": pedido}]
    passos: list[dict] = []

    for _ in range(MAX_PASSOS):
        resposta = _client().with_options(timeout=90.0).messages.create(
            model=modelo,
            max_tokens=8000,
            system=SISTEMA,
            tools=[f.para_api() for f in ferramentas],
            tool_choice={"type": "auto"},
            messages=mensagens,
        )
        if resposta.stop_reason == "refusal":
            raise RuntimeError("o modelo recusou o pedido")
        # devolve o conteudo inteiro (inclusive os blocos de thinking) na proxima chamada
        mensagens.append({"role": "assistant", "content": resposta.content})

        for bloco in resposta.content:
            if bloco.type == "text" and bloco.text.strip():
                passos.append({"tipo": "pensamento", "texto": bloco.text.strip()})

        chamadas = [b for b in resposta.content if b.type == "tool_use"]
        if not chamadas:
            break

        resultados = []
        for chamada in chamadas:
            entrada = dict(chamada.input)
            motivo = entrada.pop("motivo", "")
            ferramenta = por_nome.get(chamada.name)
            erro = False
            try:
                if ferramenta is None:
                    raise ErroFerramenta(f"ferramenta desconhecida: {chamada.name}")
                resultado = ferramenta.executar(entrada)
            except ErroFerramenta as e:
                resultado, erro = {"erro": str(e)}, True
            except Exception as e:  # noqa: BLE001 -- o agente decide o que fazer com a falha
                logger.exception("falha na ferramenta %s", chamada.name)
                resultado, erro = {"erro": f"falha inesperada: {e}"}, True
            passos.append({
                "tipo": "ferramenta", "ferramenta": chamada.name, "motivo": motivo,
                "entrada": entrada, "resultado": _resumo(resultado), "erro": erro,
            })
            resultados.append({
                "type": "tool_result", "tool_use_id": chamada.id,
                "content": json.dumps(resultado, ensure_ascii=False), "is_error": erro,
            })
        mensagens.append({"role": "user", "content": resultados})
        if terminou():
            break

    return passos, modelo
