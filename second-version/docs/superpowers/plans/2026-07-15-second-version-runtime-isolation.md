# Second Version Runtime Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent the second-version music agent from silently connecting to stale services from other repository copies, then switch the local machine to a verified all-second-version runtime.

**Architecture:** Put macOS process inspection and PID validation in one sourceable shell library. The backend and frontend launchers call the library before starting, persist only their own child PIDs under `.runtime`, and fail if a child exits before readiness. A dedicated stop script terminates only validated second-version PIDs; runtime verification then checks process working directories and the real generation API.

**Tech Stack:** zsh/bash-compatible shell, macOS `lsof`/`ps`, FastAPI/Uvicorn, Spring Boot/Maven, Vue/Vite, curl/jq, MySQL 8.4.

---

## File map

- Create `scripts/runtime-processes.sh`: reusable port inspection, child-process readiness, PID-file write, and safe stop functions.
- Create `scripts/tests/runtime-processes-test.sh`: dependency-free shell regression tests using temporary ports and processes.
- Create `scripts/stop-all-macos.sh`: stop only processes recorded by this second-version workspace.
- Modify `scripts/start-backends-macos.sh`: reject occupied ports, persist Python PID, verify the child remains alive, and clean PID state.
- Modify `scripts/start-frontends-macos.sh`: reject occupied ports, persist both Vite PIDs, and fail when either child exits immediately.
- Modify `start-all-macos.command`: start backends/frontends without hiding a failed child startup.
- Modify `.gitignore`: ignore `.runtime/`.
- Modify `README.md` and `LOCAL_SETUP.md`: document conflict diagnostics and the safe stop command.

### Task 1: Runtime process guard library

**Files:**
- Create: `scripts/runtime-processes.sh`
- Create: `scripts/tests/runtime-processes-test.sh`

- [ ] **Step 1: Write failing tests for port ownership and PID safety**

Create a shell test harness that sources `scripts/runtime-processes.sh` and verifies these concrete behaviors:

```bash
assert_port_available "$free_port"

(cd "$foreign_root" && python3 -m http.server "$busy_port" --bind 127.0.0.1) &
foreign_pid=$!
if assert_port_available "$busy_port" >"$tmp/output" 2>&1; then
  fail "occupied port was accepted"
fi
grep -F "PID: $foreign_pid" "$tmp/output"
grep -F "$foreign_root" "$tmp/output"

printf '%s\n' "$foreign_pid" >"$tmp/foreign.pid"
if stop_managed_process "$tmp/foreign.pid" "$project_root"; then
  fail "foreign process was terminated"
fi
kill -0 "$foreign_pid"
```

Also test that `wait_for_managed_http` fails when its expected child PID has exited even if an unrelated HTTP server already answers the URL.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
bash scripts/tests/runtime-processes-test.sh
```

Expected: FAIL because `scripts/runtime-processes.sh` does not exist.

- [ ] **Step 3: Implement the minimal process library**

Implement these interfaces:

```bash
runtime_process_pid_for_port() {
  lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -n 1
}

runtime_process_cwd() {
  lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p'
}

assert_port_available() {
  local port="$1" pid cwd command
  pid="$(runtime_process_pid_for_port "$port")"
  [[ -z "$pid" ]] && return 0
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
    curl --fail --silent --max-time 1 "$url" >/dev/null && return 0
    sleep 1
  done
  printf 'Timed out waiting for %s.\n' "$url" >&2
  tail -n 80 "$log_file" >&2 || true
  return 1
}

stop_managed_process() {
  local pid_file="$1" project_root="$2" pid cwd attempt
  [[ -f "$pid_file" ]] || return 0
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
    *) printf 'Refusing to stop PID %s outside %s (CWD: %s).\n' "$pid" "$project_root" "${cwd:-unknown}" >&2; return 1 ;;
  esac
  kill "$pid"
  for attempt in $(seq 1 50); do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.1
  done
  if kill -0 "$pid" 2>/dev/null; then
    printf 'PID %s did not stop after SIGTERM.\n' "$pid" >&2
    return 1
  fi
  rm -f "$pid_file"
}
```

`assert_port_available` must print the port, PID, command and CWD before returning nonzero. `wait_for_managed_http` must check `kill -0 "$pid"` before every curl attempt. `stop_managed_process` must compare the process CWD with the supplied project root before sending `TERM`, then remove the PID file only after the process exits or is already absent.

- [ ] **Step 4: Run the test and verify GREEN**

Run `bash scripts/tests/runtime-processes-test.sh`.

Expected: all named cases print `PASS` and the command exits 0.

- [ ] **Step 5: Commit the process library**

```bash
git add scripts/runtime-processes.sh scripts/tests/runtime-processes-test.sh
git commit -m "test: guard second version runtime processes"
```

### Task 2: Integrate safe startup and shutdown

**Files:**
- Create: `scripts/stop-all-macos.sh`
- Modify: `scripts/start-backends-macos.sh`
- Modify: `scripts/start-frontends-macos.sh`
- Modify: `start-all-macos.command`
- Modify: `.gitignore`

- [ ] **Step 1: Extend failing tests for launcher integration**

Add static assertions to `scripts/tests/runtime-processes-test.sh`:

```bash
grep -F 'assert_port_available 8001' scripts/start-backends-macos.sh
grep -F 'assert_port_available 8080' scripts/start-backends-macos.sh
grep -F 'wait_for_managed_http "$python_pid"' scripts/start-backends-macos.sh
grep -F 'assert_port_available 5173' scripts/start-frontends-macos.sh
grep -F 'assert_port_available 5174' scripts/start-frontends-macos.sh
grep -F 'stop_managed_process' scripts/stop-all-macos.sh
grep -Fx '.runtime/' .gitignore
```

- [ ] **Step 2: Run the test and verify RED**

Run `bash scripts/tests/runtime-processes-test.sh`.

Expected: FAIL on the first missing launcher integration assertion.

- [ ] **Step 3: Implement minimal launcher integration**

Backend launcher requirements:

```bash
source "$root/scripts/runtime-processes.sh"
assert_port_available 8001
assert_port_available 8080
write_managed_pid "$runtime_root/python-capability.pid" "$python_pid"
wait_for_managed_http "$python_pid" "http://127.0.0.1:8001/api/v1/health" "$runtime_root/python-capability.log" 30
```

Its cleanup trap must stop the recorded Python PID and remove the PID file. Frontend launcher must precheck both ports, write `teacher.pid` and `student.pid`, wait briefly for each child to remain alive, and on partial failure stop only children started by that invocation. `stop-all-macos.sh` must call `stop_managed_process` for the three PID files and explain that foreground Java is stopped with Ctrl-C unless its own validated PID file exists.

`start-all-macos.command` must start backends in one Terminal-managed process and start frontends only after backend health endpoints succeed, or fail with log paths; it must not background an unchecked launcher.

- [ ] **Step 4: Run tests and syntax checks**

```bash
bash scripts/tests/runtime-processes-test.sh
bash -n scripts/runtime-processes.sh scripts/start-backends-macos.sh scripts/start-frontends-macos.sh scripts/stop-all-macos.sh start-all-macos.command
```

Expected: both commands exit 0.

- [ ] **Step 5: Commit launcher changes**

```bash
git add .gitignore scripts/start-backends-macos.sh scripts/start-frontends-macos.sh scripts/stop-all-macos.sh start-all-macos.command scripts/tests/runtime-processes-test.sh
git commit -m "fix: isolate second version local services"
```

### Task 3: Documentation and end-to-end runtime repair

**Files:**
- Modify: `README.md`
- Modify: `LOCAL_SETUP.md`

- [ ] **Step 1: Document the exact conflict workflow**

Add the following user flow without changing existing URLs:

```text
./scripts/stop-all-macos.sh
./scripts/start-frontends-macos.sh
export DB_PASSWORD=''
./scripts/start-backends-macos.sh
```

Explain that an occupied-port error lists the foreign process and CWD and must be resolved instead of ignored.

- [ ] **Step 2: Stop the diagnosed stale processes**

Re-read `lsof` for ports `5173`, `5174`, `8001`, and `8080`. Terminate only the previously identified development processes whose CWD is outside `/Users/shishangbo/codex/第二版`. Recheck that all four ports are free.

- [ ] **Step 3: Start the second-version runtime**

Use the second-version Python virtual environment, the available bundled JDK/Maven paths, `DB_NAME=buyilehu_music_agent_v2`, empty local root password, and the normal ports. Capture logs under `/Users/shishangbo/codex/第二版/.runtime/`.

- [ ] **Step 4: Run full verification**

```bash
bash scripts/tests/runtime-processes-test.sh
backend/python-capability-library/.venv/bin/pytest backend/python-capability-library/tests -q
cd backend/music-agent-server && mvn test
cd frontend/teacher-web && npm run build
cd frontend/student-web && npm run build
```

Then verify every listener CWD with `lsof`, health endpoints with curl, login with `teacher001 / 123456`, list parsed lesson plans, and POST `/api/v1/generation-jobs`. Expected generation response: HTTP 200 with non-null `packageId`, non-null `versionId`, and `status: success`.

- [ ] **Step 5: Commit documentation and report evidence**

```bash
git add README.md LOCAL_SETUP.md
git commit -m "docs: explain isolated second version startup"
```

Report exact test counts, build exit codes, listener CWDs, health responses, and generated package identifiers.
