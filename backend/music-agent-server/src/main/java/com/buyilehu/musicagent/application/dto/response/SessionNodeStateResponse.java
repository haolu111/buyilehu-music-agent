package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import java.time.LocalDateTime;

public class SessionNodeStateResponse {
    private Long id;
    private Long sessionId;
    private Long activityNodeId;
    private String title;
    private String nodeType;
    private Integer sortOrder;
    private String status;
    private LocalDateTime unlockedAt;

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
        }
        return response;
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
}
