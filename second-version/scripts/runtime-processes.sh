#!/usr/bin/env bash

runtime_process_pid_for_port() {
  lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -n 1 || true
}

runtime_process_cwd() {
  lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' || true
}

assert_port_available() {
  local port="$1" pid cwd command
  pid="$(runtime_process_pid_for_port "$port")"
  if [[ -z "$pid" ]]; then
    return 0
  fi

  cwd="$(runtime_process_cwd "$pid")"
  command="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  printf 'Port %s is already in use.\nPID: %s\nCWD: %s\nCommand: %s\n' \
    "$port" "$pid" "${cwd:-unknown}" "${command:-unknown}" >&2
  return 1
}

write_managed_pid() {
  local pid_file="$1" pid="$2"
  mkdir -p "$(dirname "$pid_file")"
  printf '%s\n' "$pid" >"$pid_file"
}

wait_for_managed_http() {
  local pid="$1" url="$2" log_file="$3" attempts="${4:-30}" attempt
  for attempt in $(seq 1 "$attempts"); do
    if ! kill -0 "$pid" 2>/dev/null; then
      printf 'Managed process %s exited before %s became ready.\n' "$pid" "$url" >&2
      tail -n 80 "$log_file" >&2 || true
      return 1
    fi
    if curl --fail --silent --max-time 1 "$url" >/dev/null; then
      return 0
    fi
    sleep 1
  done

  printf 'Timed out waiting for %s.\n' "$url" >&2
  tail -n 80 "$log_file" >&2 || true
  return 1
}

wait_for_managed_process() {
  local pid="$1" log_file="$2" seconds="${3:-2}" attempt
  for attempt in $(seq 1 "$seconds"); do
    if ! kill -0 "$pid" 2>/dev/null; then
      printf 'Managed process %s exited during startup.\n' "$pid" >&2
      tail -n 80 "$log_file" >&2 || true
      return 1
    fi
    sleep 1
  done
}

monitor_managed_processes() {
  local entries=("$@") index pid log_file
  if (( ${#entries[@]} == 0 || ${#entries[@]} % 2 != 0 )); then
    printf 'monitor_managed_processes requires PID/log pairs.\n' >&2
    return 2
  fi

  while true; do
    index=0
    while (( index < ${#entries[@]} )); do
      pid="${entries[$index]}"
      log_file="${entries[$((index + 1))]}"
      if ! kill -0 "$pid" 2>/dev/null; then
        printf 'Managed process %s exited.\n' "$pid" >&2
        tail -n 80 "$log_file" >&2 || true
        return 1
      fi
      index=$((index + 2))
    done
    sleep 1
  done
}

stop_managed_process() {
  local pid_file="$1" project_root="$2" pid cwd attempt
  if [[ ! -f "$pid_file" ]]; then
    return 0
  fi

  pid="$(sed -n '1p' "$pid_file")"
  if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
    printf 'Invalid PID file: %s\n' "$pid_file" >&2
    return 1
  fi

  if ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$pid_file"
    return 0
  fi

  cwd="$(runtime_process_cwd "$pid")"
  case "$cwd" in
    "$project_root"|"$project_root"/*) ;;
    *)
      printf 'Refusing to stop PID %s outside %s (CWD: %s).\n' \
        "$pid" "$project_root" "${cwd:-unknown}" >&2
      return 1
      ;;
  esac

  kill "$pid"
  for attempt in $(seq 1 50); do
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid" 2>/dev/null || true
      rm -f "$pid_file"
      return 0
    fi
    sleep 0.1
  done

  printf 'PID %s did not stop after SIGTERM.\n' "$pid" >&2
  return 1
}
