package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.application.event.GenerationJobCreatedEvent;
import com.buyilehu.musicagent.application.generator.ComponentMatcher;
import com.buyilehu.musicagent.application.generator.LessonToPackageGenerator;
import com.buyilehu.musicagent.application.generator.ProposalCardGenerator;
import com.buyilehu.musicagent.application.service.ComponentRegistryService;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.application.service.GenerationJobStatusService;
import com.buyilehu.musicagent.application.service.PythonRuntimeIntegrationService;
import com.buyilehu.musicagent.application.service.MusicValidationService;
import com.buyilehu.musicagent.application.service.PackageService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.config.AsyncGenerationProperties;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.Asset;
import com.buyilehu.musicagent.domain.entity.ComponentDefinition;
import com.buyilehu.musicagent.domain.entity.ComponentInstance;
import com.buyilehu.musicagent.domain.entity.GenerationJob;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.LessonPlan;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.ProposalCard;
import com.buyilehu.musicagent.domain.entity.QualityReport;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.domain.model.QualityCheckResult;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.AssetRepository;
import com.buyilehu.musicagent.infrastructure.repository.ComponentInstanceRepository;
import com.buyilehu.musicagent.infrastructure.repository.GenerationJobRepository;
import com.buyilehu.musicagent.infrastructure.repository.LessonPlanRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.ProposalCardRepository;
import com.buyilehu.musicagent.infrastructure.repository.QualityReportRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import com.buyilehu.musicagent.infrastructure.outbox.OutboxEventService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

@Service
public class GenerationJobServiceImpl implements GenerationJobService {
    private final GenerationJobRepository generationJobRepository;
    private final LessonPlanRepository lessonPlanRepository;
    private final UserRepository userRepository;
    private final PackageService packageService;
    private final LessonToPackageGenerator lessonToPackageGenerator;
    private final ComponentMatcher componentMatcher;
    private final PythonRuntimeIntegrationService pythonRuntimeIntegrationService;
    private final MusicValidationService musicValidationService;
    private final ProposalCardGenerator proposalCardGenerator;
    private final ComponentRegistryService componentRegistryService;
    private final PackageVersionRepository packageVersionRepository;
    private final ActivityNodeRepository activityNodeRepository;
    private final ComponentInstanceRepository componentInstanceRepository;
    private final AssetRepository assetRepository;
    private final ProposalCardRepository proposalCardRepository;
    private final QualityReportRepository qualityReportRepository;
    private final ObjectMapper objectMapper;
    private final GenerationJobStatusService statusService;
    private final ApplicationEventPublisher eventPublisher;
    private final OutboxEventService outboxEventService;
    private final AsyncGenerationProperties asyncGenerationProperties;

    public GenerationJobServiceImpl(GenerationJobRepository generationJobRepository,
                                    LessonPlanRepository lessonPlanRepository,
                                    UserRepository userRepository,
                                    PackageService packageService,
                                    LessonToPackageGenerator lessonToPackageGenerator,
                                    ComponentMatcher componentMatcher,
                                    PythonRuntimeIntegrationService pythonRuntimeIntegrationService,
                                    MusicValidationService musicValidationService,
                                    ProposalCardGenerator proposalCardGenerator,
                                    ComponentRegistryService componentRegistryService,
                                    PackageVersionRepository packageVersionRepository,
                                    ActivityNodeRepository activityNodeRepository,
                                    ComponentInstanceRepository componentInstanceRepository,
                                    AssetRepository assetRepository,
                                    ProposalCardRepository proposalCardRepository,
                                    QualityReportRepository qualityReportRepository,
                                    ObjectMapper objectMapper,
                                    GenerationJobStatusService statusService,
                                    ApplicationEventPublisher eventPublisher,
                                    OutboxEventService outboxEventService,
                                    AsyncGenerationProperties asyncGenerationProperties) {
        this.generationJobRepository = generationJobRepository;
        this.lessonPlanRepository = lessonPlanRepository;
        this.userRepository = userRepository;
        this.packageService = packageService;
        this.lessonToPackageGenerator = lessonToPackageGenerator;
        this.componentMatcher = componentMatcher;
        this.pythonRuntimeIntegrationService = pythonRuntimeIntegrationService;
        this.musicValidationService = musicValidationService;
        this.proposalCardGenerator = proposalCardGenerator;
        this.componentRegistryService = componentRegistryService;
        this.packageVersionRepository = packageVersionRepository;
        this.activityNodeRepository = activityNodeRepository;
        this.componentInstanceRepository = componentInstanceRepository;
        this.assetRepository = assetRepository;
        this.proposalCardRepository = proposalCardRepository;
        this.qualityReportRepository = qualityReportRepository;
        this.objectMapper = objectMapper;
        this.statusService = statusService;
        this.eventPublisher = eventPublisher;
        this.outboxEventService = outboxEventService;
        this.asyncGenerationProperties = asyncGenerationProperties;
    }

    @Override
    @Transactional
    public GenerationJobStatus create(CreateGenerationJobRequest request, String idempotencyKey) {
        User currentUser = getCurrentUser();
        if (currentUser.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只有教师可以生成互动包");
        }

        LessonPlan lessonPlan = lessonPlanRepository.findById(request.getLessonPlanId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "教案不存在"));
        if (!currentUser.getId().equals(lessonPlan.getTeacherId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只能基于自己的教案生成互动包");
        }

        String normalizedKey = normalizeIdempotencyKey(idempotencyKey);
        String preferencesJson = toJson(request.getPreferences() == null
                ? new GeneratePreferences() : request.getPreferences());
        String requestHash = sha256(request.getLessonPlanId() + ":" + preferencesJson);
        if (normalizedKey != null) {
            GenerationJob existing = generationJobRepository
                    .findByCreatedByAndIdempotencyKey(currentUser.getId(), normalizedKey)
                    .orElse(null);
            if (existing != null) {
                if (!requestHash.equals(existing.getRequestHash())) {
                    throw new BusinessException(ErrorCode.CONFLICT,
                            "Idempotency-Key 已用于不同的生成请求");
                }
                return statusService.find(existing);
            }
        }

        GenerationJob job = createJob(lessonPlan, currentUser, preferencesJson, normalizedKey, requestHash);
        GenerationJobStatus status = statusService.queued(job);
        outboxEventService.recordGenerationJobCreated(job.getId());
        if (!asyncGenerationProperties.isEnabled()) {
            eventPublisher.publishEvent(new GenerationJobCreatedEvent(job.getId()));
        }
        return status;
    }

    @Override
    @Transactional(readOnly = true)
    public GenerationJobStatus getStatus(Long jobId) {
        GenerationJob job = findJob(jobId);
        if (!job.getCreatedBy().equals(getCurrentUserId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "无权访问该生成任务");
        }
        return statusService.find(job);
    }

    @Override
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public GenerationJobResponse execute(Long jobId) {
        GenerationJob job = generationJobRepository.findByIdForUpdate(jobId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "生成任务不存在"));
        if ("success".equals(job.getStatus())) {
            return responseFromStatus(statusService.find(job));
        }
        if ("failed".equals(job.getStatus())) {
            throw new IllegalStateException("Generation job has already failed");
        }

        User currentUser = userRepository.findById(job.getCreatedBy())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "任务创建人不存在"));
        LessonPlan lessonPlan = lessonPlanRepository.findById(job.getLessonPlanId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "教案不存在"));

        job.setStatus("running");
        job.setProgress(5);
        job.setStartedAt(LocalDateTime.now());
        generationJobRepository.save(job);
        statusService.progress(job, "parsing", 10, "正在读取教案解析结果");

        ParsedLesson parsedLesson = parseLesson(lessonPlan.getParsedJson());
        GeneratePreferences preferences = parsePreferences(job.getRequestParams());
        statusService.progress(job, "designing", 25, "正在设计课堂活动链");
        ActivityChain chain = lessonToPackageGenerator.generate(parsedLesson, preferences);

        statusService.progress(job, "matching", 50, "正在匹配互动组件");
        List<ActivityNodeConfig> nodeConfigs = componentMatcher.match(chain, parsedLesson);
        statusService.progress(job, "enriching", 65, "正在构建互动组件运行参数");
        pythonRuntimeIntegrationService.enrichNodes(parsedLesson, preferences, nodeConfigs);
        statusService.progress(job, "validating", 75, "正在校验音乐教学方案");
        QualityCheckResult quality = musicValidationService.validate(chain, nodeConfigs);

        statusService.progress(job, "persisting", 85, "正在保存互动包");
        InteractivePackage pkg = packageService.createPackage(lessonPlan, parsedLesson, job.getId());
        PackageVersion version = createInitialVersion(pkg, currentUser, chain, nodeConfigs);
        saveNodesAndComponents(pkg, nodeConfigs);
        savePlaceholderAssets(pkg, currentUser);
        saveProposalCard(job, pkg, chain, quality);
        saveQualityReport(pkg, version, quality);

        job.setStatus("success");
        job.setProgress(100);
        job.setFinishedAt(LocalDateTime.now());
        generationJobRepository.save(job);
        return GenerationJobResponse.from(job, pkg.getId(), version.getId(), chain);
    }

    @Override
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void fail(Long jobId, Throwable error) {
        GenerationJob job = findJob(jobId);
        if ("success".equals(job.getStatus())) {
            return;
        }
        job.setStatus("failed");
        job.setProgress(100);
        job.setErrorMessage(errorMessage(error));
        job.setFinishedAt(LocalDateTime.now());
        generationJobRepository.save(job);
        statusService.failed(job);
    }

    private GenerationJob createJob(LessonPlan lessonPlan, User currentUser, String preferencesJson,
                                    String idempotencyKey, String requestHash) {
        GenerationJob job = new GenerationJob();
        job.setLessonPlanId(lessonPlan.getId());
        job.setCreatedBy(currentUser.getId());
        job.setStatus("queued");
        job.setProgress(0);
        job.setRequestParams(preferencesJson);
        job.setIdempotencyKey(idempotencyKey);
        job.setRequestHash(requestHash);
        return generationJobRepository.save(job);
    }

    private String normalizeIdempotencyKey(String value) {
        if (value == null || value.trim().isEmpty()) {
            return null;
        }
        String normalized = value.trim();
        if (normalized.length() > 64 || !normalized.matches("[A-Za-z0-9._:-]+")) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "Idempotency-Key 格式不正确");
        }
        return normalized;
    }

    private String sha256(String value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder result = new StringBuilder(digest.length * 2);
            for (byte item : digest) {
                result.append(String.format("%02x", item & 0xff));
            }
            return result.toString();
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is unavailable", exception);
        }
    }

    private GenerationJob findJob(Long jobId) {
        return generationJobRepository.findById(jobId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "生成任务不存在"));
    }

    private GeneratePreferences parsePreferences(String requestParams) {
        try {
            return objectMapper.readValue(requestParams, GeneratePreferences.class);
        } catch (Exception exception) {
            return new GeneratePreferences();
        }
    }

    private GenerationJobResponse responseFromStatus(GenerationJobStatus status) {
        return new GenerationJobResponse(status.getId(), status.getLessonPlanId(), status.getPackageId(),
                status.getVersionId(), status.getStatus(), status.getProgress(), status.getErrorMessage(),
                status.getDesignProvider(), status.getDesignModel(), status.getDesignFallbackReason(),
                status.getDesignTraceId());
    }

    private String errorMessage(Throwable error) {
        String message = error.getMessage();
        return message == null || message.trim().isEmpty() ? error.getClass().getSimpleName() : message;
    }

    private ParsedLesson parseLesson(String parsedJson) {
        if (parsedJson == null || parsedJson.trim().isEmpty()) {
            return ParsedLesson.fallback();
        }
        try {
            return objectMapper.readValue(parsedJson, ParsedLesson.class);
        } catch (Exception exception) {
            return ParsedLesson.fallback();
        }
    }

    private PackageVersion createInitialVersion(InteractivePackage pkg, User currentUser,
                                                ActivityChain chain, List<ActivityNodeConfig> nodeConfigs) {
        Map<String, Object> snapshot = new HashMap<>();
        snapshot.put("chain", chain);
        snapshot.put("nodes", nodeConfigs);

        PackageVersion version = new PackageVersion();
        version.setPackageId(pkg.getId());
        version.setVersionNo(1);
        version.setCreatedBy(currentUser.getId());
        version.setSnapshotJson(toJson(snapshot));
        version.setRemark("初始生成版本");
        version.setStatus("generated");
        return packageVersionRepository.save(version);
    }

    private void saveNodesAndComponents(InteractivePackage pkg, List<ActivityNodeConfig> nodeConfigs) {
        for (ActivityNodeConfig nodeConfig : nodeConfigs) {
            ActivityNode node = new ActivityNode();
            node.setPackageId(pkg.getId());
            node.setTitle(nodeConfig.getTitle());
            node.setNodeType(nodeConfig.getNodeType());
            node.setSortOrder(nodeConfig.getSortOrder());
            node.setConfigJson(toJson(nodeConfig));
            ActivityNode savedNode = activityNodeRepository.save(node);

            int sortOrder = 1;
            for (String componentKey : nodeConfig.getComponentKeys()) {
                ComponentDefinition definition = componentRegistryService.getOrCreate(componentKey);
                ComponentInstance instance = new ComponentInstance();
                instance.setActivityNodeId(savedNode.getId());
                instance.setComponentDefinitionId(definition.getId());
                instance.setInstanceName(componentKey);
                instance.setSortOrder(sortOrder++);
                instance.setPropsJson("{\"componentKey\":\"" + componentKey + "\"}");
                componentInstanceRepository.save(instance);
            }
        }
    }

    private void savePlaceholderAssets(InteractivePackage pkg, User currentUser) {
        Asset asset = new Asset();
        asset.setOwnerId(currentUser.getId());
        asset.setPackageId(pkg.getId());
        asset.setType("placeholder");
        asset.setFileName("package-cover-placeholder.png");
        asset.setFileUrl("assets/placeholders/package-cover-placeholder.png");
        asset.setMimeType("image/png");
        asset.setFileSize(0L);
        assetRepository.save(asset);
    }

    private void saveProposalCard(GenerationJob job, InteractivePackage pkg,
                                  ActivityChain chain, QualityCheckResult quality) {
        ProposalCard proposalCard = new ProposalCard();
        proposalCard.setGenerationJobId(job.getId());
        proposalCard.setPackageId(pkg.getId());
        proposalCard.setTitle("互动包生成建议");
        proposalCard.setContent(proposalCardGenerator.generate(chain, quality));
        proposalCard.setStatus("generated");
        proposalCard.setConfirmStatus("pending");
        proposalCardRepository.save(proposalCard);
    }

    private void saveQualityReport(InteractivePackage pkg, PackageVersion version, QualityCheckResult quality) {
        QualityReport report = new QualityReport();
        report.setPackageId(pkg.getId());
        report.setVersionId(version.getId());
        report.setScore(quality.getScore());
        report.setStatus(quality.getStatus());
        report.setReportJson(toJson(quality));
        qualityReportRepository.save(report);
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            return "{}";
        }
    }

    private User getCurrentUser() {
        return userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "登录用户不存在"));
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
    }
}
