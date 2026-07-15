package com.buyilehu.musicagent.application.dto.response;

import java.time.LocalDateTime;

public class GenerationJobStatus {
    private Long id;
    private Long lessonPlanId;
    private Long packageId;
    private Long versionId;
    private String status;
    private String phase;
    private Integer progress;
    private String message;
    private String errorMessage;
    private String designProvider;
    private String designModel;
    private String designFallbackReason;
    private String designTraceId;
    private LocalDateTime updatedAt;

    public GenerationJobStatus() {
    }

    public boolean isTerminal() {
        return "success".equals(status) || "failed".equals(status);
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getLessonPlanId() { return lessonPlanId; }
    public void setLessonPlanId(Long lessonPlanId) { this.lessonPlanId = lessonPlanId; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getVersionId() { return versionId; }
    public void setVersionId(Long versionId) { this.versionId = versionId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getPhase() { return phase; }
    public void setPhase(String phase) { this.phase = phase; }
    public Integer getProgress() { return progress; }
    public void setProgress(Integer progress) { this.progress = progress; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    public String getDesignProvider() { return designProvider; }
    public void setDesignProvider(String designProvider) { this.designProvider = designProvider; }
    public String getDesignModel() { return designModel; }
    public void setDesignModel(String designModel) { this.designModel = designModel; }
    public String getDesignFallbackReason() { return designFallbackReason; }
    public void setDesignFallbackReason(String designFallbackReason) { this.designFallbackReason = designFallbackReason; }
    public String getDesignTraceId() { return designTraceId; }
    public void setDesignTraceId(String designTraceId) { this.designTraceId = designTraceId; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
