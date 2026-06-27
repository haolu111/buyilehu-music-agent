package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.PackagePublication;
import java.time.LocalDateTime;

public class PackagePublicationResponse {
    private Long id;
    private Long packageId;
    private Long versionId;
    private Long classId;
    private Long teacherId;
    private String status;
    private Boolean reviewEnabled;
    private LocalDateTime publishedAt;

    public static PackagePublicationResponse from(PackagePublication publication) {
        PackagePublicationResponse response = new PackagePublicationResponse();
        response.setId(publication.getId());
        response.setPackageId(publication.getPackageId());
        response.setVersionId(publication.getVersionId());
        response.setClassId(publication.getClassId());
        response.setTeacherId(publication.getPublishedBy());
        response.setStatus(publication.getStatus());
        response.setReviewEnabled(publication.getReviewEnabled());
        response.setPublishedAt(publication.getPublishedAt());
        return response;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getVersionId() { return versionId; }
    public void setVersionId(Long versionId) { this.versionId = versionId; }
    public Long getClassId() { return classId; }
    public void setClassId(Long classId) { this.classId = classId; }
    public Long getTeacherId() { return teacherId; }
    public void setTeacherId(Long teacherId) { this.teacherId = teacherId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Boolean getReviewEnabled() { return reviewEnabled; }
    public void setReviewEnabled(Boolean reviewEnabled) { this.reviewEnabled = reviewEnabled; }
    public LocalDateTime getPublishedAt() { return publishedAt; }
    public void setPublishedAt(LocalDateTime publishedAt) { this.publishedAt = publishedAt; }
}
