package com.buyilehu.musicagent.application.dto.request;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

public class PackageModifyRequest {
    @NotNull
    @Positive
    private Long nodeId;

    private String modifyType = "node_config";

    @Valid
    @NotNull
    private PackageNodeConfigUpdateRequest config = new PackageNodeConfigUpdateRequest();

    public Long getNodeId() { return nodeId; }
    public void setNodeId(Long nodeId) { this.nodeId = nodeId; }
    public String getModifyType() { return modifyType; }
    public void setModifyType(String modifyType) { this.modifyType = modifyType; }
    public PackageNodeConfigUpdateRequest getConfig() { return config; }
    public void setConfig(PackageNodeConfigUpdateRequest config) { this.config = config; }
}