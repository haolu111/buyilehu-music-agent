package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.InteractivePackage;

public class PackageResponse {
    private Long id;
    private Long lessonPlanId;
    private Long generationJobId;
    private Long ownerId;
    private Long currentVersionId;
    private String title;
    private String description;
    private String status;

    public static PackageResponse from(InteractivePackage pkg) {
        PackageResponse response = new PackageResponse();
        response.setId(pkg.getId());
        response.setLessonPlanId(pkg.getLessonPlanId());
        response.setGenerationJobId(pkg.getGenerationJobId());
        response.setOwnerId(pkg.getOwnerId());
        response.setCurrentVersionId(pkg.getCurrentVersionId());
        response.setTitle(pkg.getTitle());
        response.setDescription(pkg.getDescription());
        response.setStatus(pkg.getStatus());
        return response;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getLessonPlanId() { return lessonPlanId; }
    public void setLessonPlanId(Long lessonPlanId) { this.lessonPlanId = lessonPlanId; }
    public Long getGenerationJobId() { return generationJobId; }
    public void setGenerationJobId(Long generationJobId) { this.generationJobId = generationJobId; }
    public Long getOwnerId() { return ownerId; }
    public void setOwnerId(Long ownerId) { this.ownerId = ownerId; }
    public Long getCurrentVersionId() { return currentVersionId; }
    public void setCurrentVersionId(Long currentVersionId) { this.currentVersionId = currentVersionId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
