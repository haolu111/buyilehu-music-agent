#!/usr/bin/env bash
set -euo pipefail

mysql_root="/opt/homebrew/opt/mysql@8.4"
data_root="$HOME/.buyilehu-music-agent/mysql84"
runtime_root="$HOME/.buyilehu-music-agent/runtime"
mysql_admin="$mysql_root/bin/mysqladmin"
mysql_server="$mysql_root/bin/mysqld"

if [[ ! -x "$mysql_server" ]]; then
  printf 'MySQL 8.4 is required. Install it with: brew install mysql@8.4\n' >&2
  exit 1
fi

if "$mysql_admin" --protocol=tcp -h 127.0.0.1 -P 3306 -u root ping --silent >/dev/null 2>&1; then
  printf 'MySQL is already listening on 127.0.0.1:3306.\n'
  exit 0
fi

mkdir -p "$data_root" "$runtime_root"
if [[ ! -d "$data_root/mysql" ]]; then
  "$mysql_server" --initialize-insecure --basedir="$mysql_root" --datadir="$data_root"
fi

"$mysql_server" \
  --basedir="$mysql_root" \
  --datadir="$data_root" \
  --socket="$runtime_root/mysql.sock" \
  --pid-file="$runtime_root/mysql84.pid" \
  --log-error="$runtime_root/mysql84.log" \
  --bind-address=127.0.0.1 \
  --port=3306 \
  --daemonize

for _ in $(seq 1 30); do
  if "$mysql_admin" --protocol=tcp -h 127.0.0.1 -P 3306 -u root ping --silent >/dev/null 2>&1; then
    printf 'MySQL 8.4 is ready on 127.0.0.1:3306.\n'
    exit 0
  fi
  sleep 1
done

printf 'MySQL 8.4 did not start; see %s/mysql84.log\n' "$runtime_root" >&2
exit 1
