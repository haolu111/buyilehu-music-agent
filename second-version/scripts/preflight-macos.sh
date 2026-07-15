#!/usr/bin/env bash
set -euo pipefail

mode="${1:-all}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tools_root="$root/.tools"
if [[ -x "$tools_root/java/bin/java" ]]; then
  export JAVA_HOME="${JAVA_HOME:-$tools_root/java}"
  export PATH="$JAVA_HOME/bin:$PATH"
fi
if [[ -x "$tools_root/maven/bin/mvn" ]]; then
  export PATH="$tools_root/maven/bin:$PATH"
fi
if [[ -d /opt/homebrew/opt/mysql@8.4/bin ]]; then
  export PATH="/opt/homebrew/opt/mysql@8.4/bin:$PATH"
elif [[ -d /opt/homebrew/opt/mysql/bin ]]; then
  export PATH="/opt/homebrew/opt/mysql/bin:$PATH"
fi
python_bin="${PYTHON_BIN:-/opt/homebrew/bin/python3.12}"
missing=0

require_command() {
  local command_name="$1"
  local label="$2"
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'ok: %s\n' "$label"
  else
    printf 'missing: %s\n' "$label" >&2
    missing=1
  fi
}

if [[ "$mode" != "--frontend" ]]; then
  if command -v java >/dev/null 2>&1 && java -version >/dev/null 2>&1; then
    printf 'ok: Java runtime\n'
  else
    printf 'missing: Java runtime (JDK 8 or newer)\n' >&2
    missing=1
  fi
  require_command mvn "Maven"
  require_command mysql "MySQL client"
  if command -v "$python_bin" >/dev/null 2>&1 && "$python_bin" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
    printf 'ok: Python 3.11+ (%s)\n' "$python_bin"
  else
    printf 'missing: Python 3.11+ (set PYTHON_BIN to its executable)\n' >&2
    missing=1
  fi
fi

require_command node "Node.js"
require_command npm "npm"

if [[ "$missing" -ne 0 ]]; then
  printf 'Preflight failed. Install the listed prerequisites, then rerun this script.\n' >&2
  exit 1
fi

printf 'Preflight passed.\n'
