package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.generator.ComponentMatcher;
import com.buyilehu.musicagent.application.generator.LessonToPackageGenerator;
import com.buyilehu.musicagent.application.generator.ProposalCardGenerator;
import com.buyilehu.musicagent.application.service.ComponentRegistryService;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.application.service.PythonRuntimeIntegrationService;
import com.buyilehu.musicagent.application.service.MusicValidationService;
import com.buyilehu.musicagent.application.service.PackageService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
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
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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
                                    ObjectMapper objectMapper) {
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
    }

    @Override
    @Transactional
    public GenerationJobResponse createAndGenerate(CreateGenerationJobRequest request) {
        User currentUser = getCurrentUser();
        if (currentUser.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只有教师可以生成互动包");
        }

        LessonPlan lessonPlan = lessonPlanRepository.findById(request.getLessonPlanId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "教案不存在"));
        if (!currentUser.getId().equals(lessonPlan.getTeacherId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只能基于自己的教案生成互动包");
        }

        GenerationJob job = createJob(lessonPlan, currentUser, request.getPreferences());
        try {
            ParsedLesson parsedLesson = parseLesson(lessonPlan.getParsedJson());
            GeneratePreferences preferences = request.getPreferences() == null
                    ? new GeneratePreferences()
                    : request.getPreferences();

            ActivityChain chain = lessonToPackageGenerator.generate(parsedLesson, preferences);
            List<ActivityNodeConfig> nodeConfigs = componentMatcher.match(chain, parsedLesson);
            pythonRuntimeIntegrationService.enrichNodes(parsedLesson, preferences, nodeConfigs);
            QualityCheckResult quality = musicValidationService.validate(chain, nodeConfigs);

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
            return GenerationJobResponse.from(job, pkg.getId(), version.getId());
        } catch (RuntimeException exception) {
            job.setStatus("failed");
            job.setProgress(100);
            job.setErrorMessage(exception.getMessage());
            job.setFinishedAt(LocalDateTime.now());
            generationJobRepository.save(job);
            throw exception;
        }
    }

    private GenerationJob createJob(LessonPlan lessonPlan, User currentUser, GeneratePreferences preferences) {
        GenerationJob job = new GenerationJob();
        job.setLessonPlanId(lessonPlan.getId());
        job.setCreatedBy(currentUser.getId());
        job.setStatus("running");
        job.setProgress(10);
        job.setStartedAt(LocalDateTime.now());
        job.setRequestParams(toJson(preferences == null ? new GeneratePreferences() : preferences));
        return generationJobRepository.save(job);
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
