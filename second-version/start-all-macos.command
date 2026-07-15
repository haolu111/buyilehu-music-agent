#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$root/scripts/runtime-processes.sh"
printf 'Local MySQL root password (press Return if it is empty): '
IFS= read -r -s DB_PASSWORD
printf '\n'

cd "$root"
export DB_PASSWORD
assert_port_available 8001
assert_port_available 8080
mkdir -p "$root/.runtime"
"$root/scripts/start-frontends-macos.sh" >"$root/.runtime/frontend-supervisor.log" 2>&1 &
frontend_supervisor_pid=$!
cleanup_all() {
  "$root/scripts/stop-all-macos.sh" || true
  if kill -0 "${frontend_supervisor_pid:-0}" 2>/dev/null; then
    kill "$frontend_supervisor_pid" 2>/dev/null || true
    wait "$frontend_supervisor_pid" 2>/dev/null || true
  fi
}
trap cleanup_all EXIT
wait_for_managed_http "$frontend_supervisor_pid" "http://127.0.0.1:5173/login" "$root/.runtime/frontend-supervisor.log" 30
wait_for_managed_http "$frontend_supervisor_pid" "http://127.0.0.1:5174/login" "$root/.runtime/frontend-supervisor.log" 30
"$root/scripts/start-backends-macos.sh"
