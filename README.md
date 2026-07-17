# 不亦乐乎音乐教学智能体

面向小学音乐课堂的教案分析、互动包生成、课堂控制与学习反馈系统。

教师上传教案后，系统提取教学目标、年级、教学过程和音乐要素，由编排 Agent 从正式注册表中选择活动、音乐游戏和虚拟乐器任务，生成可编辑、可预览、可发布的课堂互动包。学生通过学生端加入课堂并完成互动，教师可以控制课堂进度并查看报告。

## 当前功能

- 教师登录、班级和学生管理
- 教案上传、解析和历史记录
- Agent 生成课堂互动包
- 互动包发布前完整预览与测试
- 编辑节点参数时实时预览学生端效果
- 教师确认、版本化编辑和发布互动包
- 教师端课堂控制、暂停和解锁环节
- 学生加入班级、进入课堂和提交活动结果
- 节拍、音高和顺序等客观证据评估
- 教师查看课堂完成情况和学习报告

## 互动包模型

互动包支持三类正式节点：

| 节点类型 | 用途 | 示例 |
| --- | --- | --- |
| `activity` | 已实现的教学活动 | 乐句学唱、歌词节奏、曲式排序 |
| `game` | 带规则、反馈和通关机制的音乐游戏 | 节奏回声、音高阶梯、音色侦探 |
| `instrument_task` | 带教学目标和证据规则的虚拟乐器任务 | 框鼓稳定拍、钢琴旋律序列 |

33 个实例活动归入 9 个 family，并使用 variant 区分同一家族中的具体教学形式。运行时契约为 `interactive-node-runtime.v2`，同时保留旧 renderer 兼容能力。

虚拟乐器任务不会让 AI 主观猜测学生表现：

- 节拍、音高、顺序和事件时间由规则生成客观证据。
- 音乐表现力、演奏技术、合奏平衡和创编理由由教师判断。
- AI 可用于辅助反馈，但不是所有任务的最终评分者。

## 系统结构

```text
教师端 / 学生端
       │
       ▼
Java Spring Boot API
       ├── MySQL：业务数据与互动包版本
       ├── Redis：运行状态
       ├── RabbitMQ：消息基础设施
       └── Python Capability
              ├── 教学编排 Agent
              ├── 活动与游戏注册表
              ├── 互动节点运行时生成
              └── 客观证据评估
```

主要目录：

```text
backend/
  music-agent-server/          Java Spring Boot 后端
  python-capability-library/   Python 编排与运行时服务
frontend/
  teacher-web/                 教师端 Vue 应用
  student-web/                 学生端 Vue 应用
  review-console/              组件与模板审核工作台
contracts/                     音乐活动、游戏和乐器契约
compose.yaml                   正式业务系统 Docker Compose
docker-compose.yml             Review Console 的独立旧入口
```

> 日常部署正式系统只使用 `compose.yaml`。不要省略 `-f compose.yaml`，否则 Docker 可能在多个 Compose 文件之间选择错误配置。

## Docker 部署

### 1. 环境要求

- Windows 10/11
- Docker Desktop 已启动
- Docker 使用 Linux 容器
- 建议至少 8 GB 可用内存

检查 Docker：

```powershell
docker version
docker compose version
```

### 2. 配置环境变量

在项目根目录创建或修改 `.env`：

```dotenv
DB_NAME=buyilehu_music_agent
DB_PASSWORD=123456

MYSQL_PORT=3307
MYSQL_LONG_QUERY_TIME=0.5
REDIS_PORT=6380
RABBITMQ_PORT=5673
RABBITMQ_MANAGEMENT_PORT=15672

PYTHON_CAPABILITY_PORT=8001
JAVA_SERVER_PORT=8080
TEACHER_WEB_PORT=5173
STUDENT_WEB_PORT=5174

PYTHON_CAPABILITY_CALL_MODE=primary

# 可选：不配置模型时，互动包生成使用规则兜底
CHAT_ECNU_API_KEY=
CHAT_ECNU_MODEL=ecnu-max
DOUBAO_API_KEY=
DOUBAO_MODEL=
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

不要提交真实 API Key、生产数据库密码或用户上传文件。

### 3. 检查 Compose 配置

```powershell
cd D:\buyilehu-music-agent
docker compose -f compose.yaml config --services
```

正确结果应包含：

```text
mysql
redis
rabbitmq
python-capability
java-server
teacher-web
student-web
```

### 4. 首次构建并启动

```powershell
docker compose -f compose.yaml up -d --build
```

查看状态：

```powershell
docker compose -f compose.yaml ps
```

首次启动需要等待 MySQL、Python 和 Java 依次通过健康检查。最终 7 个服务都应显示 `Up`，配置了健康检查的服务应显示 `healthy`。

### 5. 访问地址

| 服务 | 地址 |
| --- | --- |
| 教师端 | http://127.0.0.1:5173 |
| 学生端 | http://127.0.0.1:5174 |
| Java API | http://127.0.0.1:8080 |
| Java 健康检查 | http://127.0.0.1:8080/actuator/health |
| Python 健康检查 | http://127.0.0.1:8001/api/v1/health |
| RabbitMQ 管理端 | http://127.0.0.1:15672 |
| MySQL | `127.0.0.1:3307` |
| Redis | `127.0.0.1:6380` |

RabbitMQ 默认账号为 `guest / guest`。

### 6. 验证部署

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/v1/health |
  ConvertTo-Json -Depth 10

Invoke-RestMethod http://127.0.0.1:8080/actuator/health |
  ConvertTo-Json -Depth 10

(Invoke-WebRequest http://127.0.0.1:5173/ -UseBasicParsing).StatusCode
(Invoke-WebRequest http://127.0.0.1:5174/ -UseBasicParsing).StatusCode
```

预期结果：

- Python 返回 `status: ok`
- Java 返回 `status: UP`
- 两个前端均返回 HTTP `200`

## 更新代码后的重新部署

只修改 Python：

```powershell
docker compose -f compose.yaml up -d --build python-capability
```

只修改 Java：

```powershell
docker compose -f compose.yaml up -d --build java-server
```

只修改教师端或学生端：

```powershell
docker compose -f compose.yaml up -d --build teacher-web
docker compose -f compose.yaml up -d --build student-web
```

更新多个相互依赖的服务：

```powershell
docker compose -f compose.yaml up -d --build python-capability java-server teacher-web student-web
```

浏览器仍显示旧页面时，按 `Ctrl + F5` 强制刷新。

## 日常运维

查看所有服务：

```powershell
docker compose -f compose.yaml ps
```

查看日志：

```powershell
docker compose -f compose.yaml logs --tail 200
docker compose -f compose.yaml logs -f java-server python-capability
```

重启单个服务：

```powershell
docker compose -f compose.yaml restart java-server
```

停止并保留数据库数据：

```powershell
docker compose -f compose.yaml down
```

删除容器和全部命名卷：

```powershell
docker compose -f compose.yaml down -v
```

> `down -v` 会删除 MySQL、Redis、RabbitMQ 和上传文件卷中的数据，只能在确认不需要现有数据时使用。

## 教师端使用流程

1. 登录教师端。
2. 创建班级并维护学生。
3. 上传教案并等待解析完成。
4. 选择生成偏好，创建互动包。
5. 在方案页点击“预览并测试互动包”，逐环节检查。
6. 确认方案后进入编辑页。
7. 修改标题、说明、难度或组件参数，并在实时预览区检查学生端效果。
8. 保存修改，生成新的互动包版本。
9. 发布到班级并创建课堂。
10. 在课堂控制页依次解锁互动节点。
11. 课堂结束后查看报告。

教师预览处于测试沙箱，不会写入学生成绩或课堂报告。旧互动包不会自动变成 v2；需要重新生成互动包才能完整使用三类节点能力。

## Agent 与规则系统的职责

Agent 不会直接执行 Vue 组件，也不会直接写数据库。

```text
教案解析
  → Agent 选择活动、游戏和虚拟乐器任务
  → 注册表校验 ID 与组合是否合法
  → Python 生成可执行 runtime
  → Java 保存、版本化并发布
  → 前端按 renderer 渲染
```

配置模型 API 后，系统优先使用模型进行教学编排；模型不可用或配置为空时，使用规则编排兜底。无论采用哪种方式，输出都必须经过正式注册表校验。

## 数据持久化

Docker 命名卷：

- `mysql-data`：业务数据库
- `redis-data`：Redis 数据
- `rabbitmq-data`：RabbitMQ 数据
- `lesson-storage`：教案与上传文件

普通的 `docker compose down` 不会删除这些数据。重新构建应用镜像也不会清空数据库。

## 常见问题

### 端口已被占用

检查占用：

```powershell
Get-NetTCPConnection -State Listen |
  Where-Object LocalPort -In 5173,5174,8001,8080,3307,6380,5673,15672
```

可以在 `.env` 中修改宿主机端口，容器内部端口不要修改。

### 容器一直 restarting

```powershell
docker compose -f compose.yaml ps
docker compose -f compose.yaml logs --tail 200 java-server
docker compose -f compose.yaml logs --tail 200 python-capability
```

重点检查数据库连接、表结构、环境变量和 Python 健康状态。

### Java 健康检查返回 503

查看详细状态和日志：

```powershell
Invoke-WebRequest http://127.0.0.1:8080/actuator/health -UseBasicParsing
docker compose -f compose.yaml logs --tail 200 java-server
```

Java 启动完成不代表所有依赖立即可用，应以 Compose 的 `healthy` 状态为准。

### Python 容器正常但宿主机无法访问

`docker compose ps` 的端口必须显示：

```text
0.0.0.0:8001->8001/tcp
```

如果只显示 `8001/tcp`，说明没有发布宿主机端口，应检查是否使用了正确的 `compose.yaml`。

### 修改代码后页面没有变化

代码不会自动进入已有镜像。重新构建对应服务：

```powershell
docker compose -f compose.yaml up -d --build teacher-web student-web
```

然后按 `Ctrl + F5`。

### 出现 multiple config files 警告

根目录同时存在 `compose.yaml` 和 `docker-compose.yml`。正式系统始终显式使用：

```powershell
docker compose -f compose.yaml ...
```

`docker-compose.yml` 目前仅用于独立 Review Console，不属于正式 7 服务栈。

### 出现 orphan container 警告

旧的 Review Console 可能作为孤立容器继续运行。它不会影响正式系统。确认不再需要后，可以单独停止：

```powershell
docker compose -f docker-compose.yml down
```

不要为了消除警告直接给正式业务命令添加 `--remove-orphans`，除非确定需要删除这些独立容器。

## 测试

Python：

```powershell
cd backend\python-capability-library
python -m pytest -q
```

教师端：

```powershell
cd frontend\teacher-web
npm ci
npm run test
npm run build
```

学生端：

```powershell
cd frontend\student-web
npm ci
npm run build
```

Java 可以直接通过 Docker 构建验证：

```powershell
cd D:\buyilehu-music-agent
docker compose -f compose.yaml build java-server
```

## 安全说明

- 不要将 `.env`、API Key、真实用户数据或上传文件提交到仓库。
- 示例密码仅适用于本地开发，不适用于生产环境。
- 生产部署应更换数据库和 RabbitMQ 密码，并限制数据库、Redis、RabbitMQ 管理端口的外部访问。
- 教师上传的音频、谱面和教案应确认版权与使用权限。
