# 第二版课堂智能体结构

这是教师端和学生端课堂智能体的独立工作区，来源为
`haolu111/buyilehu-music-agent` 的 `6f3f784` 提交。它与第一版及组件能力库审核台完全分开。

## 目录分类

| 目录 | 内容 |
|---|---|
| `backend/music-agent-server/` | Java Spring Boot 主业务后端，提供登录、课程包、课堂会话和报告接口，端口 `8080` |
| `backend/python-capability-library/` | FastAPI Python 能力库与后端能力测试，端口 `8001` |
| `frontend/teacher-web/` | 教师端课堂管理、教案、课程包和课堂控制界面，端口 `5173` |
| `frontend/student-web/` | 学生端入班、课堂活动和提交界面，端口 `5174` |
| `database/` | 本地开发数据库示例 SQL |
| `scripts/` | 依赖预检、MySQL 8.4、本地后端和前端启动脚本 |
| `start-all-macos.command` | macOS 一键启动入口 |
| `pom.xml`、`requirements.txt`、`frontend/*/package-lock.json` | Java、Python 和两个前端的依赖清单 |

## 正确入口

- 教师端：`http://127.0.0.1:5173/login`
- 学生端：`http://127.0.0.1:5174/login`
- Java 健康检查：`http://127.0.0.1:8080/actuator/health`
- Python 健康检查：`http://127.0.0.1:8001/api/v1/health`

`template-console/music-education-review.html` 不属于这套教师/学生课堂智能体，它是组件能力库审核台，已单独归档到 `/Users/shishangbo/codex/组件能力库审核台`。

## 当前唯一前端版本

2026-07-15 的教师工作流改版和学生端视觉改版已经完整迁入本目录的 `frontend/teacher-web` 与 `frontend/student-web`。标准入口只使用本目录源码：教师端 `5173`，学生端 `5174`。

`scripts/start-frontends-macos.sh` 会检查新版的 `WorkflowStepper.vue`、教师端品牌 Logo 和学生端课堂主视觉；这些标志文件缺失时拒绝启动，防止旧前端再次覆盖后仍被误开。

## 隔离规则

- 不复制第一版的 `.venv`、`node_modules`、Maven `target` 运行缓存、`.runtime`、上传文件或数据库密码。
- API Key 只能放在本机环境变量或部署平台 Secret，不写入源码。
- 依赖从第二版内的清单安装，不能引用第一版的虚拟环境。
