#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_root="$root/backend/python-capability-library"
java_root="$root/backend/music-agent-server"
python_bin="${PYTHON_BIN:-/opt/homebrew/bin/python3.12}"
runtime_root="$root/.runtime"

source "$root/scripts/preflight-macos.sh" --backend
source "$root/scripts/runtime-processes.sh"
assert_port_available 8001
assert_port_available 8080
"$root/scripts/start-local-mysql84-macos.sh"

if [[ -z "${DB_PASSWORD+x}" ]]; then
  printf 'DB_PASSWORD must be set and is intentionally not stored in this repository.\n' >&2
  exit 1
fi

mkdir -p "$runtime_root"
if [[ ! -x "$python_root/.venv/bin/python" ]]; then
  "$python_bin" -m venv "$python_root/.venv"
  "$python_root/.venv/bin/pip" install -r "$python_root/requirements.txt"
fi

python_pid_file="$runtime_root/python-capability.pid"
(cd "$python_root" && exec "$python_root/.venv/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port 8001) >"$runtime_root/python-capability.log" 2>&1 &
python_pid=$!
write_managed_pid "$python_pid_file" "$python_pid"
cleanup_python() {
  stop_managed_process "$python_pid_file" "$root" || true
}
trap cleanup_python EXIT
wait_for_managed_http "$python_pid" "http://127.0.0.1:8001/api/v1/health" "$runtime_root/python-capability.log" 30

export DB_NAME="${DB_NAME:-buyilehu_music_agent_v2}"
export DB_USERNAME="${DB_USERNAME:-root}"
export PYTHON_CAPABILITY_ENABLED=true
export PYTHON_CAPABILITY_CALL_MODE="${PYTHON_CAPABILITY_CALL_MODE:-primary}"
export PYTHON_CAPABILITY_BASE_URL=http://127.0.0.1:8001

cd "$java_root"
mvn spring-boot:run
