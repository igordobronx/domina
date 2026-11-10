#!/usr/bin/env bash
# Sobe banco (docker), API (porta 8000) e frontend (porta 5173) juntos. Ctrl+C derruba os dois.
#   ./dev.sh          # usa o backend/.env
#   ./dev.sh --seed   # roda o seed.py antes (dados de exemplo)
set -euo pipefail
cd "$(dirname "$0")"

if grep -qE '^DATABASE_URL=postgresql' backend/.env; then
  docker compose up -d --wait db || { echo "Docker/Postgres nao subiu (confira 'docker context ls')."; exit 1; }
fi

[ -d frontend/node_modules ] || (cd frontend && npm install)
[ -f frontend/.env.local ] || cp frontend/.env.example frontend/.env.local

(cd backend && [ "${1:-}" != "--seed" ] || ../venv/bin/python seed.py)

trap 'kill 0' EXIT INT TERM  # mata o grupo inteiro (uvicorn + vite)
(cd backend && ../venv/bin/uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev) &
wait
