package com.buyilehu.musicagent.application.dto.response;

import java.util.ArrayList;
import java.util.List;

public class ProposalCardResponse {
    private Long id;
    private Long packageId;
    private Long generationJobId;
    private Long versionId;
    private Integer versionNo;
    private String title;
    private String content;
    private String status;
    private String confirmStatus;
    private PackageResponse packageInfo;
    private List<String> teachingObjectives = new ArrayList<>();
    private List<String> sourceLessonSections = new ArrayList<>();
    private List<ActivityNodeView> activityNodes = new ArrayList<>();
    private List<ComponentView> components = new ArrayList<>();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getGenerationJobId() { return generationJobId; }
    public void setGenerationJobId(Long generationJobId) { this.generationJobId = generationJobId; }
    public Long getVersionId() { return versionId; }
    public void setVersionId(Long versionId) { this.versionId = versionId; }
    public Integer getVersionNo() { return versionNo; }
    public void setVersionNo(Integer versionNo) { this.versionNo = versionNo; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getConfirmStatus() { return confirmStatus; }
    public void setConfirmStatus(String confirmStatus) { this.confirmStatus = confirmStatus; }
    public PackageResponse getPackageInfo() { return packageInfo; }
    public void setPackageInfo(PackageResponse packageInfo) { this.packageInfo = packageInfo; }
    public List<String> getTeachingObjectives() { return teachingObjectives; }
    public void setTeachingObjectives(List<String> teachingObjectives) { this.teachingObjectives = teachingObjectives; }
    public List<String> getSourceLessonSections() { return sourceLessonSections; }
    public void setSourceLessonSections(List<String> sourceLessonSections) { this.sourceLessonSections = sourceLessonSections; }
    public List<ActivityNodeView> getActivityNodes() { return activityNodes; }
    public void setActivityNodes(List<ActivityNodeView> activityNodes) { this.activityNodes = activityNodes; }
    public List<ComponentView> getComponents() { return components; }
    public void setComponents(List<ComponentView> components) { this.components = components; }

    public static class ActivityNodeView {
        private Long id;
        private String title;
        private String nodeType;
        private Integer sortOrder;
        private String configJson;
        private List<ComponentView> components = new ArrayList<>();

        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getNodeType() { return nodeType; }
        public void setNodeType(String nodeType) { this.nodeType = nodeType; }
        public Integer getSortOrder() { return sortOrder; }
        public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
        public String getConfigJson() { return configJson; }
        public void setConfigJson(String configJson) { this.configJson = configJson; }
        public List<ComponentView> getComponents() { return components; }
        public void setComponents(List<ComponentView> components) { this.components = components; }
    }

    public static class ComponentView {
        private Long id;
        private Long activityNodeId;
        private Long componentDefinitionId;
        private String componentKey;
        private String name;
        private String category;
        private String instanceName;
        private Integer sortOrder;
        private String propsJson;

        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        public Long getActivityNodeId() { return activityNodeId; }
        public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
        public Long getComponentDefinitionId() { return componentDefinitionId; }
        public void setComponentDefinitionId(Long componentDefinitionId) { this.componentDefinitionId = componentDefinitionId; }
        public String getComponentKey() { return componentKey; }
        public void setComponentKey(String componentKey) { this.componentKey = componentKey; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        public String getInstanceName() { return instanceName; }
        public void setInstanceName(String instanceName) { this.instanceName = instanceName; }
        public Integer getSortOrder() { return sortOrder; }
        public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
        public String getPropsJson() { return propsJson; }
        public void setPropsJson(String propsJson) { this.propsJson = propsJson; }
    }
}
