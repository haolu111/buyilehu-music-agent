package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import java.time.LocalDateTime;
import java.util.Map;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class SessionNodeStateResponse {
    private Long id;
    private Long sessionId;
    private Long activityNodeId;
    private String title;
    private String nodeType;
    private Integer sortOrder;
    private String status;
    private LocalDateTime unlockedAt;
    private Map<String, Object> runtimeConfig;

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    public static SessionNodeStateResponse from(SessionNodeState state, ActivityNode node) {
        SessionNodeStateResponse response = new SessionNodeStateResponse();
        response.setId(state.getId());
        response.setSessionId(state.getSessionId());
        response.setActivityNodeId(state.getActivityNodeId());
        response.setStatus(state.getStatus());
        response.setUnlockedAt(state.getUnlockedAt());
        if (node != null) {
            response.setTitle(node.getTitle());
            response.setNodeType(node.getNodeType());
            response.setSortOrder(node.getSortOrder());
            response.setRuntimeConfig(extractRuntimeConfig(node.getConfigJson()));
        }
        return response;
    }

    private static Map<String, Object> extractRuntimeConfig(String configJson) {
        if (configJson == null || configJson.trim().isEmpty()) return null;
        try {
            Map<String, Object> config = OBJECT_MAPPER.readValue(configJson, new TypeReference<Map<String, Object>>() {});
            Object runtime = config.get("activityRuntime");
            if (!(runtime instanceof Map)) return null;
            @SuppressWarnings("unchecked")
            Map<String, Object> result = (Map<String, Object>) runtime;
            return "activity-runtime.v1".equals(result.get("schemaVersion")) ? result : null;
        } catch (Exception ignored) {
            return null;
        }
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getActivityNodeId() { return activityNodeId; }
    public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getNodeType() { return nodeType; }
    public void setNodeType(String nodeType) { this.nodeType = nodeType; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getUnlockedAt() { return unlockedAt; }
    public void setUnlockedAt(LocalDateTime unlockedAt) { this.unlockedAt = unlockedAt; }
    public Map<String, Object> getRuntimeConfig() { return runtimeConfig; }
    public void setRuntimeConfig(Map<String, Object> runtimeConfig) { this.runtimeConfig = runtimeConfig; }
}
