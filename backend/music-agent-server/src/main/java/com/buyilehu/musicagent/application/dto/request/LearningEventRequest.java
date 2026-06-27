package com.buyilehu.musicagent.application.dto.request;

import java.util.HashMap;
import java.util.Map;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

public class LearningEventRequest {
    @NotNull
    @Positive
    private Long sessionId;
    @Positive
    private Long activityNodeId;
    @NotBlank
    private String eventType;
    private Map<String, Object> eventData = new HashMap<>();

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getActivityNodeId() { return activityNodeId; }
    public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public Map<String, Object> getEventData() { return eventData; }
    public void setEventData(Map<String, Object> eventData) { this.eventData = eventData; }
}
