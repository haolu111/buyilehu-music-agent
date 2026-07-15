package com.buyilehu.musicagent.application.dto.request;

import java.util.HashMap;
import java.util.Map;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

/**
 * 应用层的请求 DTO
 * 学生端向后端上报学习行为数据时用的请求对象
 */

public class LearningEventRequest {
    @NotNull
    @Positive
    private Long sessionId;//这次课堂学习会话的 ID
    @Positive
    private Long activityNodeId;//表示学生当前操作的是哪个活动节点
    @NotBlank
    private String eventType;//事件类型，也就是学生做了什么
    private Map<String, Object> eventData = new HashMap<>(); //事件的详细数据

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getActivityNodeId() { return activityNodeId; }
    public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public Map<String, Object> getEventData() { return eventData; }
    public void setEventData(Map<String, Object> eventData) { this.eventData = eventData; }
}
