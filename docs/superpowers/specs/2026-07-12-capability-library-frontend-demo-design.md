# 后端能力组件库双页面前端演示设计

日期：2026-07-12

## 目标

在 `backend/python-capability-library/frontend-demo/` 增加一个独立、可运行的前端演示工程，让工程师能够查看并调试后端能力组件库对应的两个现成界面：

1. `music-education-review.html`：音乐教育能力审核页，展示节奏型、音高、音色等组件及试听、判断交互。
2. `virtual-instrument-review.html`：虚拟乐器顺序审核向导，展示乐器视觉、真实音色、触控区域、节拍器适配和课堂玩法审核流程。

## 范围

演示工程只包含上述两个页面及其运行所需的直接和传递依赖：

- 两个 HTML 入口。
- 对应的 React/Vue 入口模块。
- 页面使用的活动组件、音乐组件、共享音乐契约和虚拟乐器模块。
- 页面实际引用的样式与静态资源。
- 最小化的 Vite、TypeScript、包管理配置。
- 与两个页面直接相关的单元测试。
- 启动、构建、测试和页面地址说明。

明确排除：

- 其他课堂活动、教师端、学生端和游戏预览页面。
- 原工程的 `node_modules`、`dist`、Vite 缓存、浏览器配置和截图产物。
- `.env`、令牌、密钥、本机绝对路径、用户上传、数据库、日志和个人数据。
- 目标仓库已有的 `frontend/student-web` 和 `frontend/teacher-web`，本次不修改这两个工程。

## 目录结构

```text
backend/python-capability-library/frontend-demo/
├── README.md
├── index.html
├── music-education-review.html
├── virtual-instrument-review.html
├── package.json
├── package-lock.json
├── tsconfig.json
├── vite.config.ts
├── src/
│   ├── music-education-review-main.tsx
│   ├── virtual-instrument-review-main.ts
│   ├── activity/
│   ├── music-components/
│   ├── shared/
│   └── virtual-instruments/
└── tests/
    ├── music-education-review 相关测试
    └── virtual-instrument-review 相关测试
```

`index.html` 是轻量入口页，只提供两个演示页面的名称、用途和链接，不复制第三个产品界面。

## 架构与依赖

演示工程保持源工程现有 React/Vue 混合 Vite 结构，因为两个审核页面分别依赖已有组件实现。依赖通过静态导入闭包确定，不整包复制原 `frontend/`。

Vite 使用相对部署基路径 `./`，使构建结果既可由静态服务器托管，也可在子目录中预览。开发服务器不默认代理后端；页面需要音频或运行时资源时，优先使用随演示复制的公开静态资源或现有无凭据降级行为。不得写入真实服务地址或凭据。

## 数据流

页面从本地 TypeScript 契约、组件注册表和演示状态初始化。交互状态只保存在浏览器内存中，不上传、不持久化个人信息。音频试听和虚拟乐器资源从演示工程的本地公开资源读取；缺少真实资源时沿用页面现有的可见降级提示。

## 错误处理

- 缺少音频或乐器资源时，页面显示现有的不可用或待启用状态，不静默失败。
- 构建时若存在缺失模块、类型错误或未解析资源，构建必须失败并阻止推送。
- 两个页面任一无法通过本地 HTTP 服务加载，视为发布失败。

## 验证标准

推送前必须满足：

1. `npm ci` 成功。
2. 与两个页面相关的测试全部通过。
3. `npm run build` 成功，构建结果包含两个 HTML 入口。
4. 使用本地 HTTP 服务分别打开两个页面，页面无阻断性控制台错误。
5. 音乐教育审核页可见节奏卡片及审核操作；虚拟乐器页可切换乐器和审核步骤。
6. Git 提交清单不包含其他 HTML 页面、缓存、构建产物、密钥、个人数据或本机绝对路径。

## 交付结果

最终在目标仓库 `main` 分支增加独立双页面演示工程，并在能力库主 README 中加入启动命令和两个页面地址。现有前后端工程保持不变。
