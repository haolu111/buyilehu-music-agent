#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runtime_root="$root/.runtime"

required_frontend_files=(
  "$root/frontend/teacher-web/src/components/WorkflowStepper.vue"
  "$root/frontend/teacher-web/src/assets/buyilehu-logo-sidebar.png"
  "$root/frontend/student-web/src/assets/student-music-classroom-hero.png"
)
for required_file in "${required_frontend_files[@]}"; do
  if [[ ! -f "$required_file" ]]; then
    printf 'The canonical 2026-07-15 frontend is incomplete: missing %s\n' "$required_file" >&2
    printf 'Restore the frontend from the approved teacher-workflow-refresh source before starting.\n' >&2
    exit 1
  fi
done

source "$root/scripts/preflight-macos.sh" --frontend
source "$root/scripts/runtime-processes.sh"
mkdir -p "$runtime_root"
assert_port_available 5173
assert_port_available 5174

started_pid_files=()

cleanup_started_frontends() {
  local pid_file
  for pid_file in "${started_pid_files[@]:-}"; do
    [[ -n "$pid_file" ]] || continue
    stop_managed_process "$pid_file" "$root" || true
  done
}

trap cleanup_started_frontends EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

start_frontend() {
  local name="$1"
  local directory="$2"
  local port="$3"
  if [[ ! -d "$directory/node_modules" ]]; then
    (cd "$directory" && npm ci)
  fi
  local log_file="$runtime_root/$name.log"
  local pid_file="$runtime_root/$name.pid"
  (cd "$directory" && exec "$directory/node_modules/.bin/vite" --host 127.0.0.1 --port "$port" --strictPort) >"$log_file" 2>&1 &
  local pid=$!
  write_managed_pid "$pid_file" "$pid"
  started_pid_files+=("$pid_file")
  wait_for_managed_process "$pid" "$log_file" 2
  printf '%s PID: %s, URL: http://127.0.0.1:%s/\n' "$name" "$pid" "$port"
}

if ! start_frontend teacher "$root/frontend/teacher-web" 5173; then
  cleanup_started_frontends
  exit 1
fi
if ! start_frontend student "$root/frontend/student-web" 5174; then
  exit 1
fi

printf 'Logs are in %s. Stop managed services with: ./scripts/stop-all-macos.sh\n' "$runtime_root"
teacher_pid="$(sed -n '1p' "$runtime_root/teacher.pid")"
student_pid="$(sed -n '1p' "$runtime_root/student.pid")"
monitor_managed_processes \
  "$teacher_pid" "$runtime_root/teacher.log" \
  "$student_pid" "$runtime_root/student.log"
