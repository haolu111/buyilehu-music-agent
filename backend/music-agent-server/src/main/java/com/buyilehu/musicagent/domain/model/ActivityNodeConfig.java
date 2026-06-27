package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;

public class ActivityNodeConfig {
    private String title;
    private String nodeType;
    private Integer sortOrder;
    private List<String> componentKeys = new ArrayList<>();

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getNodeType() { return nodeType; }
    public void setNodeType(String nodeType) { this.nodeType = nodeType; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public List<String> getComponentKeys() { return componentKeys; }
    public void setComponentKeys(List<String> componentKeys) { this.componentKeys = componentKeys; }
}
