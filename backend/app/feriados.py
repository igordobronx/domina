"""Feriados nacionais do Brasil de um ano, calculados (nao precisam de manutencao anual)."""
from datetime import date, timedelta


def _pascoa(ano: int) -> date:  # algoritmo de Meeus/Jones/Butcher
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    g = (b - (b + 8) // 25 + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def feriados(ano: int) -> list[tuple[date, str]]:
    p = _pascoa(ano)
    fixos = [(1, 1, "Confraternização Universal"), (4, 21, "Tiradentes"), (5, 1, "Dia do Trabalho"),
             (9, 7, "Independência do Brasil"), (10, 12, "Nossa Senhora Aparecida"), (11, 2, "Finados"),
             (11, 15, "Proclamação da República"), (11, 20, "Consciência Negra"), (12, 25, "Natal")]
    moveis = [(p - timedelta(47), "Carnaval"), (p - timedelta(2), "Sexta-feira Santa"),
              (p + timedelta(60), "Corpus Christi")]
    return sorted([(date(ano, m, d), n) for m, d, n in fixos] + moveis)
