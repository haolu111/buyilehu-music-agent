package com.buyilehu.musicagent.application.dto.request;

import java.time.LocalDateTime;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

public class CreateClassroomSessionRequest {
    @NotNull
    @Positive
    private Long publicationId;

    private String courseTitle;

    private String courseDescription;

    private LocalDateTime scheduledStartAt;

    private Boolean startImmediately = false;

    public Long getPublicationId() { return publicationId; }
    public void setPublicationId(Long publicationId) { this.publicationId = publicationId; }
    public String getCourseTitle() { return courseTitle; }
    public void setCourseTitle(String courseTitle) { this.courseTitle = courseTitle; }
    public String getCourseDescription() { return courseDescription; }
    public void setCourseDescription(String courseDescription) { this.courseDescription = courseDescription; }
    public LocalDateTime getScheduledStartAt() { return scheduledStartAt; }
    public void setScheduledStartAt(LocalDateTime scheduledStartAt) { this.scheduledStartAt = scheduledStartAt; }
    public Boolean getStartImmediately() { return startImmediately; }
    public void setStartImmediately(Boolean startImmediately) { this.startImmediately = startImmediately; }
}