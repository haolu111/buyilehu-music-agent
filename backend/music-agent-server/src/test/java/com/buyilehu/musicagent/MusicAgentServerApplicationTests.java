package com.buyilehu.musicagent;

import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.AssetRepository;
import com.buyilehu.musicagent.infrastructure.repository.ComponentInstanceRepository;
import com.buyilehu.musicagent.infrastructure.repository.GenerationJobRepository;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.OutboxEventRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.ProposalCardRepository;
import com.buyilehu.musicagent.infrastructure.repository.QualityReportRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.stream.Collectors;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = "app.async-generation.enabled=false")
@AutoConfigureMockMvc
@Testcontainers(disabledWithoutDocker = true)
class MusicAgentServerApplicationTests {
    @Container
    private static final MySQLContainer<?> MYSQL = new MySQLContainer<>("mysql:8.0.36")
            .withDatabaseName("buyilehu_music_agent_test")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void databaseProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", MYSQL::getJdbcUrl);
        registry.add("spring.datasource.username", MYSQL::getUsername);
        registry.add("spring.datasource.password", MYSQL::getPassword);
        registry.add("spring.flyway.locations",
                () -> "classpath:db/migration,classpath:db/local");
        registry.add("app.storage.root", () -> "target/test-uploads");
        registry.add("spring.cache.type", () -> "none");
        registry.add("app.distributed-lock.enabled", () -> "false");
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private GenerationJobRepository generationJobRepository;

    @Autowired
    private InteractivePackageRepository interactivePackageRepository;

    @Autowired
    private PackageVersionRepository packageVersionRepository;

    @Autowired
    private ProposalCardRepository proposalCardRepository;

    @Autowired
    private ActivityNodeRepository activityNodeRepository;

    @Autowired
    private ComponentInstanceRepository componentInstanceRepository;

    @Autowired
    private AssetRepository assetRepository;

    @Autowired
    private QualityReportRepository qualityReportRepository;

    @Autowired
    private OutboxEventRepository outboxEventRepository;

    @Test
    void contextLoadsAndHealthEndpointIsPublic() throws Exception {
        mockMvc.perform(get("/api/v1/system/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.status").value("UP"));
    }

    @Test
    void flywayCreatesTransactionalSchemaAndCoreIndexes() {
        String engine = jdbcTemplate.queryForObject(
                "SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'generation_jobs'",
                String.class);
        Integer versionIndexCount = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = DATABASE() "
                        + "AND TABLE_NAME = 'package_versions' AND INDEX_NAME = 'uk_package_versions_package_no'",
                Integer.class);

        org.assertj.core.api.Assertions.assertThat(engine).isEqualToIgnoringCase("InnoDB");
        org.assertj.core.api.Assertions.assertThat(versionIndexCount).isEqualTo(1);
    }

    @Test
    void businessEndpointRequiresAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/users/1"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void teacherCanLoginAndGetCurrentUser() throws Exception {
        String token = loginAndGetToken("teacher001", "123456");

        mockMvc.perform(get("/api/v1/auth/me")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.username").value("teacher001"))
                .andExpect(jsonPath("$.data.role").value("teacher"));
    }

    @Test
    void teacherCreatesClassAndStudentJoinsByInviteCode() throws Exception {
        String teacherToken = loginAndGetToken("teacher001", "123456");
        String studentToken = loginAndGetToken("student001", "123456");

        String createClassResponse = mockMvc.perform(post("/api/v1/classes")
                        .header("Authorization", "Bearer " + teacherToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"className\":\"一年级音乐一班\",\"description\":\"节奏启蒙班\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").isNumber())
                .andExpect(jsonPath("$.data.className").value("一年级音乐一班"))
                .andExpect(jsonPath("$.data.inviteCode").isNotEmpty())
                .andReturn()
                .getResponse()
                .getContentAsString(StandardCharsets.UTF_8);

        JsonNode classData = objectMapper.readTree(createClassResponse).path("data");
        long classId = classData.path("id").asLong();
        String inviteCode = classData.path("inviteCode").asText();

        mockMvc.perform(post("/api/v1/classes/join")
                        .header("Authorization", "Bearer " + studentToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"inviteCode\":\"" + inviteCode + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").value(classId));

        mockMvc.perform(get("/api/v1/classes/" + classId + "/students")
                        .header("Authorization", "Bearer " + teacherToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data[0].username").value("student001"))
                .andExpect(jsonPath("$.data[0].realName").value("学生001"));
    }

    @Test
    void teacherUploadsTxtLessonPlanAndParserCreatesStructuredResult() throws Exception {
        String teacherToken = loginAndGetToken("teacher001", "123456");
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "lesson.txt",
                MediaType.TEXT_PLAIN_VALUE,
                ("课程名称：小星星节奏课\n"
                        + "年级：一年级\n"
                        + "教学目标：感受稳定节拍\n"
                        + "教学重点：节奏与旋律\n"
                        + "教学过程：聆听歌曲\n"
                        + "跟随节奏拍手\n").getBytes("UTF-8"));

        String uploadResponse = mockMvc.perform(multipart("/api/v1/lesson-plans")
                        .file(file)
                        .param("title", "小星星节奏课")
                        .header("Authorization", "Bearer " + teacherToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").isNumber())
                .andExpect(jsonPath("$.data.sourceFileUrl").isNotEmpty())
                .andExpect(jsonPath("$.data.rawText").isNotEmpty())
                .andExpect(jsonPath("$.data.parsedJson").isNotEmpty())
                .andExpect(jsonPath("$.data.parseStatus").value("success"))
                .andReturn()
                .getResponse()
                .getContentAsString(StandardCharsets.UTF_8);

        JsonNode data = objectMapper.readTree(uploadResponse).path("data");
        long lessonPlanId = data.path("id").asLong();
        JsonNode parsedJson = objectMapper.readTree(data.path("parsedJson").asText());

        org.assertj.core.api.Assertions.assertThat(parsedJson.path("courseName").asText()).isEqualTo("小星星节奏课");
        org.assertj.core.api.Assertions.assertThat(parsedJson.path("objectives").get(0).asText()).contains("感受稳定节拍");
        org.assertj.core.api.Assertions.assertThat(parsedJson.path("musicElements").toString()).contains("节奏");

        mockMvc.perform(get("/api/v1/lesson-plans/" + lessonPlanId)
                        .header("Authorization", "Bearer " + teacherToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").value(lessonPlanId))
                .andExpect(jsonPath("$.data.parseStatus").value("success"));
    }

    @Test
    void teacherGeneratesInteractivePackageFromLessonPlan() throws Exception {
        String teacherToken = loginAndGetToken("teacher001", "123456");
        long lessonPlanId = uploadTxtLessonPlanAndGetId(teacherToken);
        long jobCountBefore = generationJobRepository.count();
        String idempotencyKey = "generation-test-" + lessonPlanId;
        String requestBody = "{\"lessonPlanId\":" + lessonPlanId
                + ",\"preferences\":{\"style\":\"standard\",\"durationMinutes\":40}}";

        String generationResponse = mockMvc.perform(post("/api/v1/generation-jobs")
                        .header("Authorization", "Bearer " + teacherToken)
                        .header("Idempotency-Key", idempotencyKey)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.status").value("success"))
                .andExpect(jsonPath("$.data.progress").value(100))
                .andExpect(jsonPath("$.data.packageId").isNumber())
                .andExpect(jsonPath("$.data.versionId").isNumber())
                .andExpect(jsonPath("$.data.designProvider").isNotEmpty())
                .andReturn()
                .getResponse()
                .getContentAsString(StandardCharsets.UTF_8);

        JsonNode data = objectMapper.readTree(generationResponse).path("data");
        long jobId = data.path("id").asLong();
        long packageId = data.path("packageId").asLong();
        long versionId = data.path("versionId").asLong();

        mockMvc.perform(post("/api/v1/generation-jobs")
                        .header("Authorization", "Bearer " + teacherToken)
                        .header("Idempotency-Key", idempotencyKey)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.id").value(jobId));
        org.assertj.core.api.Assertions.assertThat(generationJobRepository.count())
                .isEqualTo(jobCountBefore + 1);

        org.assertj.core.api.Assertions.assertThat(generationJobRepository.findById(jobId)).isPresent();
        org.assertj.core.api.Assertions.assertThat(interactivePackageRepository.findById(packageId)).isPresent();
        org.assertj.core.api.Assertions.assertThat(packageVersionRepository.findById(versionId)).isPresent();
        org.assertj.core.api.Assertions.assertThat(proposalCardRepository.findByPackageId(packageId)).hasSize(1);
        org.assertj.core.api.Assertions.assertThat(assetRepository.findByPackageId(packageId)).hasSize(1);
        org.assertj.core.api.Assertions.assertThat(qualityReportRepository.findByPackageId(packageId)).hasSize(1);
        org.assertj.core.api.Assertions.assertThat(outboxEventRepository
                .findByAggregateTypeAndAggregateIdAndEventType(
                        "generation_job", jobId, "generation_job.created"))
                .get()
                .extracting(com.buyilehu.musicagent.domain.entity.OutboxEvent::getStatus)
                .isEqualTo("published");

        List<ActivityNode> nodes = activityNodeRepository.findByPackageIdOrderBySortOrderAsc(packageId);
        org.assertj.core.api.Assertions.assertThat(nodes).hasSizeBetween(3, 7);
        org.assertj.core.api.Assertions.assertThat(nodes)
                .extracting(ActivityNode::getTitle)
                .allSatisfy(title -> org.assertj.core.api.Assertions.assertThat(title).isNotBlank());

        List<Long> nodeIds = nodes.stream().map(ActivityNode::getId).collect(Collectors.toList());
        org.assertj.core.api.Assertions.assertThat(componentInstanceRepository.findByActivityNodeIdIn(nodeIds))
                .isNotEmpty();

        String confirmResponse = mockMvc.perform(post("/api/v1/packages/" + packageId + "/proposal/confirm")
                        .header("Authorization", "Bearer " + teacherToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.packageInfo.currentVersionId").value(versionId))
                .andReturn()
                .getResponse()
                .getContentAsString(StandardCharsets.UTF_8);
        long confirmedVersionId = objectMapper.readTree(confirmResponse)
                .path("data").path("packageInfo").path("currentVersionId").asLong();

        Long lockVersionBefore = interactivePackageRepository.findById(packageId)
                .orElseThrow(AssertionError::new)
                .getLockVersion();
        long nodeId = nodes.get(0).getId();
        mockMvc.perform(patch("/api/v1/packages/" + packageId + "/nodes/" + nodeId + "/config")
                        .header("Authorization", "Bearer " + teacherToken)
                        .header("X-Package-Version", confirmedVersionId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"description\":\"并发编辑测试\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.fromVersionId").value(confirmedVersionId))
                .andExpect(jsonPath("$.data.toVersionId").isNumber());

        Long lockVersionAfter = interactivePackageRepository.findById(packageId)
                .orElseThrow(AssertionError::new)
                .getLockVersion();
        org.assertj.core.api.Assertions.assertThat(lockVersionAfter).isGreaterThan(lockVersionBefore);

        mockMvc.perform(patch("/api/v1/packages/" + packageId + "/nodes/" + nodeId + "/config")
                        .header("Authorization", "Bearer " + teacherToken)
                        .header("X-Package-Version", confirmedVersionId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"description\":\"过期编辑\"}"))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value(40900));
    }

    private long uploadTxtLessonPlanAndGetId(String teacherToken) throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "generation-lesson.txt",
                MediaType.TEXT_PLAIN_VALUE,
                ("课程名称：节奏创编课\n"
                        + "年级：二年级\n"
                        + "教学目标：体验节拍和节奏\n"
                        + "教学重点：2/4节拍、节奏疏密与旋律\n"
                        + "教学过程：节拍体验\n"
                        + "节奏拖拽\n"
                        + "合作创编\n"
                        + "总结归纳\n").getBytes("UTF-8"));

        String uploadResponse = mockMvc.perform(multipart("/api/v1/lesson-plans")
                        .file(file)
                        .param("title", "节奏创编课")
                        .header("Authorization", "Bearer " + teacherToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andReturn()
                .getResponse()
                .getContentAsString(StandardCharsets.UTF_8);

        return objectMapper.readTree(uploadResponse).path("data").path("id").asLong();
    }

    private String loginAndGetToken(String username, String password) throws Exception {
        String loginResponse = mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"username\":\"" + username + "\",\"password\":\"" + password + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.token").isNotEmpty())
                .andReturn()
                .getResponse()
                .getContentAsString(StandardCharsets.UTF_8);

        return objectMapper.readTree(loginResponse).path("data").path("token").asText();
    }
}


