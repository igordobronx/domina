"""Compara a IA com as notas humanas da base externa (AES-ENEM com 3 humanos, Essay-BR com 1).
uso (de backend/): .venv/bin/python ../docs/calibracao/2026-10-16/analisa_externa.py <ia1.jsonl> [<ia2.jsonl> ...]
"""
import csv, json, statistics as st, sys
from pathlib import Path



def pearson(a, b):  # mesmas funcoes de calibracao/analisa.py (que roda ao importar)
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den if den else float("nan")


def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2
        i = j + 1
    return r

AQUI = Path(__file__).parent
HUM = {r["id_planilha"]: r for r in csv.DictReader(open(AQUI / "aes_enem_notas_corretores.csv"))}
FAIXAS = [("<=400", 0, 400), ("440-600", 440, 600), ("640-800", 640, 800), ("840-960", 840, 960), ("1000", 1000, 1000)]


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def comp(r, quem):
    return [int(r[f"{quem}_C{k}"]) for k in range(1, 6)]


for arq in sys.argv[1:]:
    L = [json.loads(l) for l in open(arq, encoding="utf-8")]
    aes = [x for x in L if x["grupo"] == "aes" and x["id"] in HUM]
    ebr = [x for x in L if x["grupo"] == "ebr"]
    print(f"\n######## {Path(arq).name}: {len(L)} redacoes ({len(aes)} AES-ENEM, {len(ebr)} Essay-BR)")
    ia = [x["ia_total"] for x in aes]
    site = [int(HUM[x["id"]]["orig_total"]) for x in aes]
    a = [int(HUM[x["id"]]["grader_a_total"]) for x in aes]
    b = [int(HUM[x["id"]]["grader_b_total"]) for x in aes]
    med = [(s + p + q) / 3 for s, p, q in zip(site, a, b)]
    dm = lambda u, v: st.mean(abs(p - q) for p, q in zip(u, v))
    print("  AES-ENEM, diferenca media no total:")
    print(f"    IA x site {dm(ia, site):.0f} | IA x A {dm(ia, a):.0f} | IA x B {dm(ia, b):.0f} | IA x media dos 3 humanos {dm(ia, med):.0f}")
    print(f"    (humanos entre si: site x A {dm(site, a):.0f} | site x B {dm(site, b):.0f} | A x B {dm(a, b):.0f})")
    print(f"    IA a menos de 100 da media humana: {sum(abs(i - m) < 100 for i, m in zip(ia, med))}/{len(aes)}")
    print(f"    spearman IA x media humana {spearman(ia, med):.2f} | (A x B {spearman(a, b):.2f} | site x media A,B {spearman(site, [(p + q) / 2 for p, q in zip(a, b)]):.2f})")
    print("    por faixa (nota do site): site | A | B | IA")
    for nome, lo, hi in FAIXAS:
        ix = [k for k, s in enumerate(site) if lo <= s <= hi]
        if ix:
            print(f"      {nome:8} {st.mean(site[k] for k in ix):5.0f} {st.mean(a[k] for k in ix):5.0f} {st.mean(b[k] for k in ix):5.0f} {st.mean(ia[k] for k in ix):5.0f}")
    print("    por competencia, diferenca media IA x media humana | (A x B):")
    for c in range(5):
        mh = [(comp(HUM[x["id"]], "orig")[c] + comp(HUM[x["id"]], "grader_a")[c] + comp(HUM[x["id"]], "grader_b")[c]) / 3 for x in aes]
        iac = [x["ia"][c] for x in aes]
        ab = st.mean(abs(comp(HUM[x["id"]], "grader_a")[c] - comp(HUM[x["id"]], "grader_b")[c]) for x in aes)
        print(f"      C{c + 1}: {dm(iac, mh):4.0f} | ({ab:.0f})  vies IA {st.mean(i - m for i, m in zip(iac, mh)):+.0f}")
    if ebr:
        ie, re_ = [x["ia_total"] for x in ebr], [x["real_total"] for x in ebr]
        print(f"  Essay-BR: diferenca media IA x site {dm(ie, re_):.0f} | spearman {spearman(ie, re_):.2f} | vies {st.mean(i - r for i, r in zip(ie, re_)):+.0f}")
        for nome, lo, hi in FAIXAS:
            ix = [k for k, s in enumerate(re_) if lo <= s <= hi]
            if ix:
                print(f"      {nome:8} site {st.mean(re_[k] for k in ix):5.0f} | IA {st.mean(ie[k] for k in ix):5.0f}")
