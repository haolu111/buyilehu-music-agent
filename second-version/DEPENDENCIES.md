# 第二版真实智能体依赖

## Java 后端

- 项目：`backend/music-agent-server/pom.xml`
- 启动：`scripts/start-backends-macos.sh`
- 端口：`8080`

## Python 能力库

- 清单：`backend/python-capability-library/requirements.txt`
- 测试：`backend/python-capability-library/tests/`
- 端口：`8001`

## 教师端和学生端

- 教师端清单：`frontend/teacher-web/package.json` 与 `package-lock.json`
- 学生端清单：`frontend/student-web/package.json` 与 `package-lock.json`
- 启动：`scripts/start-frontends-macos.sh`
- 端口：教师 `5173`，学生 `5174`

不要把 `.venv/`、`node_modules/`、数据库密码、`.runtime/` 或上传文件提交到 GitHub。依赖目录应由这些清单在第二版目录内重新安装。
