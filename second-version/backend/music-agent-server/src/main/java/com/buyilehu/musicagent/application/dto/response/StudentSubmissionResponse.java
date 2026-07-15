package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.StudentProgress;
import com.buyilehu.musicagent.domain.entity.User;
import java.time.LocalDateTime;

public class StudentSubmissionResponse {
    private Long progressId;
    private Long sessionId;
    private Long studentId;
    private String studentName;
    private Long nodeId;
    private String nodeTitle;
    private Integer sortOrder;
    private String progressStatus;
    private Integer progress;
    private Integer score;
    private Integer wrongCount;
    private Integer hintUsedCount;
    private Integer durationSeconds;
    private String resultJson;
    private LocalDateTime lastActiveAt;

    public static StudentSubmissionResponse from(StudentProgress progress, User student, ActivityNode node) {
        StudentSubmissionResponse response = new StudentSubmissionResponse();
        response.setProgressId(progress.getId());
        response.setSessionId(progress.getSessionId());
        response.setStudentId(progress.getStudentId());
        response.setNodeId(progress.getCurrentNodeId());
        response.setProgressStatus(progress.getProgressStatus());
        response.setProgress(progress.getProgress());
        response.setScore(progress.getScore());
        response.setWrongCount(progress.getWrongCount());
        response.setHintUsedCount(progress.getHintUsedCount());
        response.setDurationSeconds(progress.getDurationSeconds());
        response.setResultJson(progress.getResultJson());
        response.setLastActiveAt(progress.getLastActiveAt());
        if (student != null) {
            response.setStudentName(student.getRealName() != null ? student.getRealName() : student.getUsername());
        }
        if (node != null) {
            response.setNodeTitle(node.getTitle());
            response.setSortOrder(node.getSortOrder());
        }
        return response;
    }

    public Long getProgressId() { return progressId; }
    public void setProgressId(Long progressId) { this.progressId = progressId; }
    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getStudentId() { return studentId; }
    public void setStudentId(Long studentId) { this.studentId = studentId; }
    public String getStudentName() { return studentName; }
    public void setStudentName(String studentName) { this.studentName = studentName; }
    public Long getNodeId() { return nodeId; }
    public void setNodeId(Long nodeId) { this.nodeId = nodeId; }
    public String getNodeTitle() { return nodeTitle; }
    public void setNodeTitle(String nodeTitle) { this.nodeTitle = nodeTitle; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public String getProgressStatus() { return progressStatus; }
    public void setProgressStatus(String progressStatus) { this.progressStatus = progressStatus; }
    public Integer getProgress() { return progress; }
    public void setProgress(Integer progress) { this.progress = progress; }
    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }
    public Integer getWrongCount() { return wrongCount; }
    public void setWrongCount(Integer wrongCount) { this.wrongCount = wrongCount; }
    public Integer getHintUsedCount() { return hintUsedCount; }
    public void setHintUsedCount(Integer hintUsedCount) { this.hintUsedCount = hintUsedCount; }
    public Integer getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(Integer durationSeconds) { this.durationSeconds = durationSeconds; }
    public String getResultJson() { return resultJson; }
    public void setResultJson(String resultJson) { this.resultJson = resultJson; }
    public LocalDateTime getLastActiveAt() { return lastActiveAt; }
    public void setLastActiveAt(LocalDateTime lastActiveAt) { this.lastActiveAt = lastActiveAt; }
}