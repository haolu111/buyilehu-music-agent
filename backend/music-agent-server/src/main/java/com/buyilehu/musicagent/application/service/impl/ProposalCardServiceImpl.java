package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.response.PackageResponse;
import com.buyilehu.musicagent.application.dto.response.ProposalCardResponse;
import com.buyilehu.musicagent.application.dto.response.ProposalCardResponse.ActivityNodeView;
import com.buyilehu.musicagent.application.dto.response.ProposalCardResponse.ComponentView;
import com.buyilehu.musicagent.application.service.PackageVersionService;
import com.buyilehu.musicagent.application.service.ProposalCardService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ComponentDefinition;
import com.buyilehu.musicagent.domain.entity.ComponentInstance;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.LessonPlan;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.ProposalCard;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.ComponentDefinitionRepository;
import com.buyilehu.musicagent.infrastructure.repository.ComponentInstanceRepository;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.LessonPlanRepository;
import com.buyilehu.musicagent.infrastructure.repository.ProposalCardRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProposalCardServiceImpl implements ProposalCardService {
    private final InteractivePackageRepository interactivePackageRepository;
    private final ProposalCardRepository proposalCardRepository;
    private final PackageVersionService packageVersionService;
    private final ActivityNodeRepository activityNodeRepository;
    private final ComponentInstanceRepository componentInstanceRepository;
    private final ComponentDefinitionRepository componentDefinitionRepository;
    private final LessonPlanRepository lessonPlanRepository;
    private final UserRepository userRepository;
    private final ObjectMapper objectMapper;

    public ProposalCardServiceImpl(InteractivePackageRepository interactivePackageRepository,
                                   ProposalCardRepository proposalCardRepository,
                                   PackageVersionService packageVersionService,
                                   ActivityNodeRepository activityNodeRepository,
                                   ComponentInstanceRepository componentInstanceRepository,
                                   ComponentDefinitionRepository componentDefinitionRepository,
                                   LessonPlanRepository lessonPlanRepository,
                                   UserRepository userRepository,
                                   ObjectMapper objectMapper) {
        this.interactivePackageRepository = interactivePackageRepository;
        this.proposalCardRepository = proposalCardRepository;
        this.packageVersionService = packageVersionService;
        this.activityNodeRepository = activityNodeRepository;
        this.componentInstanceRepository = componentInstanceRepository;
        this.componentDefinitionRepository = componentDefinitionRepository;
        this.lessonPlanRepository = lessonPlanRepository;
        this.userRepository = userRepository;
        this.objectMapper = objectMapper;
    }

    @Override
    public ProposalCardResponse getProposal(Long packageId) {
        InteractivePackage pkg = getOwnedPackage(packageId);
        ProposalCard proposalCard = getLatestProposal(packageId);
        PackageVersion version = packageVersionService.getLatestVersion(packageId);
        return buildResponse(pkg, proposalCard, version);
    }

    @Override
    @Transactional
    public ProposalCardResponse confirmProposal(Long packageId) {
        InteractivePackage pkg = getOwnedPackage(packageId);
        ProposalCard proposalCard = getLatestProposal(packageId);
        PackageVersion version = packageVersionService.confirmLatestVersion(packageId);

        proposalCard.setConfirmStatus("confirmed");
        proposalCardRepository.save(proposalCard);

        pkg.setStatus("confirmed");
        pkg.setCurrentVersionId(version.getId());
        InteractivePackage savedPackage = interactivePackageRepository.save(pkg);

        return buildResponse(savedPackage, proposalCard, version);
    }

    private ProposalCardResponse buildResponse(InteractivePackage pkg, ProposalCard proposalCard, PackageVersion version) {
        ParsedLesson parsedLesson = getParsedLesson(pkg.getLessonPlanId());
        List<ActivityNode> nodes = activityNodeRepository.findByPackageIdOrderBySortOrderAsc(pkg.getId());
        List<ComponentInstance> componentInstances = findComponentInstances(nodes);
        Map<Long, ComponentDefinition> definitionMap = findDefinitionMap(componentInstances);
        Map<Long, List<ComponentView>> componentsByNode = new HashMap<>();
        List<ComponentView> allComponents = new ArrayList<>();

        for (ComponentInstance instance : componentInstances) {
            ComponentView componentView = toComponentView(instance, definitionMap.get(instance.getComponentDefinitionId()));
            allComponents.add(componentView);
            if (!componentsByNode.containsKey(instance.getActivityNodeId())) {
                componentsByNode.put(instance.getActivityNodeId(), new ArrayList<ComponentView>());
            }
            componentsByNode.get(instance.getActivityNodeId()).add(componentView);
        }

        ProposalCardResponse response = new ProposalCardResponse();
        response.setId(proposalCard.getId());
        response.setPackageId(pkg.getId());
        response.setGenerationJobId(proposalCard.getGenerationJobId());
        response.setVersionId(version.getId());
        response.setVersionNo(version.getVersionNo());
        response.setTitle(proposalCard.getTitle());
        response.setContent(proposalCard.getContent());
        response.setStatus(proposalCard.getStatus());
        response.setConfirmStatus(proposalCard.getConfirmStatus());
        response.setPackageInfo(PackageResponse.from(pkg));
        response.setTeachingObjectives(nonNullList(parsedLesson.getObjectives()));
        response.setSourceLessonSections(buildSourceSections(parsedLesson));
        response.setComponents(allComponents);

        List<ActivityNodeView> nodeViews = new ArrayList<>();
        for (ActivityNode node : nodes) {
            ActivityNodeView nodeView = new ActivityNodeView();
            nodeView.setId(node.getId());
            nodeView.setTitle(node.getTitle());
            nodeView.setNodeType(node.getNodeType());
            nodeView.setSortOrder(node.getSortOrder());
            nodeView.setConfigJson(node.getConfigJson());
            List<ComponentView> nodeComponents = componentsByNode.get(node.getId());
            nodeView.setComponents(nodeComponents == null ? new ArrayList<ComponentView>() : nodeComponents);
            nodeViews.add(nodeView);
        }
        response.setActivityNodes(nodeViews);
        return response;
    }

    private List<ComponentInstance> findComponentInstances(List<ActivityNode> nodes) {
        List<Long> nodeIds = new ArrayList<>();
        for (ActivityNode node : nodes) {
            nodeIds.add(node.getId());
        }
        if (nodeIds.isEmpty()) {
            return new ArrayList<>();
        }
        return componentInstanceRepository.findByActivityNodeIdIn(nodeIds);
    }

    private Map<Long, ComponentDefinition> findDefinitionMap(List<ComponentInstance> componentInstances) {
        List<Long> definitionIds = new ArrayList<>();
        for (ComponentInstance instance : componentInstances) {
            if (!definitionIds.contains(instance.getComponentDefinitionId())) {
                definitionIds.add(instance.getComponentDefinitionId());
            }
        }
        Map<Long, ComponentDefinition> map = new HashMap<>();
        if (definitionIds.isEmpty()) {
            return map;
        }
        Iterable<ComponentDefinition> definitions = componentDefinitionRepository.findAllById(definitionIds);
        for (ComponentDefinition definition : definitions) {
            map.put(definition.getId(), definition);
        }
        return map;
    }

    private ComponentView toComponentView(ComponentInstance instance, ComponentDefinition definition) {
        ComponentView view = new ComponentView();
        view.setId(instance.getId());
        view.setActivityNodeId(instance.getActivityNodeId());
        view.setComponentDefinitionId(instance.getComponentDefinitionId());
        view.setInstanceName(instance.getInstanceName());
        view.setSortOrder(instance.getSortOrder());
        view.setPropsJson(instance.getPropsJson());
        if (definition != null) {
            view.setComponentKey(definition.getComponentKey());
            view.setName(definition.getName());
            view.setCategory(definition.getCategory());
        }
        return view;
    }

    private List<String> buildSourceSections(ParsedLesson parsedLesson) {
        List<String> sections = new ArrayList<>();
        sections.addAll(nonNullList(parsedLesson.getProcess()));
        if (sections.isEmpty()) {
            sections.addAll(nonNullList(parsedLesson.getKeyPoints()));
        }
        if (sections.isEmpty() && parsedLesson.getCourseName() != null) {
            sections.add(parsedLesson.getCourseName());
        }
        return sections;
    }

    private List<String> nonNullList(List<String> values) {
        return values == null ? new ArrayList<String>() : values;
    }

    private ParsedLesson getParsedLesson(Long lessonPlanId) {
        if (lessonPlanId == null) {
            return ParsedLesson.fallback();
        }
        LessonPlan lessonPlan = lessonPlanRepository.findById(lessonPlanId).orElse(null);
        if (lessonPlan == null || lessonPlan.getParsedJson() == null || lessonPlan.getParsedJson().trim().isEmpty()) {
            return ParsedLesson.fallback();
        }
        try {
            return objectMapper.readValue(lessonPlan.getParsedJson(), ParsedLesson.class);
        } catch (Exception exception) {
            return ParsedLesson.fallback();
        }
    }

    private InteractivePackage getOwnedPackage(Long packageId) {
        User currentUser = getCurrentTeacher();
        InteractivePackage pkg = interactivePackageRepository.findById(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package not found"));
        if (!currentUser.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "package access denied");
        }
        return pkg;
    }

    private ProposalCard getLatestProposal(Long packageId) {
        return proposalCardRepository.findFirstByPackageIdOrderByIdDesc(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "proposal card not found"));
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
