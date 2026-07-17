package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.GenerationJob;
import com.buyilehu.musicagent.domain.model.ActivityChain;

public class GenerationJobResponse {
    private final Long id;
    private final Long lessonPlanId;
    private final Long packageId;
    private final Long versionId;
    private final String status;
    private final Integer progress;
    private final String phase;
    private final String message;
    private final String errorMessage;
    private final String designProvider;
    private final String designModel;
    private final String designFallbackReason;
    private final String designTraceId;

    public GenerationJobResponse(Long id, Long lessonPlanId, Long packageId, Long versionId,
                                 String status, Integer progress, String errorMessage) {
        this(id, lessonPlanId, packageId, versionId, status, progress, errorMessage,
                null, null, null, null, null, null);
    }

    public GenerationJobResponse(Long id, Long lessonPlanId, Long packageId, Long versionId,
                                 String status, Integer progress, String errorMessage,
                                 String designProvider, String designModel,
                                 String designFallbackReason, String designTraceId,
                                 String phase, String message) {
        this.id = id;
        this.lessonPlanId = lessonPlanId;
        this.packageId = packageId;
        this.versionId = versionId;
        this.status = status;
        this.progress = progress;
        this.phase = phase;
        this.message = message;
        this.errorMessage = errorMessage;
        this.designProvider = designProvider;
        this.designModel = designModel;
        this.designFallbackReason = designFallbackReason;
        this.designTraceId = designTraceId;
    }

    public static GenerationJobResponse from(GenerationJob job, Long packageId, Long versionId,
                                             ActivityChain chain) {
        return new GenerationJobResponse(job.getId(), job.getLessonPlanId(), packageId, versionId,
                job.getStatus(), job.getProgress(), job.getErrorMessage(),
                chain.getDesignProvider(), chain.getDesignModel(),
                chain.getDesignFallbackReason(), chain.getDesignTraceId(),
                "completed", "活动包与教学质量报告已生成");
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

    public static GenerationJobResponse progress(GenerationJob job, String phase, String message) {
        return new GenerationJobResponse(
                job.getId(), job.getLessonPlanId(), null, null,
                job.getStatus(), job.getProgress(), job.getErrorMessage(),
                null, null, null, null, phase, message);
    }

    public Long getId() { return id; }
    public Long getLessonPlanId() { return lessonPlanId; }
    public Long getPackageId() { return packageId; }
    public Long getVersionId() { return versionId; }
    public String getStatus() { return status; }
    public Integer getProgress() { return progress; }
    public String getPhase() { return phase; }
    public String getMessage() { return message; }
    public String getErrorMessage() { return errorMessage; }
    public String getDesignProvider() { return designProvider; }
    public String getDesignModel() { return designModel; }
    public String getDesignFallbackReason() { return designFallbackReason; }
    public String getDesignTraceId() { return designTraceId; }
}
