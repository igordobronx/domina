#!/bin/bash
# Valida o app (v12 + 2 correcoes + media) nas 53 do INEP com flash-lite (~106-160 chamadas).
# uso (da raiz do repo): bash docs/calibracao/2026-10-19/roda_dupla.sh
set -e
cd "$(dirname "$0")/../../../backend"
D=../docs/calibracao/2026-10-19
set -a; . ./.env; set +a
DATABASE_URL=sqlite:// JWT_SECRET=x GEMINI_MODEL=gemini-3.5-flash-lite PYTHONPATH=. .venv/bin/python $D/roda_dupla53.py $D/inep_lite_v12_dupla.jsonl 2>&1 | tee $D/log_inep_v12_dupla.txt
.venv/bin/python ../docs/calibracao/2026-10-18/analisa_inep.py $D/inep_lite_v12_dupla.jsonl | tee -a $D/log_inep_v12_dupla.txt
echo; echo "PRONTO. Pode avisar o Claude."
