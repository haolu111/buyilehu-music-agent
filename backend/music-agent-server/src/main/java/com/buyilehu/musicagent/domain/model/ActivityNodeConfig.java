package com.buyilehu.musicagent.domain.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.LinkedHashMap;
import java.util.ArrayList;
import java.util.Map;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class ActivityNodeConfig {
    private String title;
    private String nodeType;
    private Integer sortOrder;
    private List<String> componentKeys = new ArrayList<>();
    private String capabilityActivityId;
    private String capabilitySource;
    private Map<String, Object> toolkit = new LinkedHashMap<String, Object>();
    private Map<String, Object> runtime = new LinkedHashMap<String, Object>();
    private Map<String, Object> mediaSessionPreview;
    private String capabilityStatus;
    private Map<String, Object> capabilityError;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getNodeType() { return nodeType; }
    public void setNodeType(String nodeType) { this.nodeType = nodeType; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public List<String> getComponentKeys() { return componentKeys; }
    public void setComponentKeys(List<String> componentKeys) { this.componentKeys = componentKeys; }
    public String getCapabilityActivityId() { return capabilityActivityId; }
    public void setCapabilityActivityId(String capabilityActivityId) { this.capabilityActivityId = capabilityActivityId; }
    public String getCapabilitySource() { return capabilitySource; }
    public void setCapabilitySource(String capabilitySource) { this.capabilitySource = capabilitySource; }
    public Map<String, Object> getToolkit() { return toolkit; }
    public void setToolkit(Map<String, Object> toolkit) { this.toolkit = toolkit; }
    public Map<String, Object> getRuntime() { return runtime; }
    public void setRuntime(Map<String, Object> runtime) { this.runtime = runtime; }
    public Map<String, Object> getMediaSessionPreview() { return mediaSessionPreview; }
    public void setMediaSessionPreview(Map<String, Object> mediaSessionPreview) { this.mediaSessionPreview = mediaSessionPreview; }
    public String getCapabilityStatus() { return capabilityStatus; }
    public void setCapabilityStatus(String capabilityStatus) { this.capabilityStatus = capabilityStatus; }
    public Map<String, Object> getCapabilityError() { return capabilityError; }
    public void setCapabilityError(Map<String, Object> capabilityError) { this.capabilityError = capabilityError; }
}
