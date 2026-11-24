"""Converte LaTeX que o OCR as vezes devolve ($\\frac{1}{2}$, \\cdot, x^{2}) em simbolos comuns (1/2, ·, x²)."""
import re

_SIMBOLOS = {
    r"\cdot": "·", r"\times": "×", r"\div": "÷", r"\pm": "±", r"\mid": "|", r"\circ": "°",
    r"\rightarrow": "→", r"\to": "→", r"\Rightarrow": "⇒", r"\leftarrow": "←", r"\leq": "≤", r"\geq": "≥",
    r"\neq": "≠", r"\approx": "≈", r"\infty": "∞", r"\sqrt": "√", r"\Delta": "Δ", r"\delta": "δ",
    r"\Omega": "Ω", r"\omega": "ω", r"\pi": "π", r"\theta": "θ", r"\alpha": "α", r"\beta": "β",
    r"\mu": "μ", r"\lambda": "λ", r"\sigma": "σ", r"\rho": "ρ", r"\varepsilon": "ε",
}
_SUP = str.maketrans("0123456789+-n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿ")
_SUB = str.maketrans("0123456789+-", "₀₁₂₃₄₅₆₇₈₉₊₋")


def _supsub(m: re.Match) -> str:
    sinal, conteudo = m.group(1), m.group(2) or m.group(3)
    tabela = _SUP if sinal == "^" else _SUB
    if all(c in "0123456789+-n" if sinal == "^" else c in "0123456789+-" for c in conteudo):
        return conteudo.translate(tabela)
    return conteudo if sinal == "_" else f"^{conteudo}"  # indice de letra (V_m): so tira o "_"


def sem_latex(texto: str) -> str:
    if "\\" not in texto and "$" not in texto and "^" not in texto:
        return texto
    t = re.sub(r"\\(?:text|mathrm|mathbf|textbf)\{([^{}]*)\}", r"\1", texto)
    t = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", t)
    for latex, simbolo in sorted(_SIMBOLOS.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(re.escape(latex) + r"(?![A-Za-z])", simbolo, t)
    t = re.sub(r"([_^])(?:\{([^{}]*)\}|([0-9A-Za-z+-]))", _supsub, t)
    t = t.replace("\\,", " ").replace("\\ ", " ").replace("\\%", "%")
    return t.replace("$", "")
