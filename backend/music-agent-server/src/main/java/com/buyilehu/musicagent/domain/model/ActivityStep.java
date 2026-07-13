package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;

public class ActivityStep {
    private String title;
    private String activityId;
    private String nodeType;
    private Integer sortOrder;
    private List<String> componentKeys = new ArrayList<>();

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
}
