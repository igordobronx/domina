#!/bin/bash
# Roda o prompt v9 (flash-lite) na base INEP (53). uso: bash docs/calibracao/2026-10-19/roda_v9.sh (da raiz do repo)
set -e
cd "$(dirname "$0")/../../../backend"
D=../docs/calibracao
P=$D/2026-10-18/prompt_v9.txt
M=gemini-3.5-flash-lite
PYTHONPATH=. .venv/bin/python $D/2026-10-18/roda_inep.py $P $D/2026-10-19/inep_lite_v9.jsonl $M 2>&1 | tee $D/2026-10-19/log_inep_v9.txt
echo; echo "PRONTO. Pode avisar o Claude."
