#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p server-runtime/audiveris server-runtime/jianpu-omr

if [[ ! -f .env.server ]]; then
  cp .env.server.example .env.server
  echo "Created .env.server from .env.server.example"
fi

echo "Checking local server runtime commands..."

if command -v tesseract >/dev/null 2>&1; then
  echo "OK: tesseract $(tesseract --version | head -1)"
else
  echo "WARN: tesseract is not installed on this host. Docker image installs it automatically."
fi

if command -v audiveris >/dev/null 2>&1; then
  echo "OK: audiveris found at $(command -v audiveris)"
else
  echo "WARN: audiveris was not found on host PATH."
  echo "      For Docker, place an Audiveris distribution under server-runtime/audiveris,"
  echo "      or edit AUDIVERIS_HOST_DIR and AUDIVERIS_COMMAND in .env.server."
fi

if [[ -n "${JIANPU_OMR_COMMAND:-}" ]]; then
  echo "OK: JIANPU_OMR_COMMAND is configured."
else
  echo "WARN: JIANPU_OMR_COMMAND is not configured."
  echo "      Put a numbered-notation OMR project under server-runtime/jianpu-omr"
  echo "      and set JIANPU_OMR_COMMAND=/opt/jianpu-omr/run.sh {input} {output}."
fi

echo
echo "Next:"
echo "  docker compose --env-file .env.server up --build"
echo "  open http://127.0.0.1:8000/api/deployment/status"
echo "  docker compose --env-file .env.server exec music-agent python scripts/preflight_competition_server.py"
