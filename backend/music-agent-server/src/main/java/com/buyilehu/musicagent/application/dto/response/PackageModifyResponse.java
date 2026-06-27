package com.buyilehu.musicagent.application.dto.response;

public class PackageModifyResponse {
    private Long packageId;
    private Long nodeId;
    private Long fromVersionId;
    private Long toVersionId;
    private Integer versionNo;
    private String message;

    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getNodeId() { return nodeId; }
    public void setNodeId(Long nodeId) { this.nodeId = nodeId; }
    public Long getFromVersionId() { return fromVersionId; }
    public void setFromVersionId(Long fromVersionId) { this.fromVersionId = fromVersionId; }
    public Long getToVersionId() { return toVersionId; }
    public void setToVersionId(Long toVersionId) { this.toVersionId = toVersionId; }
    public Integer getVersionNo() { return versionNo; }
    public void setVersionNo(Integer versionNo) { this.versionNo = versionNo; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}