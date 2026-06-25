# music-agent-server

“不亦乐乎”音乐课堂智能体后端基础工程，采用 Java 8、Spring Boot 2.7、Maven 和标准三层架构。

## 分层

- `presentation`：HTTP 接口、参数校验、统一返回。
- `application`：用例编排与业务规则，包含 `service`、`generator`、DTO。
- `domain`：实体、枚举和领域模型。
- `infrastructure`：JPA Repository、文件存储、AI 客户端等基础设施实现。

依赖方向为 `presentation -> application -> domain/infrastructure`。Controller 不直接调用 Repository。

## 本地启动

需要 JDK 8 和 Maven 3.8+。

```bash
mvn spring-boot:run
```

默认激活 `local` 环境，使用内存 H2（MySQL 兼容模式）。健康检查地址：

```text
GET http://localhost:8080/api/v1/system/health
```

除健康检查、Actuator 和 H2 控制台外，接口默认受 Spring Security 保护。JWT 登录将在认证模块实现时接入。

## 测试与构建

```bash
mvn test
mvn clean package
```

## 使用 MySQL

```bash
java -jar target/music-agent-server-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
```

生产环境读取以下环境变量：`DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USERNAME`、`DB_PASSWORD`、`STORAGE_PATH`。首次启动由 Flyway 执行 `db/migration` 中的脚本。
