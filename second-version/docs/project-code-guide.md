# 项目代码结构说明

这份文档按“先看整体结构，再看功能链路，最后看关键函数”的顺序，帮助快速理解本项目代码。

## 1. 项目整体结构

项目分成三层：

1. `backend/music-agent-server`：Spring Boot 后端，负责登录、班级、教案、互动包、课堂会话、报表等业务。
2. `frontend/student-web`：学生端 Web，负责登录、加入班级、进入课堂、完成活动、查看课堂状态。
3. `frontend/teacher-web`：教师端 Web，负责登录、上传教案、查看历史教案、生成互动包、发布到班级、查看报表。

另外还有：

- `database`：数据库相关脚本和初始化资源。
- `deploy`：部署相关文件。
- `docs`：项目说明文档。
- `storage`：本地文件存储目录，教案文件等会落到这里。

## 2. 后端代码结构

后端主入口是 `backend/music-agent-server/src/main/java/com/buyilehu/musicagent/MusicAgentServerApplication.java`。

后端按照分层组织：

- `presentation/controller`：HTTP 接口层，只负责接收请求、返回响应。
- `application/service`：业务接口定义。
- `application/service/impl`：业务实现，真正写业务规则的地方。
- `application/dto`：请求和响应对象。
- `domain/entity`：数据库实体。
- `domain/model`：领域模型和生成过程中的中间对象。
- `infrastructure/repository`：JPA 数据访问层。
- `infrastructure/storage`：文件存储。
- `config`：Spring Security、JWT、文件存储配置。
- `common`：统一响应、异常、错误码、工具类。

### 2.1 后端关键功能分布

#### 登录与用户

- 接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/AuthController.java`
- 业务：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/application/service/impl/AuthServiceImpl.java`
- 数据：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/domain/entity/User.java`

作用：

- 校验用户名和密码。
- 生成 JWT token。
- 返回当前登录用户信息。
- `me()` 用于前端刷新登录态。

关键函数：

- `AuthServiceImpl.login(...)`：校验账号密码，生成 token。
- `AuthServiceImpl.me()`：根据当前 token 读取当前用户。
- `AuthServiceImpl.getCurrentUserId()`：从 Spring Security 上下文里取出当前用户 id。

#### 班级管理

- 接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/ClassController.java`
- 业务：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/application/service/impl/ClassServiceImpl.java`
- 数据：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/domain/entity/ClassEntity.java`、`ClassMember.java`

作用：

- 教师创建班级。
- 学生通过邀请码加入班级。
- 学生和教师都可以查看自己关联的班级。
- 教师可以查看班级学生名单。

关键函数：

- `ClassServiceImpl.create(...)`：教师创建班级并生成邀请码。
- `ClassServiceImpl.listMine()`：教师返回自己创建的班级，学生返回自己加入的班级。
- `ClassServiceImpl.join(...)`：学生按邀请码加入班级。
- `ClassServiceImpl.listStudents(...)`：教师查看自己班级的学生列表。

#### 教案上传与历史查看

- 接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/LessonPlanController.java`
- 业务：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/application/service/impl/LessonPlanServiceImpl.java`
- 数据：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/domain/entity/LessonPlan.java`

作用：

- 教师上传教案文件。
- 系统保存原始文件、解析文本和解析结果。
- 教师可查看历史上传的教案列表。
- 教师可按 id 查看某一份教案详情。

关键函数：

- `LessonPlanServiceImpl.upload(...)`：上传文件，保存到本地存储，解析内容并入库。
- `LessonPlanServiceImpl.listMine()`：返回当前教师的历史教案。
- `LessonPlanServiceImpl.getById(...)`：返回指定教案详情。

#### 互动包生成、修改、发布

- 生成入口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/GenerationJobController.java`
- 互动包接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/PackageController.java`
- 修改接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/PackageModifyController.java`
- 发布接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/ClassroomSessionController.java`
- 发布业务：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/application/service/impl/PackagePublicationServiceImpl.java`

作用：

- 根据教案生成互动包。
- 维护互动包版本。
- 支持对互动包节点内容做修改。
- 将互动包发布到班级，并指定版本和是否开启复核。

关键函数：

- `PackagePublicationServiceImpl.publish(...)`：检查包归属、版本和班级权限后创建发布记录。
- `PackageVersionServiceImpl`：管理互动包版本。
- `PackageModifyServiceImpl`：修改节点配置并保存修改记录。

#### 学生课堂流程

- 接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/StudentClassroomController.java`
- 业务：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/application/service/impl/StudentProgressServiceImpl.java`
- 数据：`ClassroomSession.java`、`SessionNodeState.java`、`StudentProgress.java`、`LearningEvent.java`

作用：

- 学生查询当前课堂。
- 学生进入某个课堂节点。
- 学生提交节点结果。
- 后端记录学习事件和进度。

关键函数：

- `StudentProgressServiceImpl.getCurrentClassroom()`：按当前学生已加入班级查找正在进行中的课堂。
- `StudentProgressServiceImpl.enterNode(...)`：学生进入节点，写入进度并记录事件。
- `StudentProgressServiceImpl.submitNode(...)`：学生提交活动结果并记录进度。
- `StudentProgressServiceImpl.validateUnlockedNode(...)`：检查学生是否属于班级、课堂是否运行、节点是否解锁。

#### 课堂报表

- 接口：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/presentation/controller/ReportController.java`
- 业务：`backend/music-agent-server/src/main/java/com/buyilehu/musicagent/application/service/impl/ReportServiceImpl.java`

作用：

- 汇总课堂内学生进入、完成、得分、时长等统计数据。
- 按节点和按学生生成报表。

关键函数：

- `ReportServiceImpl.getClassroomSessionReport(...)`：生成整场课堂报表。
- `ReportServiceImpl.buildNodeReports(...)`：按节点统计完成情况。
- `ReportServiceImpl.buildStudentReports(...)`：按学生统计课堂数据。

### 2.2 后端常用基础设施

- `common/response/ApiResponse.java`：统一接口返回格式。
- `common/exception/GlobalExceptionHandler.java`：统一异常处理，错误会打印到终端日志。
- `common/utils/JwtUtils.java`：JWT 生成和解析。
- `common/utils/PasswordUtils.java`：密码加密和校验。
- `config/SecurityConfig.java`：Spring Security 配置。
- `config/JwtAuthenticationFilter.java`：JWT 认证过滤器。
- `infrastructure/storage/LocalFileStorageService.java`：本地文件保存实现。

## 3. 学生端代码结构

学生端主入口是 `frontend/student-web/src/main.ts`，路由入口是 `frontend/student-web/src/router/index.ts`，状态管理核心是 `frontend/student-web/src/stores/studentStore.ts`。

### 3.1 学生端页面职责

- `views/LoginView.vue`：学生登录页。
- `views/JoinClassView.vue`：输入邀请码加入班级。
- `views/StudentHomeView.vue`：学生首页，展示已加入班级和当前课堂。
- `views/ClassroomEntryView.vue`：课堂入口页，显示节点和解锁状态。
- `views/ActivityNodeView.vue`：具体活动页，负责展示工具、游戏、创编和总结。
- `views/WaitingNextNodeView.vue`：等待下一节点的轮询页。

### 3.2 学生端关键函数

`frontend/student-web/src/stores/studentStore.ts`

- `login(username, password)`：登录后保存 token 和 profile，并拉取已加入班级。
- `join(inviteCode)`：加入班级后同步班级列表。
- `loadJoinedClasses()`：从后端 `/classes` 拉取学生已加入班级。
- `ensureJoinedClassesLoaded()`：路由切换时确保班级列表已同步。
- `refreshCurrentClassroom()`：刷新当前课堂会话和班级状态。
- `enterCurrentNode(nodeId)`：进入当前活动节点。
- `submitCurrentNode(nodeId, resultJson, score)`：提交活动结果。

`frontend/student-web/src/router/index.ts`

- 路由守卫会检查 `student_token`。
- 登录后会自动尝试同步已加入班级，避免刷新后丢失课堂信息。

### 3.3 学生端数据来源

- 登录态：`localStorage.student_token`。
- 用户信息：`localStorage.student_profile`。
- 班级关系：后端数据库 `class_members`。
- 当前课堂：后端数据库 `classroom_sessions` 和 `session_node_states`。
- 学生进度：后端数据库 `student_progress`、`learning_events`。

## 4. 教师端代码结构

教师端主入口是 `frontend/teacher-web/src/main.ts`，路由入口是 `frontend/teacher-web/src/router/index.ts`，登录状态在 `frontend/teacher-web/src/stores/authStore.ts`。

### 4.1 教师端页面职责

- `views/LoginView.vue`：教师登录页。
- `views/DashboardView.vue`：仪表盘。
- `views/ClassListView.vue`、`views/ClassDetailView.vue`：班级管理。
- `views/LessonUploadView.vue`：上传教案。
- `views/LessonPlanHistoryView.vue`：查看历史教案。
- `views/LessonParseResultView.vue`：查看教案解析结果。
- `views/PackageGenerateView.vue`：生成互动包。
- `views/PackageDetailView.vue`：互动包详情。
- `views/PublishPackageView.vue`：发布互动包到班级。
- `views/ClassroomControlView.vue`：课堂控制。
- `views/ClassroomReportView.vue`：课堂报表。

### 4.2 教师端关键函数

`frontend/teacher-web/src/stores/authStore.ts`

- `login(...)`：教师登录并保存 token。
- `fetchMe()`：刷新当前教师信息。
- `logout()`：清理登录态。

`frontend/teacher-web/src/api/lessonPlanApi.ts`

- `upload(file, title)`：上传教案。
- `listMine()`：获取历史教案列表。
- `getLessonPlan(id)`：获取教案详情。

`frontend/teacher-web/src/api/packageApi.ts`

- `createGenerationJob(...)`：根据教案创建生成任务。
- `listVersions(packageId)`：查看互动包版本。
- `publishPackage(packageId, classId, versionId, reviewEnabled)`：发布互动包到班级。

## 5. 代码阅读顺序建议

如果你想快速看懂系统，建议按下面顺序读：

1. 先看 `backend/music-agent-server/src/main/java/com/buyilehu/musicagent/MusicAgentServerApplication.java`
2. 再看 `common/exception/GlobalExceptionHandler.java`，理解错误如何返回和打日志。
3. 看 `AuthController.java` 和 `AuthServiceImpl.java`，理解登录链路。
4. 看 `ClassController.java` 和 `ClassServiceImpl.java`，理解班级和入班逻辑。
5. 看 `LessonPlanController.java` 和 `LessonPlanServiceImpl.java`，理解教案上传和历史记录。
6. 看 `PackagePublicationServiceImpl.java`，理解互动包如何发到班级。
7. 看 `StudentClassroomController.java` 和 `StudentProgressServiceImpl.java`，理解学生端课堂流程。
8. 最后看前端 `student-web` 和 `teacher-web` 的 `store + router + views`，对应页面功能。

## 6. 本地运行时要点

- 后端数据库使用本地 MySQL，配置在 `backend/music-agent-server/src/main/resources/application-local.yml`。
- 本地开发默认库名是 `buyilehu_music_agent_v2`，默认用户名 `root`；数据库密码只通过环境变量提供，不写入仓库。
- 学生端和教师端的登录态都保存在浏览器 `localStorage`，不是数据库。
- 用户账号和密码本身存放在数据库 `users` 表中，密码是哈希值，不是明文。
- 学生和班级的关联存放在 `class_members` 表中。

这份文档的目标是帮助你先把系统骨架看清，再去追具体功能。后面如果你要，我可以继续把“教师端功能说明”或者“数据库表结构说明”单独再整理成一份。
