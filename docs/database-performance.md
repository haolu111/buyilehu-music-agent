# Database Performance Guide

## Slow Query Log

The Compose MySQL service enables the slow query log with a default threshold of 500 ms.
Override `MYSQL_LONG_QUERY_TIME` in `.env` when a different local threshold is needed.

```powershell
docker compose exec mysql mysql -uroot -p123456 -e "SHOW VARIABLES LIKE 'slow_query%'; SHOW VARIABLES LIKE 'long_query_time';"
docker compose exec mysql sh -lc "mysqldumpslow -s t -t 20 /var/lib/mysql/mysql-slow.log"
```

The first command verifies the active settings. The second groups the 20 slowest normalized SQL
statements by total execution time. Do not commit production query parameters or user data copied
from a slow log.

MySQL Performance Schema provides an aggregate view without reading the log file directly:

```sql
SELECT DIGEST_TEXT,
       COUNT_STAR,
       ROUND(SUM_TIMER_WAIT / 1000000000000, 2) AS total_seconds,
       ROUND(AVG_TIMER_WAIT / 1000000000, 2) AS average_ms,
       SUM_ROWS_EXAMINED,
       SUM_ROWS_SENT
FROM performance_schema.events_statements_summary_by_digest
WHERE SCHEMA_NAME = DATABASE()
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 20;
```

## EXPLAIN Workflow

Run `docs/sql/core-query-explain.sql` against representative data. For each query, check that:

- `type` is `const`, `ref`, or `range` rather than `ALL` for growing tables.
- `key` matches the expected core index documented in the SQL file.
- `rows` is close to the expected result set instead of the full table size.
- `Extra` does not show avoidable `Using filesort` or `Using temporary` operations.

When a slow statement is found, capture its normalized SQL and `EXPLAIN FORMAT=JSON` output first.
Only add an index after checking existing indexes and the query's selectivity; every additional index
also increases insert and update cost.
