package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;

public class ActivityStep {
    private String title;
    private String activityId;
    private String nodeType;
    private Integer sortOrder;
    private List<String> componentKeys = new ArrayList<>();
    private String recommendationReason;
    private Map<String, Object> musicContent = new LinkedHashMap<>();
    private Map<String, Object> resolvedMusicContent = new LinkedHashMap<>();

    public ActivityStep() {
    }

    public ActivityStep(String title, String nodeType, Integer sortOrder, List<String> componentKeys) {
        this.title = title;
        this.nodeType = nodeType;
        this.sortOrder = sortOrder;
        this.componentKeys = componentKeys;
    }

    public ActivityStep(String title, String activityId, String nodeType, Integer sortOrder, List<String> componentKeys) {
        this(title, nodeType, sortOrder, componentKeys);
        this.activityId = activityId;
    }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getActivityId() { return activityId; }
    public void setActivityId(String activityId) { this.activityId = activityId; }
    public String getNodeType() { return nodeType; }
    public void setNodeType(String nodeType) { this.nodeType = nodeType; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public List<String> getComponentKeys() { return componentKeys; }
    public void setComponentKeys(List<String> componentKeys) { this.componentKeys = componentKeys; }
    public String getRecommendationReason() { return recommendationReason; }
    public void setRecommendationReason(String recommendationReason) { this.recommendationReason = recommendationReason; }
    public Map<String, Object> getMusicContent() { return musicContent; }
    public void setMusicContent(Map<String, Object> musicContent) { this.musicContent = musicContent; }
    public Map<String, Object> getResolvedMusicContent() { return resolvedMusicContent; }
    public void setResolvedMusicContent(Map<String, Object> resolvedMusicContent) { this.resolvedMusicContent = resolvedMusicContent; }
}
