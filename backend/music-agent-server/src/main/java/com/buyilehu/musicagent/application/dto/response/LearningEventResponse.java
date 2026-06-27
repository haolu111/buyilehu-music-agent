package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.LearningEvent;
import java.time.LocalDateTime;

public class LearningEventResponse {
    private Long id;
    private Long sessionId;
    private Long studentId;
    private Long activityNodeId;
    private String eventType;
    private String eventData;
    private LocalDateTime occurredAt;

    public static LearningEventResponse from(LearningEvent event) {
        LearningEventResponse response = new LearningEventResponse();
        response.setId(event.getId());
        response.setSessionId(event.getSessionId());
        response.setStudentId(event.getStudentId());
        response.setActivityNodeId(event.getActivityNodeId());
        response.setEventType(event.getEventType());
        response.setEventData(event.getEventData());
        response.setOccurredAt(event.getOccurredAt());
        return response;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getStudentId() { return studentId; }
    public void setStudentId(Long studentId) { this.studentId = studentId; }
    public Long getActivityNodeId() { return activityNodeId; }
    public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public String getEventData() { return eventData; }
    public void setEventData(String eventData) { this.eventData = eventData; }
    public LocalDateTime getOccurredAt() { return occurredAt; }
    public void setOccurredAt(LocalDateTime occurredAt) { this.occurredAt = occurredAt; }
}
