"""Compara a IA com a nota oficial do INEP. uso: python analisa_inep.py <ia.jsonl> [...]"""
import json, statistics as st, sys
FAIXAS = [("<=700", 0, 700), ("720-860", 720, 860), ("880-960", 880, 960), ("1000", 1000, 1000)]
for arq in sys.argv[1:]:
    L = [json.loads(l) for l in open(arq, encoding="utf-8")]
    print(f"## {arq}: {len(L)} redacoes")
    d = [abs(x["ia_total"] - x["real_total"]) for x in L]
    print(f"erro medio total {st.mean(d):.0f} | a menos de 100: {sum(v < 100 for v in d)}/{len(L)} | vies {st.mean(x['ia_total']-x['real_total'] for x in L):+.0f}")
    for c in range(5):
        e = [x["ia"][c] - x["real"][c] for x in L]
        ex = sum(x["ia"][c] == x["real"][c] for x in L)
        print(f"  C{c+1}: erro medio {st.mean(abs(v) for v in e):3.0f} | vies {st.mean(e):+4.0f} | acerta exato {ex}/{len(L)}")
    for n, lo, hi in FAIXAS:
        g = [x for x in L if lo <= x["real_total"] <= hi]
        if g: print(f"  {n:7} n={len(g):2} real {st.mean(x['real_total'] for x in g):4.0f} IA {st.mean(x['ia_total'] for x in g):4.0f}")
