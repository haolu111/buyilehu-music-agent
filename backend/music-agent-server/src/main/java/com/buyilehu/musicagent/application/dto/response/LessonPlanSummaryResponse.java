package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.LessonPlan;
import java.time.LocalDateTime;

public class LessonPlanSummaryResponse {
    private final Long id;
    private final Long teacherId;
    private final String title;
    private final String parseStatus;
    private final String status;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    public LessonPlanSummaryResponse(Long id, Long teacherId, String title, String parseStatus,
                                     String status, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.teacherId = teacherId;
        this.title = title;
        this.parseStatus = parseStatus;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public static LessonPlanSummaryResponse from(LessonPlan lessonPlan) {
        return new LessonPlanSummaryResponse(
                lessonPlan.getId(),
                lessonPlan.getTeacherId(),
                lessonPlan.getTitle(),
                lessonPlan.getParseStatus(),
                lessonPlan.getStatus(),
                lessonPlan.getCreatedAt(),
                lessonPlan.getUpdatedAt());
    }

    public Long getId() { return id; }
    public Long getTeacherId() { return teacherId; }
    public String getTitle() { return title; }
    public String getParseStatus() { return parseStatus; }
    public String getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
