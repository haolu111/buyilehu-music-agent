package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;

public class PythonPackageDesignStep {
    @JsonProperty("activity_id")
    private String activityId;
    private String title;
    @JsonProperty("node_type")
    private String nodeType;
    @JsonProperty("sort_order")
    private Integer sortOrder;
    @JsonProperty("component_keys")
    private List<String> componentKeys = new ArrayList<String>();
    @JsonProperty("recommendation_reason")
    private String recommendationReason;
    @JsonProperty("music_content")
    private Map<String, Object> musicContent = new LinkedHashMap<String, Object>();
    @JsonProperty("resolved_music_content")
    private Map<String, Object> resolvedMusicContent = new LinkedHashMap<String, Object>();

    public String getActivityId() { return activityId; }
    public void setActivityId(String activityId) { this.activityId = activityId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
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
