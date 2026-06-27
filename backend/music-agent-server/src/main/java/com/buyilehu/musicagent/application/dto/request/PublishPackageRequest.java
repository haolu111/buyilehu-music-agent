package com.buyilehu.musicagent.application.dto.request;

import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

public class PublishPackageRequest {
    @NotNull
    @Positive
    private Long versionId;

    @NotNull
    @Positive
    private Long classId;

    private Boolean reviewEnabled = false;

    public Long getVersionId() {
        return versionId;
    }

    public void setVersionId(Long versionId) {
        this.versionId = versionId;
    }

    public Long getClassId() {
        return classId;
    }

    public void setClassId(Long classId) {
        this.classId = classId;
    }

    public Boolean getReviewEnabled() {
        return reviewEnabled;
    }

    public void setReviewEnabled(Boolean reviewEnabled) {
        this.reviewEnabled = reviewEnabled;
    }
}
