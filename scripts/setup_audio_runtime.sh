#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Missing virtualenv python at ${PYTHON_BIN}" >&2
  exit 1
fi

"${PYTHON_BIN}" -m pip install -r "${ROOT_DIR}/requirements.txt"
"${PYTHON_BIN}" -m pip install tinysoundfont --no-deps
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/cache_soundfonts.py"

echo "Audio runtime is ready."
