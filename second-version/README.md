# Buyilehu Music Agent 第二版

这是教师端和学生端课堂智能体的完整工程，和第一版、组件能力库审核台分开。

## 真实智能体入口

- 教师端：`http://127.0.0.1:5173/login`
- 学生端：`http://127.0.0.1:5174/login`
- Java 主后端：`http://127.0.0.1:8080/actuator/health`
- Python 能力库：`http://127.0.0.1:8001/api/v1/health`

`backend/python-capability-library/frontend-demo/music-education-review.html` 只是组件能力库审核演示，不是教师端或学生端主智能体界面。

## macOS 启动

先安装 JDK 8+、Maven、MySQL 8.4、Python 3.11+、Node.js 和 npm，然后执行：

```bash
./scripts/preflight-macos.sh
mysql -u root -p -e 'CREATE DATABASE IF NOT EXISTS buyilehu_music_agent_v2 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
mysql -u root -p buyilehu_music_agent_v2 < database/buyilehu_music_agent_20260711.sql
export DB_USERNAME=root
export DB_PASSWORD='你的本地数据库密码'
export DB_NAME=buyilehu_music_agent_v2
./start-all-macos.command
```

也可以分别执行 `./scripts/start-backends-macos.sh` 和 `./scripts/start-frontends-macos.sh`。详细说明见 [LOCAL_SETUP.md](LOCAL_SETUP.md)。

如果提示 `Port ... is already in use`，脚本会同时显示占用进程的 PID、命令和工作目录。不要忽略后继续使用旧页面；先关闭提示中的其他项目进程，再重新启动第二版。第二版脚本自己启动的 Python 和两个前端可用以下命令安全停止：

```bash
./scripts/stop-all-macos.sh
```

Java 后端保持在启动它的前台终端中运行，使用 `Ctrl-C` 停止。脚本不会用宽泛的 `pkill` 终止其他仓库副本。

单独运行 `start-frontends-macos.sh` 时，该终端会持续监督教师端和学生端；保持终端打开，按 `Ctrl-C` 可同时停止两个前端。

## Windows 启动

在项目根目录先在当前 PowerShell 设置数据库凭据，再运行 `start-backends.bat` 和 `start-frontends.bat`。后端默认使用 `buyilehu_music_agent_v2`，首次使用请按上面的 SQL 导入步骤创建数据库。

```powershell
$env:DB_USERNAME = 'root'
$env:DB_PASSWORD = '你的本地数据库密码'
$env:DB_NAME = 'buyilehu_music_agent_v2'
.\start-backends.bat
```

## 依赖与数据隔离

- Python 依赖来自 `backend/python-capability-library/requirements.txt`。
- 两个前端依赖来自各自的 `package-lock.json`。
- 不提交 `.venv`、`node_modules`、`target`、`.runtime`、上传文件、数据库密码或 API Key。
- API Key 只能配置在本机环境变量或部署平台 Secret 中。
