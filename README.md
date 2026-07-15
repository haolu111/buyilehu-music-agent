## Docker Quick Start

The recommended local setup starts MySQL, Redis, RabbitMQ, the Python capability service,
and the Java server as one stack.

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Service endpoints:

```text
Java API:           http://127.0.0.1:8080
Java health:        http://127.0.0.1:8080/actuator/health
Python capability:  http://127.0.0.1:8001/api/v1/health
RabbitMQ console:   http://127.0.0.1:15672
```

Stop the stack without deleting data:

```powershell
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete all container data.

## Local Development Startup
>>>>>>> 9f27bf0 (保存我的本地修改)

仓库包含运行所需的图片、游戏资源、音色库和本地音频素材。不会包含任何模型 API Key、用户上传内容、登录数据库或本机缓存。

## 本地启动

后端：

<<<<<<< HEAD
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm ci
npm run dev -- --port 5176
```

打开：`http://127.0.0.1:5176/template-console/music-education-review.html`

```powershell
java -version
mvn -version
node -v
npm -v
mysql --version
redis-cli --version
rabbitmqctl version
```

The backend is a Spring Boot 2.7 app and expects JDK 8+, Maven, RabbitMQ, and Redis. The frontend apps use Node/npm.

### 1. Use Your Local MySQL

For manual startup, the backend connects directly to your local MySQL instance and expects the `buyilehu_music_agent` database.

If the database does not exist yet:

```powershell
mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS buyilehu_music_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

The local profile runs Flyway automatically. On an empty database, the backend creates the schema from:

生产预览可运行：

```bash
docker compose up --build
```

<<<<<<< HEAD

然后打开：`http://127.0.0.1:8000/template-console/music-education-review.html`

Local demo users and component definitions are loaded from `db/local`. Existing databases
without Flyway history are baselined at version 1 and then receive later migrations. Back up
an existing database before its first migration because version 2 converts legacy MyISAM tables
to InnoDB and adds uniqueness constraints and query indexes.

If you previously imported `database/buyilehu_music_agent_schema.sql`, recreate the local database before starting the backend. That file is an older schema and does not match the current Java entities.

安全边界

- 后端只提供审核目录、确定性审核预览、静态资源和健康检查。
- 不暴露文件上传、账户、生成任务、模型调用或任意命令执行接口。
- 审核结果里的“智能体可调用”是正式注册表的受限能力标记，不会从页面执行模型或系统命令。
### 2. Start RabbitMQ and Redis

The generation API publishes jobs to RabbitMQ and stores live progress in Redis. Start both services before the Java backend. The default connections are:

```text
RabbitMQ: localhost:5672, guest / guest
Redis: localhost:6379, database 0
```

Use `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USERNAME`, `RABBITMQ_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, and `REDIS_DATABASE` to override them. For a broker-free test or emergency fallback, set `ASYNC_GENERATION_ENABLED=false`; generation then runs synchronously in-process.

### 3. Prepare Python Capability Service

Python 3.11 or newer is required. Create its isolated environment once:

```powershell
cd backend\python-capability-library
py -3.11 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 4. Start Both Backends

From the project root, start Python first, wait for its health check, and then start Java:

```powershell
.\start-backends.bat
```

Python capability health check:

```text
http://127.0.0.1:8001/api/v1/health
```

Java health reports both services:

```text
http://127.0.0.1:8080/api/v1/system/health
```

To start Java manually:

```powershell
cd backend\music-agent-server
$env:DB_NAME='buyilehu_music_agent'
$env:DB_USERNAME='root'
$env:DB_PASSWORD='123456'
mvn spring-boot:run
```

Backend health check:

```text
http://127.0.0.1:8080/actuator/health
```

### 5. Start Teacher Web

```powershell
cd frontend\teacher-web
npm install
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Teacher web:

```text
http://127.0.0.1:5173/
```

### 6. Start Student Web

```powershell
cd frontend\student-web
npm install
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

Student web:

```text
http://127.0.0.1:5174/
```

### 7. Async Generation API

The teacher web uses this flow automatically:

```text
POST /api/v1/generation-jobs
GET  /api/v1/generation-jobs/{jobId}
GET  /api/v1/generation-jobs/{jobId}/events
```

The SSE endpoint emits named `status` events. States are `queued`, `running`, `success`, and `failed`; successful terminal events contain `packageId` and `versionId`. Redis snapshots expire after 24 hours, while final task and package records remain in MySQL.

Generation creation accepts an optional `Idempotency-Key` header. Reusing a key with the same
request returns the existing job; reusing it with a different request returns HTTP 409.

Generation jobs and their `generation_job.created` outbox events are committed in one MySQL
transaction. A scheduled publisher claims pending outbox rows, waits for RabbitMQ publisher
confirms, and retries failed deliveries with backoff. The consumer remains idempotent by locking
the generation job row before execution.

Package node edits require the current package version in the `X-Package-Version` header. A stale
version returns HTTP 409 instead of overwriting a newer edit. Redis also serializes package edits
across Java instances; the lock is released only after the database transaction finishes.

### 8. Tests

Java integration tests use Testcontainers and require a running Docker engine. They start isolated
MySQL and Redis containers automatically.

```powershell
cd backend\music-agent-server
mvn test

cd ..\python-capability-library
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

cd frontend-demo
npm test
npm run build
```

Both Vue applications are validated with `npm run build`. GitHub Actions runs these checks on every
pull request and builds the Java and Python container images after all test jobs succeed.

### 9. Default Accounts

```text
Teacher: teacher001 / 123456
Student: student001 / 123456
```

### 10. Notes

- Teacher web runs on port `5173`.
- Student web runs on port `5174`.
- Backend runs on port `8080`.
- Python capability service runs on port `8001`.
- RabbitMQ carries generation job IDs; the durable queue and dead-letter queue are declared automatically.
- Redis stores generation progress and publishes cross-instance status events consumed by SSE connections.
- Redis caches low-churn component definitions for six hours and coordinates package-edit distributed locks.
- MySQL slow-query logging is enabled in Compose; analysis commands and core `EXPLAIN` queries are documented in `docs/database-performance.md`.
- `PYTHON_CAPABILITY_CALL_MODE=primary` uses Python-generated activity runtime; `shadow` records it for inspection; `disabled` uses Java fallback runtime.
- Both frontend apps proxy `/api` requests to `http://localhost:8080`.
- The backend local profile points to your local MySQL database and uses Flyway migrations to keep the schema aligned with the Java entities.
