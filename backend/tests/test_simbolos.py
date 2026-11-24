from app.ocr.simbolos import sem_latex


def test_latex_vira_simbolos():
    t = r"$V_m = \frac{180}{2,5} = 72\text{ km/h}$ e $F = m \cdot a \rightarrow a = 3\text{ m/s}^2$ H_2O"
    assert sem_latex(t) == "Vm = 180/2,5 = 72 km/h e F = m · a → a = 3 m/s² H₂O"


def test_texto_normal_nao_muda():
    assert sem_latex("Resposta: 5 m/s e 3 + 2 = 5") == "Resposta: 5 m/s e 3 + 2 = 5"
