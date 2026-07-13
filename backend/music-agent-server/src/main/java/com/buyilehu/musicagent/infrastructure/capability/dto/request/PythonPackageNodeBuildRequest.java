package com.buyilehu.musicagent.infrastructure.capability.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.LinkedHashMap;
import java.util.Map;

public class PythonPackageNodeBuildRequest {
    @JsonProperty("client_ref")
    private String clientRef;
    @JsonProperty("activity_id")
    private String activityId;
    private Map<String, Object> composition = new LinkedHashMap<String, Object>();
    private Map<String, Object> request = new LinkedHashMap<String, Object>();

    public String getClientRef() { return clientRef; }
    public void setClientRef(String clientRef) { this.clientRef = clientRef; }
    public String getActivityId() { return activityId; }
    public void setActivityId(String activityId) { this.activityId = activityId; }
    public Map<String, Object> getComposition() { return composition; }
    public void setComposition(Map<String, Object> composition) { this.composition = composition; }
    public Map<String, Object> getRequest() { return request; }
    public void setRequest(Map<String, Object> request) { this.request = request; }
}
