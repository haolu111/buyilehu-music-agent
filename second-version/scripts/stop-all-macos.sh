#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runtime_root="$root/.runtime"
source "$root/scripts/runtime-processes.sh"

failed=0
for name in teacher student python-capability; do
  pid_file="$runtime_root/$name.pid"
  if stop_managed_process "$pid_file" "$root"; then
    printf 'Stopped managed service: %s\n' "$name"
  else
    failed=1
  fi
done

java_pid="$(runtime_process_pid_for_port 8080)"
if [[ -n "$java_pid" ]]; then
  java_cwd="$(runtime_process_cwd "$java_pid")"
  case "$java_cwd" in
    "$root"|"$root"/*)
      printf 'Java is still running in its foreground terminal (PID %s). Stop it there with Ctrl-C.\n' "$java_pid"
      ;;
    *)
      printf 'Port 8080 belongs to another workspace (PID %s, CWD: %s); it was not stopped.\n' \
        "$java_pid" "${java_cwd:-unknown}" >&2
      ;;
  esac
fi

exit "$failed"
