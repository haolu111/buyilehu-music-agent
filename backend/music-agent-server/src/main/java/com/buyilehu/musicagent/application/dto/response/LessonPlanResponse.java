package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.LessonPlan;

public class LessonPlanResponse {
    private final Long id;
    private final Long teacherId;
    private final String title;
    private final String sourceFileUrl;
    private final String rawText;
    private final String parsedJson;
    private final String parseStatus;
    private final String status;

    public LessonPlanResponse(Long id, Long teacherId, String title, String sourceFileUrl,
                              String rawText, String parsedJson, String parseStatus, String status) {
        this.id = id;
        this.teacherId = teacherId;
        this.title = title;
        this.sourceFileUrl = sourceFileUrl;
        this.rawText = rawText;
        this.parsedJson = parsedJson;
        this.parseStatus = parseStatus;
        this.status = status;
    }

    public static LessonPlanResponse from(LessonPlan lessonPlan) {
        return new LessonPlanResponse(
                lessonPlan.getId(),
                lessonPlan.getTeacherId(),
                lessonPlan.getTitle(),
                lessonPlan.getSourceFileUrl(),
                lessonPlan.getRawText(),
                lessonPlan.getParsedJson(),
                lessonPlan.getParseStatus(),
                lessonPlan.getStatus());
    }

    public Long getId() { return id; }
    public Long getTeacherId() { return teacherId; }
    public String getTitle() { return title; }
    public String getSourceFileUrl() { return sourceFileUrl; }
    public String getRawText() { return rawText; }
    public String getParsedJson() { return parsedJson; }
    public String getParseStatus() { return parseStatus; }
    public String getStatus() { return status; }
}
