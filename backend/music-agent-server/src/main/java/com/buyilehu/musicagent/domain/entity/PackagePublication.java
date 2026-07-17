package com.buyilehu.musicagent.domain.entity;

import java.time.LocalDateTime;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "package_publications")
public class PackagePublication extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "package_id", nullable = false)
    private Long packageId;

    @Column(name = "version_id", nullable = false)
    private Long versionId;

    @Column(name = "class_id", nullable = false)
    private Long classId;

    @Column(name = "published_by", nullable = false)
    private Long publishedBy;

    @Column(name = "publish_channel", nullable = false, length = 50)
    private String publishChannel;

    @Column(nullable = false, length = 30)
    private String status = "published";

    @Column(name = "review_enabled", nullable = false)
    private Boolean reviewEnabled = false;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    public PackagePublication() {
    }

    public Long getId() { return id; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getVersionId() { return versionId; }
    public void setVersionId(Long versionId) { this.versionId = versionId; }
    public Long getClassId() { return classId; }
    public void setClassId(Long classId) { this.classId = classId; }
    public Long getPublishedBy() { return publishedBy; }
    public void setPublishedBy(Long publishedBy) { this.publishedBy = publishedBy; }
    public String getPublishChannel() { return publishChannel; }
    public void setPublishChannel(String publishChannel) { this.publishChannel = publishChannel; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Boolean getReviewEnabled() { return reviewEnabled; }
    public void setReviewEnabled(Boolean reviewEnabled) { this.reviewEnabled = reviewEnabled; }
    public LocalDateTime getPublishedAt() { return publishedAt; }
    public void setPublishedAt(LocalDateTime publishedAt) { this.publishedAt = publishedAt; }
}
