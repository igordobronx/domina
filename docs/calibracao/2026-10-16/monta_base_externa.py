"""Monta essays/base_teste_externa.xlsm a partir da original (molde) com amostra de AES-ENEM e Essay-BR.
uso: backend/.venv/bin/python <este> (de dentro da raiz do repo)
"""
import ast, collections, copy, csv, random, re, shutil, unicodedata
from pathlib import Path

import openpyxl
import pyarrow.parquet as pq

RAIZ = Path.cwd()
ORIG = RAIZ / "essays" / "base_redacoes_enem_domina_ai.xlsm"
NOVA = RAIZ / "essays" / "base_teste_externa.xlsm"
EXT = Path.home() / "Downloads" / "domina_dados_externos"
CSV_CORRETORES = RAIZ / "docs" / "calibracao" / "2026-10-16" / "aes_enem_notas_corretores.csv"
URL_AES = "https://huggingface.co/datasets/kamel-usp/aes_enem_dataset"
URL_EBR = "https://github.com/rafaelanchieta/essay"
FAIXAS = [("<=400", 0, 400), ("440-600", 440, 600), ("640-800", 640, 800), ("840-960", 840, 960), ("1000", 1000, 1000)]
NOTAS_OK = {0, 40, 80, 120, 160, 200}
csv.field_size_limit(10**9)


def norm(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)[:120]


def faixa(total):
    for nome, a, b in FAIXAS:
        if a <= total <= b:
            return nome
    return None


def palavras(t):
    return len(str(t).split())


# --- textos ja existentes na base original (UOL + nota 1000), para nao repetir
wb_o = openpyxl.load_workbook(ORIG, read_only=True, data_only=True)
existentes = {norm(r[3]) for r in list(wb_o["Redações"].iter_rows(values_only=True))[1:] if r[0] and r[3]}

# --- AES-ENEM
def le(sub, split):
    p = EXT / "aes_enem" / sub / f"{split}.parquet"
    return [dict(x, _sub=sub, _split=split) for x in pq.read_table(p).to_pylist()] if p.exists() else []

def notas(g):
    g = [int(x) for x in (ast.literal_eval(g) if isinstance(g, str) else g)]
    return g[:5]

grupos = collections.defaultdict(dict)  # texto normalizado -> {reference: linha}
for split in ("train", "validation", "test"):
    for x in le("sourceAWithGraders", split):
        grupos[norm(x["essay_text"])][x["reference"]] = x
com_corretores = [g for g in grupos.values() if {"crawled_from_web", "grader_a", "grader_b"} <= g.keys()]
reserva = [x for s in ("train", "validation", "test") for x in le("sourceAOnly", s)] + le("sourceB", "full")
mil = [x for s in ("train", "validation", "test") for x in le("gradesThousand", s)]

problemas = []

def valido(x):
    n = notas(x["grades"])
    if any(v not in NOTAS_OK for v in n):
        problemas.append(f"AES {x['_sub']} {x['id']}: nota fora da escala {n}"); return False
    return palavras(x["essay_text"]) >= 120 and norm(x["essay_text"]) not in existentes

rnd = random.Random(7)
usados = set()
aes = []  # (linha, grupo_ou_None, faixa)
for nome, _, _ in FAIXAS:
    cand = [g for g in com_corretores if valido(g["crawled_from_web"]) and faixa(sum(notas(g["crawled_from_web"]["grades"]))) == nome]
    rnd.shuffle(cand)
    pegos = []
    for g in cand:
        k = norm(g["crawled_from_web"]["essay_text"])
        if k not in usados and len(pegos) < 10:
            usados.add(k); pegos.append((g["crawled_from_web"], g, nome))
    if len(pegos) < 10:
        extra = [x for x in (mil if nome == "1000" else []) + reserva if valido(x) and faixa(sum(notas(x["grades"]))) == nome]
        rnd.shuffle(extra)
        for x in extra:
            k = norm(x["essay_text"])
            if k not in usados and len(pegos) < 10:
                usados.add(k); pegos.append((x, None, nome))
    aes += pegos

# --- Essay-BR
def _lista(t):
    try:
        return ast.literal_eval(t)
    except (SyntaxError, ValueError):  # algumas propostas vem como texto puro
        return [t]

P = {p["id"]: _lista(p["description"]) for p in csv.DictReader(open(EXT / "essay_br" / "prompts.csv", encoding="utf-8"))}

# titulos das propostas: o prompts.csv do Essay-BR estendido tem o titulo; casa pelo inicio do texto da proposta
TIT = {norm(" ".join(_lista(p["description"])))[:80]: p["title"].strip()
       for p in csv.DictReader(open(EXT / "essay_br" / "prompts_extended.csv", encoding="utf-8"))}

def titulo(texto_proposta):
    return TIT.get(norm(texto_proposta)[:80])

def tema_ebr_antigo(pid):
    # shortcut: o Essay-BR nao tem o titulo do tema, so o texto da proposta; usa a 1a pergunta (ou 1a frase), ate 200 chars
    txt = " ".join(P.get(pid, []))
    perg = re.findall(r"[^.?!]*\?", txt)
    t = (perg[0] if perg else re.split(r"(?<=[.!])\s", txt)[0]).strip()
    return t[:200]

ebr_pool = []
for r in csv.DictReader(open(EXT / "essay_br" / "essay-br.csv", encoding="utf-8")):
    texto = "\n".join(ast.literal_eval(r["essay"]))
    n = [int(v) for v in ast.literal_eval(r["competence"])]
    if any(v not in NOTAS_OK for v in n):
        problemas.append(f"EBR prompt {r['prompt']}: nota fora da escala {n}"); continue
    if sum(n) != int(r["score"]):
        problemas.append(f"EBR prompt {r['prompt']}: soma {sum(n)} != score {r['score']}")
    if palavras(texto) >= 120 and norm(texto) not in existentes:
        ebr_pool.append((r, texto, n))
ebr = []
for nome, _, _ in FAIXAS:
    cand = [c for c in ebr_pool if faixa(sum(c[2])) == nome]
    rnd.shuffle(cand)
    pegos = []
    for c in cand:
        k = norm(c[1])
        if k not in usados and len(pegos) < 6:
            usados.add(k); pegos.append((*c, nome))
    ebr += pegos

# --- linhas da planilha (mesmas 14 colunas da original)
linhas, corretores = [], []
temas_fonte = collections.Counter()
for x, g, fx in aes:
    ano = int(x["essay_year"]) if str(x.get("essay_year", "-1")) not in ("-1", "", "None") else None
    tema = titulo(x.get("prompt") or "") or (x.get("id_prompt") or "").replace("-", " ").strip().capitalize()
    temas_fonte["titulo" if titulo(x.get("prompt") or "") else "slug"] += 1
    obs = (f"AES-ENEM, subconjunto {'sourceAWithGraders' if g else x['_sub']} ({x['_split']}), id {x['id']}. "
           "Nota do site de origem, dada por corretor do site (não é nota oficial do INEP). "
           + ("Notas de mais 2 corretores em docs/calibracao/2026-10-16/aes_enem_notas_corretores.csv. " if g else "")
           + ("" if titulo(x.get("prompt") or "") else "Tema derivado do identificador da proposta (sem acentos). ") + "Licença: MIT/Apache-2.0 (card do dataset).")
    linhas.append(dict(ano=ano, tema=tema, texto=x["essay_text"].strip(), n=notas(x["grades"]),
                       origem="AES-ENEM (USP, Hugging Face kamel-usp)", link=URL_AES, obs=obs, faixa=fx, fonte="AES"))
    if g:
        corretores.append((len(linhas), notas(g["crawled_from_web"]["grades"]), notas(g["grader_a"]["grades"]), notas(g["grader_b"]["grades"])))
for r, texto, n, fx in ebr:
    obs = (f"Essay-BR (Marinho, Anchiêta e Moura, 2021), proposta {r['prompt']}. Redações do Banco de Redações "
           "UOL/Brasil Escola, notas na escala do ENEM dadas por corretores do site (não é nota oficial do INEP). "
           "Licença: MIT.")
    linhas.append(dict(ano=None, tema=titulo(" ".join(P.get(r["prompt"], []))) or tema_ebr_antigo(r["prompt"]), texto=texto.strip(), n=n,
                       origem="Essay-BR (UFPI, GitHub rafaelanchieta/essay)", link=URL_EBR, obs=obs, faixa=fx, fonte="EBR"))

# --- escreve usando a original como molde
shutil.copyfile(ORIG, NOVA)
wb = openpyxl.load_workbook(NOVA, keep_vba=True)
ws = wb["Redações"]
molde = [copy.copy(c._style) for c in ws[2]]  # estilo de cada coluna, da 1a linha de dados
lmolde = copy.copy(ws["L2"].font)
ws.delete_rows(2, ws.max_row)
for i, l in enumerate(linhas, start=2):
    vals = [f"{i - 1:04d}", l["ano"], l["tema"], l["texto"], *l["n"], f"=SUM(E{i}:I{i})", l["origem"], "Ver link", None, l["obs"]]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c._style = copy.copy(molde[j - 1])
    ws.cell(row=i, column=12).hyperlink = l["link"]
    ws.cell(row=i, column=12).font = copy.copy(lmolde)
ult = len(linhas) + 1
ws.auto_filter.ref = f"A1:N{ult}"
for dv in ws.data_validations.dataValidation:
    dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange(f"E2:I{ult}")

t = wb["Temas por ano"]
t.delete_rows(2, t.max_row)
temas = sorted({(l["ano"], l["tema"]) for l in linhas if l["ano"]}, key=lambda a: (a[0], a[1]))
for i, (a, tm) in enumerate(temas, start=2):
    t.cell(row=i, column=1, value=a); t.cell(row=i, column=2, value=tm)

im = wb["Imagens"]
im.delete_rows(2, im.max_row)
im._images = []  # as redacoes novas nao tem imagem

# aba extra: comparacao entre os 3 corretores do AES-ENEM
cmp_ = wb.create_sheet("Comparação corretores")
comps = ["C1", "C2", "C3", "C4", "C5", "Total"]
cab = (["ID da redação", "Ano"] + [f"Original {c}" for c in comps] + [f"Corretor A {c}" for c in comps]
       + [f"Corretor B {c}" for c in comps] + [f"|Orig−A| {c}" for c in comps] + [f"|Orig−B| {c}" for c in comps] + [f"|A−B| {c}" for c in comps])
hstyle = copy.copy(ws["A1"]._style)
for j, v in enumerate(cab, start=1):
    c = cmp_.cell(row=1, column=j, value=v); c._style = copy.copy(hstyle)
dif = {"oa": [], "ob": [], "ab": []}
for i, (lin, o, a, b) in enumerate(corretores, start=2):
    o6, a6, b6 = o + [sum(o)], a + [sum(a)], b + [sum(b)]
    oa, ob, ab = ([abs(p - q) for p, q in zip(x, y)] for x, y in ((o6, a6), (o6, b6), (a6, b6)))
    dif["oa"].append(oa); dif["ob"].append(ob); dif["ab"].append(ab)
    for j, v in enumerate([f"{lin - 1:04d}", linhas[lin - 2]["ano"], *o6, *a6, *b6, *oa, *ob, *ab], start=1):
        cmp_.cell(row=i, column=j, value=v)
r = len(corretores) + 3
cmp_.cell(row=r, column=1, value="Diferença média").font = openpyxl.styles.Font(bold=True)
cmp_.cell(row=r + 1, column=1, value="% concordância exata").font = openpyxl.styles.Font(bold=True)
for bloco, chave in enumerate(("oa", "ob", "ab")):
    for k in range(6):
        col = 21 + bloco * 6 + k
        vals = [d[k] for d in dif[chave]]
        if vals:
            cmp_.cell(row=r, column=col, value=round(sum(vals) / len(vals), 1))
            cmp_.cell(row=r + 1, column=col, value=round(100 * sum(v == 0 for v in vals) / len(vals)))
cmp_.freeze_panes = "C2"
cmp_.column_dimensions["A"].width = 14
wb.save(NOVA)

CSV_CORRETORES.parent.mkdir(parents=True, exist_ok=True)
with CSV_CORRETORES.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id_planilha"] + [f"orig_C{k}" for k in range(1, 6)] + ["orig_total"] + [f"grader_a_C{k}" for k in range(1, 6)] + ["grader_a_total"] + [f"grader_b_C{k}" for k in range(1, 6)] + ["grader_b_total"])
    for lin, o, a, b in corretores:
        w.writerow([f"{lin:04d}", *o, sum(o), *a, sum(a), *b, sum(b)])

# --- relatorio
cont = collections.Counter((l["fonte"], l["faixa"]) for l in linhas)
for fonte in ("AES", "EBR"):
    print(fonte, {fx: cont[(fonte, fx)] for fx, _, _ in FAIXAS}, "| palavras medias", round(sum(palavras(l["texto"]) for l in linhas if l["fonte"] == fonte) / max(1, sum(l["fonte"] == fonte for l in linhas))))
print("AES com 2 corretores:", len(corretores), "| AES sem:", sum(1 for _, g, _ in aes if not g), {x["_sub"] for x, g, _ in aes if not g})
if corretores:
    d = lambda p, q: sum(abs(sum(p) - sum(q)) for _ in [0])
    oa = sum(abs(sum(o) - sum(a)) for _, o, a, b in corretores) / len(corretores)
    ob = sum(abs(sum(o) - sum(b)) for _, o, a, b in corretores) / len(corretores)
    ab = sum(abs(sum(a) - sum(b)) for _, o, a, b in corretores) / len(corretores)
    print(f"|dif| media no total: orig x A {oa:.0f} | orig x B {ob:.0f} | A x B {ab:.0f}")
print("pool com corretores:", len(com_corretores), "| problemas:", len(problemas), problemas[:8])
print("temas por ano:", len(temas))

print("temas AES:", dict(temas_fonte), "| EBR com titulo:", sum(1 for r_, t_, n_, f_ in ebr if titulo(" ".join(P.get(r_["prompt"], [])))))
