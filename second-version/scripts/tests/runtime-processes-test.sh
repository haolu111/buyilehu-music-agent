#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
library="$project_root/scripts/runtime-processes.sh"
tmp="$(mktemp -d)"
managed_pids=()

cleanup() {
  local pid
  for pid in "${managed_pids[@]:-}"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  rm -rf "$tmp"
}
trap cleanup EXIT

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$1"
}

free_port() {
  python3 - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
}

wait_for_listener() {
  local port="$1" pid="$2" attempt
  for attempt in $(seq 1 50); do
    if lsof -a -p "$pid" -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.1
  done
  fail "test HTTP server did not listen on port $port"
}

[[ -f "$library" ]] || fail "missing $library"
# shellcheck source=../runtime-processes.sh
source "$library"

available_port="$(free_port)"
assert_port_available "$available_port" || fail "free port was rejected"
pass "free port is accepted"

if ! bash -c 'set -euo pipefail; source "$1"; assert_port_available "$2"; printf survived' _ "$library" "$available_port" >"$tmp/strict.out"; then
  fail "free-port check exits under set -e and pipefail"
fi
grep -Fx 'survived' "$tmp/strict.out" >/dev/null || fail "strict shell did not continue after free-port check"
pass "free port works under strict shell options"

foreign_root="$tmp/foreign-project"
mkdir -p "$foreign_root"
busy_port="$(free_port)"
(cd "$foreign_root" && exec python3 -m http.server "$busy_port" --bind 127.0.0.1) >"$tmp/foreign.log" 2>&1 &
foreign_pid=$!
managed_pids+=("$foreign_pid")
wait_for_listener "$busy_port" "$foreign_pid"

if assert_port_available "$busy_port" >"$tmp/occupied.out" 2>&1; then
  fail "occupied port was accepted"
fi
grep -F "PID: $foreign_pid" "$tmp/occupied.out" >/dev/null || fail "occupied-port output omitted PID"
grep -F "$foreign_root" "$tmp/occupied.out" >/dev/null || fail "occupied-port output omitted CWD"
pass "occupied port reports PID and CWD"

printf '%s\n' "$foreign_pid" >"$tmp/foreign.pid"
if stop_managed_process "$tmp/foreign.pid" "$project_root" >"$tmp/refuse.out" 2>&1; then
  fail "foreign process was accepted as managed"
fi
kill -0 "$foreign_pid" 2>/dev/null || fail "foreign process was terminated"
pass "foreign PID file cannot terminate another workspace"

managed_port="$(free_port)"
(cd "$project_root" && exec python3 -m http.server "$managed_port" --bind 127.0.0.1) >"$tmp/managed.log" 2>&1 &
managed_pid=$!
managed_pids+=("$managed_pid")
wait_for_listener "$managed_port" "$managed_pid"
write_managed_pid "$tmp/managed.pid" "$managed_pid"
stop_managed_process "$tmp/managed.pid" "$project_root" || fail "managed process was not stopped"
wait "$managed_pid" 2>/dev/null || true
if kill -0 "$managed_pid" 2>/dev/null; then
  fail "managed process is still alive"
fi
[[ ! -e "$tmp/managed.pid" ]] || fail "managed PID file was not removed"
pass "validated managed process stops safely"

stale_pid=999999
printf '%s\n' "$stale_pid" >"$tmp/stale.pid"
stop_managed_process "$tmp/stale.pid" "$project_root" || fail "stale PID file was rejected"
[[ ! -e "$tmp/stale.pid" ]] || fail "stale PID file was not removed"
pass "stale PID file is removed"

unrelated_port="$(free_port)"
(cd "$foreign_root" && exec python3 -m http.server "$unrelated_port" --bind 127.0.0.1) >"$tmp/unrelated.log" 2>&1 &
unrelated_pid=$!
managed_pids+=("$unrelated_pid")
wait_for_listener "$unrelated_port" "$unrelated_pid"
(exit 0) &
expected_pid=$!
wait "$expected_pid"
if wait_for_managed_http "$expected_pid" "http://127.0.0.1:$unrelated_port/" "$tmp/expected.log" 1 >"$tmp/readiness.out" 2>&1; then
  fail "readiness accepted an unrelated service after the expected child exited"
fi
pass "readiness requires the expected child to remain alive"

sleep 5 &
first_supervised_pid=$!
managed_pids+=("$first_supervised_pid")
sleep 5 &
second_supervised_pid=$!
managed_pids+=("$second_supervised_pid")
monitor_managed_processes \
  "$first_supervised_pid" "$tmp/first-supervised.log" \
  "$second_supervised_pid" "$tmp/second-supervised.log" \
  >"$tmp/monitor.out" 2>&1 &
monitor_pid=$!
managed_pids+=("$monitor_pid")
sleep 0.2
kill -0 "$monitor_pid" 2>/dev/null || fail "managed-process monitor returned while children were alive"
kill "$second_supervised_pid"
wait "$second_supervised_pid" 2>/dev/null || true
if wait "$monitor_pid"; then
  fail "managed-process monitor accepted an exited child"
fi
pass "managed-process monitor keeps the launcher alive"

assert_file_contains() {
  local expected="$1" file="$2"
  grep -F "$expected" "$file" >/dev/null || fail "$file is missing: $expected"
}

assert_file_contains 'assert_port_available 8001' "$project_root/scripts/start-backends-macos.sh"
assert_file_contains 'assert_port_available 8080' "$project_root/scripts/start-backends-macos.sh"
assert_file_contains 'wait_for_managed_http "$python_pid"' "$project_root/scripts/start-backends-macos.sh"
assert_file_contains 'assert_port_available 5173' "$project_root/scripts/start-frontends-macos.sh"
assert_file_contains 'assert_port_available 5174' "$project_root/scripts/start-frontends-macos.sh"
assert_file_contains 'WorkflowStepper.vue' "$project_root/scripts/start-frontends-macos.sh"
assert_file_contains 'buyilehu-logo-sidebar.png' "$project_root/scripts/start-frontends-macos.sh"
assert_file_contains 'student-music-classroom-hero.png' "$project_root/scripts/start-frontends-macos.sh"
assert_file_contains 'stop_managed_process' "$project_root/scripts/stop-all-macos.sh"
grep -Fx '.runtime/' "$project_root/.gitignore" >/dev/null || fail '.gitignore does not ignore .runtime/'
pass "launchers use the runtime process guard"

printf 'All runtime process tests passed.\n'
