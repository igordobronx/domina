import json, statistics as st, sys
from pathlib import Path

def pearson(a, b):
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

for arq in sys.argv[1:]:
    L = [json.loads(l) for l in Path(arq).read_text(encoding="utf-8").splitlines()]
    print(f"\n######## {Path(arq).name}: {len(L)} redacoes, modelo {L[0]['modelo'] if L else '-'}")
    for g in ("mil", "uol"):
        G = [x for x in L if x["grupo"] == g]
        if not G: continue
        it, rt = [x["ia_total"] for x in G], [x["real_total"] for x in G]
        print(f"\n== {'NOTA 1000 (INEP oficial)' if g == 'mil' else 'UOL (corretores UOL, escala 0/50/.../200)'}  n={len(G)}")
        print(f"   total: real medio {st.mean(rt):.0f} | IA media {st.mean(it):.0f} | vies {st.mean(i - r for i, r in zip(it, rt)):+.0f} | erro medio {st.mean(abs(i - r) for i, r in zip(it, rt)):.0f}")
        if g == "mil":
            print(f"   IA >= 880: {sum(i >= 880 for i in it)}/{len(G)} | IA >= 800: {sum(i >= 800 for i in it)}/{len(G)} | menor {min(it)} | maior {max(it)}")
        else:
            print(f"   correlacao totais: pearson {pearson(it, rt):.2f} | spearman {pearson(ranks(it), ranks(rt)):.2f} | |dif| <= 100: {sum(abs(i - r) <= 100 for i, r in zip(it, rt))}/{len(G)}")
            for faixa, lo, hi in (("fracas (<=350)", 0, 350), ("medias (400-600)", 400, 600), ("boas (>=700)", 700, 1000)):
                F = [x for x in G if lo <= x["real_total"] <= hi]
                if F: print(f"   {faixa:17s} real {st.mean(x['real_total'] for x in F):4.0f} -> IA {st.mean(x['ia_total'] for x in F):4.0f}")
        print("   por competencia (vies IA - real | erro medio):")
        for c in range(5):
            d = [x["ia"][c] - x["real"][c] for x in G]
            print(f"     C{c+1}: real {st.mean(x['real'][c] for x in G):5.0f}  IA {st.mean(x['ia'][c] for x in G):5.0f}  vies {st.mean(d):+5.0f}  erro {st.mean(map(abs, d)):4.0f}")
    print(f"\n   confianca media {st.mean(x['confianca'] for x in L):.2f} | tempo medio {st.mean(x['seg'] for x in L):.0f}s")


# --- Score de Correcao (0-100): media de 3 partes -------------------------------------------
# precisao : nota 1000 oficial do INEP -> 100 - erro medio/10   (mede rigidez/generosidade no topo)
# ordenacao: UOL -> spearman x 100                              (separa fraca, media e boa?)
# acerto   : UOL -> % com |IA - real| <= 100                    (a nota bate com a banca?)
# ponytail: UOL usa outra escala (passo 50, corretores UOL); trocar pela nota oficial INEP
# por competencia quando houver redacoes reais de alunos com boletim.
def score(L):
    mil = [x for x in L if x["grupo"] == "mil"]; uol = [x for x in L if x["grupo"] == "uol"]
    precisao = 100 - st.mean(abs(x["ia_total"] - x["real_total"]) for x in mil) / 10
    it, rt = [x["ia_total"] for x in uol], [x["real_total"] for x in uol]
    ordenacao = max(0.0, pearson(ranks(it), ranks(rt))) * 100
    acerto = 100 * sum(abs(i - r) <= 100 for i, r in zip(it, rt)) / len(uol)
    return precisao, ordenacao, acerto, (precisao + ordenacao + acerto) / 3


print("\n================ SCORE DE CORRECAO (0-100) ================")
print(f"{'arquivo':22s} {'precisao':>9s} {'ordenacao':>10s} {'acerto':>7s} {'SCORE':>7s}")
for arq in sys.argv[1:]:
    L = [json.loads(l) for l in Path(arq).read_text(encoding="utf-8").splitlines()]
    p, o, a, s = score(L)
    print(f"{Path(arq).stem:22s} {p:9.1f} {o:10.1f} {a:7.1f} {s:7.1f}")
