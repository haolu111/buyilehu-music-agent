package com.buyilehu.musicagent.domain.entity;

import java.time.LocalDateTime;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "session_node_states")
public class SessionNodeState extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false)
    private Long sessionId;

    @Column(name = "activity_node_id", nullable = false)
    private Long activityNodeId;

    @Column(nullable = false, length = 30)
    private String status = "locked";

    @Column(name = "state_json", columnDefinition = "TEXT")
    private String stateJson;

    @Column(name = "unlocked_at")
    private LocalDateTime unlockedAt;

    public SessionNodeState() {
    }

    public Long getId() { return id; }
    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getActivityNodeId() { return activityNodeId; }
    public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getStateJson() { return stateJson; }
    public void setStateJson(String stateJson) { this.stateJson = stateJson; }
    public LocalDateTime getUnlockedAt() { return unlockedAt; }
    public void setUnlockedAt(LocalDateTime unlockedAt) { this.unlockedAt = unlockedAt; }
}
