package com.buyilehu.musicagent.domain.entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "package_modify_records")
public class PackageModifyRecord extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "package_id", nullable = false)
    private Long packageId;

    @Column(name = "version_id")
    private Long versionId;

    @Column(name = "modified_by", nullable = false)
    private Long modifiedBy;

    @Column(name = "modify_type", nullable = false, length = 50)
    private String modifyType;

    @Column(name = "modify_content", columnDefinition = "TEXT")
    private String modifyContent;

    public PackageModifyRecord() {
    }

    public Long getId() { return id; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getVersionId() { return versionId; }
    public void setVersionId(Long versionId) { this.versionId = versionId; }
    public Long getModifiedBy() { return modifiedBy; }
    public void setModifiedBy(Long modifiedBy) { this.modifiedBy = modifiedBy; }
    public String getModifyType() { return modifyType; }
    public void setModifyType(String modifyType) { this.modifyType = modifyType; }
    public String getModifyContent() { return modifyContent; }
    public void setModifyContent(String modifyContent) { this.modifyContent = modifyContent; }
}
