package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ClassroomSession;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class ClassroomSessionResponse {
    private Long id;
    private Long publicationId;
    private Long classId;
    private Long packageId;
    private Long teacherId;
    private Long currentNodeId;
    private String status;
    private LocalDateTime startedAt;
    private LocalDateTime endedAt;
    private List<SessionNodeStateResponse> nodeStates = new ArrayList<>();

    public static ClassroomSessionResponse from(ClassroomSession session, List<SessionNodeStateResponse> nodeStates) {
        ClassroomSessionResponse response = new ClassroomSessionResponse();
        response.setId(session.getId());
        response.setPublicationId(session.getPublicationId());
        response.setClassId(session.getClassId());
        response.setPackageId(session.getPackageId());
        response.setTeacherId(session.getTeacherId());
        response.setCurrentNodeId(session.getCurrentNodeId());
        response.setStatus(session.getStatus());
        response.setStartedAt(session.getStartedAt());
        response.setEndedAt(session.getEndedAt());
        response.setNodeStates(nodeStates);
        return response;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPublicationId() { return publicationId; }
    public void setPublicationId(Long publicationId) { this.publicationId = publicationId; }
    public Long getClassId() { return classId; }
    public void setClassId(Long classId) { this.classId = classId; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getTeacherId() { return teacherId; }
    public void setTeacherId(Long teacherId) { this.teacherId = teacherId; }
    public Long getCurrentNodeId() { return currentNodeId; }
    public void setCurrentNodeId(Long currentNodeId) { this.currentNodeId = currentNodeId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getStartedAt() { return startedAt; }
    public void setStartedAt(LocalDateTime startedAt) { this.startedAt = startedAt; }
    public LocalDateTime getEndedAt() { return endedAt; }
    public void setEndedAt(LocalDateTime endedAt) { this.endedAt = endedAt; }
    public List<SessionNodeStateResponse> getNodeStates() { return nodeStates; }
    public void setNodeStates(List<SessionNodeStateResponse> nodeStates) { this.nodeStates = nodeStates; }
}
