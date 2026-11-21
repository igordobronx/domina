"""Pontos de cada questao: o que o professor deu a ela, ou (atividades antigas) o total dividido igual."""


def valor_da_questao(atividade, tema, n_questoes: int) -> float:
    if tema.valor is not None:
        return float(tema.valor)
    return float(atividade.valor_total or 1000) / max(n_questoes, 1)


def distribuir(valores: list[float | None], total: float) -> list[float]:
    """Pontos de cada questao: os que o professor deu; as sem valor dividem igual o que sobra.
    A soma tem que fechar o total (ValueError com a mensagem para o professor)."""
    dados = sum(v for v in valores if v is not None)
    vazias = sum(1 for v in valores if v is None)
    if vazias:
        resto = total - dados
        if resto <= 0.001:
            raise ValueError("Os pontos das questões já passam do total: sobrou nada para as outras.")
        return [round(resto / vazias, 2) if v is None else float(v) for v in valores]
    if abs(dados - total) > 0.05:
        raise ValueError(f"A soma dos pontos das questões ({dados:g}) precisa ser igual ao total ({total:g}).")
    return [float(v) for v in valores]
