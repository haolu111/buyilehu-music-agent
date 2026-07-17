package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.PackageVersion;
import java.time.LocalDateTime;

public class PackageVersionResponse {
    private Long id;
    private Long packageId;
    private Integer versionNo;
    private Long createdBy;
    private String remark;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static PackageVersionResponse from(PackageVersion version) {
        PackageVersionResponse response = new PackageVersionResponse();
        response.setId(version.getId());
        response.setPackageId(version.getPackageId());
        response.setVersionNo(version.getVersionNo());
        response.setCreatedBy(version.getCreatedBy());
        response.setRemark(version.getRemark());
        response.setStatus(version.getStatus());
        response.setCreatedAt(version.getCreatedAt());
        response.setUpdatedAt(version.getUpdatedAt());
        return response;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Integer getVersionNo() { return versionNo; }
    public void setVersionNo(Integer versionNo) { this.versionNo = versionNo; }
    public Long getCreatedBy() { return createdBy; }
    public void setCreatedBy(Long createdBy) { this.createdBy = createdBy; }
    public String getRemark() { return remark; }
    public void setRemark(String remark) { this.remark = remark; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}