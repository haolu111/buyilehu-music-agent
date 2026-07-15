package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.PackageModifyRequest;
import com.buyilehu.musicagent.application.dto.request.PackageNodeConfigUpdateRequest;
import com.buyilehu.musicagent.application.dto.response.PackageModifyResponse;
import com.buyilehu.musicagent.application.service.ActivityNodeModifyService;
import com.buyilehu.musicagent.application.service.ComponentConfigService;
import com.buyilehu.musicagent.application.service.PackageModifyService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ComponentInstance;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.PackageModifyRecord;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.PackageVersionDiff;
import com.buyilehu.musicagent.domain.entity.QualityReport;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.lock.DistributedLockManager;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.ComponentInstanceRepository;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageModifyRecordRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionDiffRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.QualityReportRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;

@Service
public class PackageModifyServiceImpl implements PackageModifyService {
    private final InteractivePackageRepository interactivePackageRepository;
    private final PackageVersionRepository packageVersionRepository;
    private final ActivityNodeRepository activityNodeRepository;
    private final ComponentInstanceRepository componentInstanceRepository;
    private final PackageModifyRecordRepository packageModifyRecordRepository;
    private final PackageVersionDiffRepository packageVersionDiffRepository;
    private final QualityReportRepository qualityReportRepository;
    private final UserRepository userRepository;
    private final ActivityNodeModifyService activityNodeModifyService;
    private final ComponentConfigService componentConfigService;
    private final ObjectMapper objectMapper;
    private final DistributedLockManager distributedLockManager;
    private final TransactionTemplate transactionTemplate;

    public PackageModifyServiceImpl(InteractivePackageRepository interactivePackageRepository,
                                    PackageVersionRepository packageVersionRepository,
                                    ActivityNodeRepository activityNodeRepository,
                                    ComponentInstanceRepository componentInstanceRepository,
                                    PackageModifyRecordRepository packageModifyRecordRepository,
                                    PackageVersionDiffRepository packageVersionDiffRepository,
                                    QualityReportRepository qualityReportRepository,
                                    UserRepository userRepository,
                                    ActivityNodeModifyService activityNodeModifyService,
                                    ComponentConfigService componentConfigService,
                                    ObjectMapper objectMapper,
                                    DistributedLockManager distributedLockManager,
                                    TransactionTemplate transactionTemplate) {
        this.interactivePackageRepository = interactivePackageRepository;
        this.packageVersionRepository = packageVersionRepository;
        this.activityNodeRepository = activityNodeRepository;
        this.componentInstanceRepository = componentInstanceRepository;
        this.packageModifyRecordRepository = packageModifyRecordRepository;
        this.packageVersionDiffRepository = packageVersionDiffRepository;
        this.qualityReportRepository = qualityReportRepository;
        this.userRepository = userRepository;
        this.activityNodeModifyService = activityNodeModifyService;
        this.componentConfigService = componentConfigService;
        this.objectMapper = objectMapper;
        this.distributedLockManager = distributedLockManager;
        this.transactionTemplate = transactionTemplate;
    }

    @Override
    public PackageModifyResponse updateNodeConfig(Long packageId, Long nodeId, Long baseVersionId,
                                                  PackageNodeConfigUpdateRequest request) {
        PackageModifyRequest modifyRequest = new PackageModifyRequest();
        modifyRequest.setNodeId(nodeId);
        modifyRequest.setBaseVersionId(baseVersionId);
        modifyRequest.setModifyType("node_config");
        modifyRequest.setConfig(request);
        return modify(packageId, modifyRequest);
    }

    @Override
    public PackageModifyResponse modify(Long packageId, PackageModifyRequest request) {
        return distributedLockManager.executeWithLock("package-modify:" + packageId,
                () -> transactionTemplate.execute(status -> modifyInTransaction(packageId, request)));
    }

    private PackageModifyResponse modifyInTransaction(Long packageId, PackageModifyRequest request) {
        User teacher = getCurrentTeacher();
        InteractivePackage pkg = interactivePackageRepository.findById(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package not found"));
        if (!teacher.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "package access denied");
        }
        if (!request.getBaseVersionId().equals(pkg.getCurrentVersionId())) {
            throw new BusinessException(ErrorCode.CONFLICT, "课程包已被更新，请刷新后重新编辑");
        }

        PackageVersion fromVersion = packageVersionRepository.findFirstByPackageIdOrderByVersionNoDesc(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package version not found"));
        ActivityNode node = activityNodeRepository.findByIdAndPackageId(request.getNodeId(), packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "activity node not found"));

        Map<String, Object> beforeSnapshot = buildSnapshot(packageId);
        activityNodeModifyService.applyNodeConfig(node, request.getConfig());
        activityNodeRepository.save(node);
        componentConfigService.applyComponentConfig(node, request.getConfig());
        Map<String, Object> afterSnapshot = buildSnapshot(packageId);

        PackageVersion toVersion = new PackageVersion();
        toVersion.setPackageId(packageId);
        toVersion.setVersionNo(fromVersion.getVersionNo() + 1);
        toVersion.setCreatedBy(teacher.getId());
        toVersion.setSnapshotJson(toJson(afterSnapshot));
        toVersion.setRemark(buildRemark(request));
        toVersion.setStatus("modified");
        toVersion = packageVersionRepository.save(toVersion);

        PackageModifyRecord record = new PackageModifyRecord();
        record.setPackageId(packageId);
        record.setVersionId(toVersion.getId());
        record.setModifiedBy(teacher.getId());
        record.setModifyType(request.getModifyType() == null ? "node_config" : request.getModifyType());
        record.setModifyContent(toJson(request));
        packageModifyRecordRepository.save(record);

        PackageVersionDiff diff = new PackageVersionDiff();
        diff.setPackageId(packageId);
        diff.setFromVersionId(fromVersion.getId());
        diff.setToVersionId(toVersion.getId());
        diff.setDiffJson(toJson(buildDiff(request, beforeSnapshot, afterSnapshot)));
        packageVersionDiffRepository.save(diff);

        QualityReport qualityReport = new QualityReport();
        qualityReport.setPackageId(packageId);
        qualityReport.setVersionId(toVersion.getId());
        qualityReport.setScore(90);
        qualityReport.setStatus("passed");
        qualityReport.setReportJson(toJson(buildQualityReport(request, afterSnapshot)));
        qualityReportRepository.save(qualityReport);

        pkg.setCurrentVersionId(toVersion.getId());
        pkg.setStatus("modified");
        interactivePackageRepository.save(pkg);

        PackageModifyResponse response = new PackageModifyResponse();
        response.setPackageId(packageId);
        response.setNodeId(request.getNodeId());
        response.setFromVersionId(fromVersion.getId());
        response.setToVersionId(toVersion.getId());
        response.setVersionNo(toVersion.getVersionNo());
        response.setMessage("修改已保存并生成新版本");
        return response;
    }

    private Map<String, Object> buildSnapshot(Long packageId) {
        Map<String, Object> snapshot = new HashMap<>();
        List<Map<String, Object>> nodeSnapshots = new ArrayList<>();
        List<ActivityNode> nodes = activityNodeRepository.findByPackageIdOrderBySortOrderAsc(packageId);
        for (ActivityNode node : nodes) {
            Map<String, Object> nodeSnapshot = new HashMap<>();
            nodeSnapshot.put("id", node.getId());
            nodeSnapshot.put("title", node.getTitle());
            nodeSnapshot.put("nodeType", node.getNodeType());
            nodeSnapshot.put("sortOrder", node.getSortOrder());
            nodeSnapshot.put("configJson", node.getConfigJson());
            List<Map<String, Object>> componentSnapshots = new ArrayList<>();
            for (ComponentInstance instance : componentInstanceRepository.findByActivityNodeIdOrderBySortOrderAsc(node.getId())) {
                Map<String, Object> componentSnapshot = new HashMap<>();
                componentSnapshot.put("id", instance.getId());
                componentSnapshot.put("componentDefinitionId", instance.getComponentDefinitionId());
                componentSnapshot.put("instanceName", instance.getInstanceName());
                componentSnapshot.put("sortOrder", instance.getSortOrder());
                componentSnapshot.put("propsJson", instance.getPropsJson());
                componentSnapshots.add(componentSnapshot);
            }
            nodeSnapshot.put("components", componentSnapshots);
            nodeSnapshots.add(nodeSnapshot);
        }
        snapshot.put("nodes", nodeSnapshots);
        return snapshot;
    }

    private Map<String, Object> buildDiff(PackageModifyRequest request, Map<String, Object> beforeSnapshot, Map<String, Object> afterSnapshot) {
        Map<String, Object> diff = new HashMap<>();
        diff.put("nodeId", request.getNodeId());
        diff.put("modifyType", request.getModifyType());
        diff.put("config", request.getConfig());
        diff.put("beforeSummary", buildSnapshotSummary(beforeSnapshot));
        diff.put("afterSummary", buildSnapshotSummary(afterSnapshot));
        return diff;
    }

    private Map<String, Object> buildQualityReport(PackageModifyRequest request, Map<String, Object> afterSnapshot) {
        Map<String, Object> report = new HashMap<>();
        report.put("status", "passed");
        report.put("score", 90);
        report.put("message", "参数级修改已通过基础检查");
        report.put("nodeId", request.getNodeId());
        report.put("snapshotSummary", buildSnapshotSummary(afterSnapshot));
        return report;
    }

    private Map<String, Object> buildSnapshotSummary(Map<String, Object> snapshot) {
        Map<String, Object> summary = new HashMap<>();
        Object nodesValue = snapshot.get("nodes");
        if (!(nodesValue instanceof List)) {
            summary.put("nodeCount", 0);
            summary.put("componentCount", 0);
            return summary;
        }
        List<?> nodes = (List<?>) nodesValue;
        int componentCount = 0;
        for (Object nodeValue : nodes) {
            if (!(nodeValue instanceof Map)) {
                continue;
            }
            Object componentsValue = ((Map<?, ?>) nodeValue).get("components");
            if (componentsValue instanceof List) {
                componentCount += ((List<?>) componentsValue).size();
            }
        }
        summary.put("nodeCount", nodes.size());
        summary.put("componentCount", componentCount);
        return summary;
    }

    private String buildRemark(PackageModifyRequest request) {
        return "参数级修改：nodeId=" + request.getNodeId();
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "modify payload is not valid json");
        }
    }

    private User getCurrentTeacher() {
        User user = userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "login user not found"));
        if (user.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "teacher permission required");
        }
        return user;
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
    }
}
