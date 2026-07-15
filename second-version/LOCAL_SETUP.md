# macOS 本地运行

本目录是工程师维护的完整整合项目，独立于父目录的“第一版”应用；不要用其中的文件覆盖父目录的 `app/` 或 `frontend/`。

## 依赖

- JDK 8 或更高版本，以及 Maven
- MySQL（可连接的本地实例）
- Python 3.11 或更高版本；脚本默认使用 Homebrew 的 `/opt/homebrew/bin/python3.12`，也可设置 `PYTHON_BIN` 为其他 Python 3.11+ 可执行文件
- Node.js 与 npm

先运行预检：

```bash
./scripts/preflight-macos.sh
```

预检只检查环境，不安装软件、不创建数据库，也不会读取或保存数据库密码。

## 数据库

启动脚本会在首次运行时，将 MySQL 8.4 初始化到 `~/.buyilehu-music-agent/mysql84` 并监听 `127.0.0.1:3306`。该目录独立于任何 Homebrew 默认 MySQL 数据目录。创建本地开发数据库：

```bash
mysql -u root -p -e 'CREATE DATABASE IF NOT EXISTS buyilehu_music_agent_v2 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
mysql -u root -p buyilehu_music_agent_v2 < database/buyilehu_music_agent_20260711.sql
```

第二版本地配置使用独立数据库 `buyilehu_music_agent_v2`，并按当前 Java 实体自动对齐结构。首次使用请导入仓库中的 `database/buyilehu_music_agent_20260711.sql`；该 SQL 已与 `snapshot_json MEDIUMTEXT` 实体定义保持一致。

## 启动后端

将密码仅保留在当前终端环境中：

```bash
export DB_PASSWORD='你的本地数据库密码'
export DB_USERNAME=root
export DB_NAME=buyilehu_music_agent_v2
./scripts/start-backends-macos.sh
```

Homebrew 新初始化的仅本机 MySQL 默认 root 密码为空时，使用 `export DB_PASSWORD=''`；生产或共享环境必须先设置强密码。

脚本依次启动 Python 能力服务（`http://127.0.0.1:8001/api/v1/health`）和 Java 服务（`http://127.0.0.1:8080/actuator/health`）。Java 服务退出时，脚本会停止它启动的 Python 服务。

启动前会检查 `8001` 和 `8080`。如果端口已被占用，脚本会打印占用者 PID、命令和工作目录并退出，避免把第一版或其他 worktree 的健康响应误判为第二版启动成功。

## 启动前端

另开一个终端执行：

```bash
./scripts/start-frontends-macos.sh
```

- 教师端：`http://127.0.0.1:5173/`
- 学生端：`http://127.0.0.1:5174/`

前端将 `/api` 代理到 Java 服务的 `http://127.0.0.1:8080`。日志保存到本项目的 `.runtime/`（已忽略）。

前端启动脚本会留在前台监督两个 Vite 进程。保持该终端打开；任一前端异常退出时脚本会显示对应日志并停止另一端，按 `Ctrl-C` 可正常停止两端。

## 停止与端口冲突

停止由第二版脚本记录的 Python、教师端和学生端进程：

```bash
./scripts/stop-all-macos.sh
```

Java 后端在运行 `start-backends-macos.sh` 的终端中按 `Ctrl-C` 停止。停止脚本会校验 PID 对应进程的工作目录必须属于当前第二版，校验失败时拒绝终止，避免误伤其他项目。

如果启动时报端口冲突，请根据输出中的 `CWD` 找到旧副本，在它原来的终端停止；确认以下端口空闲后再启动第二版：

- 教师端 `5173`
- 学生端 `5174`
- Python 能力库 `8001`
- Java 主后端 `8080`
