#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo " Starting PatchForge-Nemotron Locally... "
echo "========================================="

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required."
    exit 1
fi

export PORT="${PORT:-8000}"
export HOST="${HOST:-0.0.0.0}"

echo "Serving on http://${HOST}:${PORT}"
python3 -m uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
