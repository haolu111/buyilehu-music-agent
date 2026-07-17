package com.buyilehu.musicagent.application.dto.request;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import javax.validation.constraints.Positive;

public class PublishPackageRequest {
    @Positive
    private Long versionId;

    @Positive
    private Long classId;

    private List<@Positive Long> classIds = new ArrayList<>();

    private String courseTitle;

    private String courseDescription;

    private LocalDateTime scheduledStartAt;

    private Boolean startImmediately = false;

    private Boolean reviewEnabled = false;

    public Long getVersionId() { return versionId; }
    public void setVersionId(Long versionId) { this.versionId = versionId; }
    public Long getClassId() { return classId; }
    public void setClassId(Long classId) { this.classId = classId; }
    public List<Long> getClassIds() { return classIds; }
    public void setClassIds(List<Long> classIds) { this.classIds = classIds; }
    public String getCourseTitle() { return courseTitle; }
    public void setCourseTitle(String courseTitle) { this.courseTitle = courseTitle; }
    public String getCourseDescription() { return courseDescription; }
    public void setCourseDescription(String courseDescription) { this.courseDescription = courseDescription; }
    public LocalDateTime getScheduledStartAt() { return scheduledStartAt; }
    public void setScheduledStartAt(LocalDateTime scheduledStartAt) { this.scheduledStartAt = scheduledStartAt; }
    public Boolean getStartImmediately() { return startImmediately; }
    public void setStartImmediately(Boolean startImmediately) { this.startImmediately = startImmediately; }
    public Boolean getReviewEnabled() { return reviewEnabled; }
    public void setReviewEnabled(Boolean reviewEnabled) { this.reviewEnabled = reviewEnabled; }
}
