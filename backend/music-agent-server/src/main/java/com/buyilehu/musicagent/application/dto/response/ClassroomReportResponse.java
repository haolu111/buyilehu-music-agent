package com.buyilehu.musicagent.application.dto.response;

import java.util.ArrayList;
import java.util.List;

public class ClassroomReportResponse {
    private Long sessionId;
    private Long classId;
    private Long packageId;
    private Integer totalStudentCount;
    private Integer enteredStudentCount;
    private Integer completedStudentCount;
    private Double averageScore;
    private Double averageDurationSeconds;
    private List<NodeCompletionReport> nodeReports = new ArrayList<>();
    private List<StudentCompletionReport> studentReports = new ArrayList<>();

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public Long getClassId() { return classId; }
    public void setClassId(Long classId) { this.classId = classId; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Integer getTotalStudentCount() { return totalStudentCount; }
    public void setTotalStudentCount(Integer totalStudentCount) { this.totalStudentCount = totalStudentCount; }
    public Integer getEnteredStudentCount() { return enteredStudentCount; }
    public void setEnteredStudentCount(Integer enteredStudentCount) { this.enteredStudentCount = enteredStudentCount; }
    public Integer getCompletedStudentCount() { return completedStudentCount; }
    public void setCompletedStudentCount(Integer completedStudentCount) { this.completedStudentCount = completedStudentCount; }
    public Double getAverageScore() { return averageScore; }
    public void setAverageScore(Double averageScore) { this.averageScore = averageScore; }
    public Double getAverageDurationSeconds() { return averageDurationSeconds; }
    public void setAverageDurationSeconds(Double averageDurationSeconds) { this.averageDurationSeconds = averageDurationSeconds; }
    public List<NodeCompletionReport> getNodeReports() { return nodeReports; }
    public void setNodeReports(List<NodeCompletionReport> nodeReports) { this.nodeReports = nodeReports; }
    public List<StudentCompletionReport> getStudentReports() { return studentReports; }
    public void setStudentReports(List<StudentCompletionReport> studentReports) { this.studentReports = studentReports; }

    public static class NodeCompletionReport {
        private Long nodeId;
        private String title;
        private String nodeType;
        private Integer sortOrder;
        private Integer completedCount;
        private Double completionRate;

        public Long getNodeId() { return nodeId; }
        public void setNodeId(Long nodeId) { this.nodeId = nodeId; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getNodeType() { return nodeType; }
        public void setNodeType(String nodeType) { this.nodeType = nodeType; }
        public Integer getSortOrder() { return sortOrder; }
        public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
        public Integer getCompletedCount() { return completedCount; }
        public void setCompletedCount(Integer completedCount) { this.completedCount = completedCount; }
        public Double getCompletionRate() { return completionRate; }
        public void setCompletionRate(Double completionRate) { this.completionRate = completionRate; }
    }

    public static class StudentCompletionReport {
        private Long studentId;
        private String studentName;
        private Boolean entered;
        private Integer completedNodeCount;
        private Integer wrongCount;
        private Integer hintUsedCount;
        private Integer totalDurationSeconds;
        private Integer totalScore;
        private Double averageScore;
        private List<Long> completedNodeIds = new ArrayList<>();

        public Long getStudentId() { return studentId; }
        public void setStudentId(Long studentId) { this.studentId = studentId; }
        public String getStudentName() { return studentName; }
        public void setStudentName(String studentName) { this.studentName = studentName; }
        public Boolean getEntered() { return entered; }
        public void setEntered(Boolean entered) { this.entered = entered; }
        public Integer getCompletedNodeCount() { return completedNodeCount; }
        public void setCompletedNodeCount(Integer completedNodeCount) { this.completedNodeCount = completedNodeCount; }
        public Integer getWrongCount() { return wrongCount; }
        public void setWrongCount(Integer wrongCount) { this.wrongCount = wrongCount; }
        public Integer getHintUsedCount() { return hintUsedCount; }
        public void setHintUsedCount(Integer hintUsedCount) { this.hintUsedCount = hintUsedCount; }
        public Integer getTotalDurationSeconds() { return totalDurationSeconds; }
        public void setTotalDurationSeconds(Integer totalDurationSeconds) { this.totalDurationSeconds = totalDurationSeconds; }
        public Integer getTotalScore() { return totalScore; }
        public void setTotalScore(Integer totalScore) { this.totalScore = totalScore; }
        public Double getAverageScore() { return averageScore; }
        public void setAverageScore(Double averageScore) { this.averageScore = averageScore; }
        public List<Long> getCompletedNodeIds() { return completedNodeIds; }
        public void setCompletedNodeIds(List<Long> completedNodeIds) { this.completedNodeIds = completedNodeIds; }
    }
}