# Buyilehu Music Agent

## Local Development Startup

Run commands from the project root unless a step says to enter a subdirectory.

### 1. Use Your Local MySQL

The backend now connects directly to your local MySQL instance and expects the `buyilehu_music_agent` database. No Docker container is needed.

If the database does not exist yet:

```powershell
mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS buyilehu_music_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

If you need to rebuild the schema from scratch, import `database/buyilehu_music_agent_schema.sql` into that database.

### 2. Start Backend

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

### 3. Start Teacher Web

```powershell
cd frontend\teacher-web
npm install
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Teacher web:

```text
http://127.0.0.1:5173/
```

### 4. Start Student Web

```powershell
cd frontend\student-web
npm install
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

Student web:

```text
http://127.0.0.1:5174/
```

### 5. Default Accounts

```text
Teacher: teacher001 / 123456
Student: student001 / 123456
```

### 6. Notes

- Teacher web runs on port `5173`.
- Student web runs on port `5174`.
- Backend runs on port `8080`.
- Both frontend apps proxy `/api` requests to `http://localhost:8080`.
- The backend local profile points to your local MySQL database and skips Flyway, so an existing database like the one in your screenshot can be used directly.
