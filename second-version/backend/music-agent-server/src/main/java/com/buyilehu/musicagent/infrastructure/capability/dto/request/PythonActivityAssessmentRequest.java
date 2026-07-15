package com.buyilehu.musicagent.infrastructure.capability.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.LinkedHashMap;
import java.util.Map;

public class PythonActivityAssessmentRequest {
    @JsonProperty("activity_id")
    private String activityId;
    private String renderer;
    private String title;
    private Map<String, Object> result = new LinkedHashMap<>();
    private Map<String, Object> assessment = new LinkedHashMap<>();

    public String getActivityId() { return activityId; }
    public void setActivityId(String activityId) { this.activityId = activityId; }
    public String getRenderer() { return renderer; }
    public void setRenderer(String renderer) { this.renderer = renderer; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public Map<String, Object> getResult() { return result; }
    public void setResult(Map<String, Object> result) { this.result = result; }
    public Map<String, Object> getAssessment() { return assessment; }
    public void setAssessment(Map<String, Object> assessment) { this.assessment = assessment; }
}
