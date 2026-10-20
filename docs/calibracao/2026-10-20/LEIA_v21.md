# Teste do v21 (nota do meio)
Mudança: em cada competência a IA pode dar a nota do meio (20, 60, 100, 140, 180) quando a redação fica
entre dois níveis, como a média de 2 corretores do INEP. Troca "na dúvida, dê 160" (C1 e C3) por "dê o meio".
Para testar, o validador precisa aceitar passos de 20: na cópia de scratch, em backend/app/correcao.py troque
`NOTAS_VALIDAS = {0, 40, 80, 120, 160, 200}` por `NOTAS_VALIDAS = set(range(0, 201, 20))`.
Rodar (thread SEM conexão ao Mac), de backend/:
DATABASE_URL=sqlite:// JWT_SECRET=x PYTHONPATH=. python ../docs/calibracao/2026-10-19/roda_inep53.py ../docs/calibracao/2026-10-20/prompt_v21.txt ../docs/calibracao/2026-10-20/inep_lite_v21.jsonl gemini-3.5-flash-lite
Depois: python ../docs/calibracao/2026-10-18/analisa_inep.py <saida>. Base: v14 = 48 (2 rodadas). Adotar só se ganhar 6+.

## Resultado (20/10, flash-lite, 53)
v21 = erro 51 (v14 = 48). A IA deu nota do meio só 1 vez em 265 notas (C4=180). Não adotado; fica o v14.
