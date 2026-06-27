package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.GenerationJob;

public class GenerationJobResponse {
    private final Long id;
    private final Long lessonPlanId;
    private final Long packageId;
    private final Long versionId;
    private final String status;
    private final Integer progress;
    private final String errorMessage;

    public GenerationJobResponse(Long id, Long lessonPlanId, Long packageId, Long versionId,
                                 String status, Integer progress, String errorMessage) {
        this.id = id;
        this.lessonPlanId = lessonPlanId;
        this.packageId = packageId;
        this.versionId = versionId;
        this.status = status;
        this.progress = progress;
        this.errorMessage = errorMessage;
    }

    public static GenerationJobResponse from(GenerationJob job, Long packageId, Long versionId) {
        return new GenerationJobResponse(
                job.getId(),
                job.getLessonPlanId(),
                packageId,
                versionId,
                job.getStatus(),
                job.getProgress(),
                job.getErrorMessage());
    }

    public Long getId() { return id; }
    public Long getLessonPlanId() { return lessonPlanId; }
    public Long getPackageId() { return packageId; }
    public Long getVersionId() { return versionId; }
    public String getStatus() { return status; }
    public Integer getProgress() { return progress; }
    public String getErrorMessage() { return errorMessage; }
}
