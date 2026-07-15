# 音乐教育组件总审核台

## 第二版课堂智能体

教师端、学生端及其 Java/Python 服务端工程位于 [`second-version/`](second-version/)，与本目录的组件审核台相互独立。克隆本仓库后，请进入该目录并按其中的 [README](second-version/README.md) 与 [本地启动说明](second-version/LOCAL_SETUP.md) 安装依赖、初始化数据库和启动服务：

```bash
git clone git@github.com:haolu111/buyilehu-music-agent.git
cd buyilehu-music-agent/second-version
```

第二版的教师端与学生端均提交了 `package-lock.json`，请使用 `npm ci` 安装可复现依赖；不会包含 `node_modules`、本机数据库、上传文件或密钥。

这是截图所示的“音乐教育组件总审核台”。它集中审核正式注册的基础与专业组件、课堂活动、完整游戏模板、虚拟教具、虚拟乐器和音乐材料绑定器，并保留审核预览、真实音色试听和全屏预览入口。

仓库包含运行所需的图片、游戏资源、音色库和本地音频素材。不会包含任何模型 API Key、用户上传内容、登录数据库或本机缓存。

## 本地启动

后端：

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

生产预览可运行：

```bash
docker compose up --build
```

然后打开：`http://127.0.0.1:8000/template-console/music-education-review.html`

## 安全边界

- 后端只提供审核目录、确定性审核预览、静态资源和健康检查。
- 不暴露文件上传、账户、生成任务、模型调用或任意命令执行接口。
- 审核结果里的“智能体可调用”是正式注册表的受限能力标记，不会从页面执行模型或系统命令。
