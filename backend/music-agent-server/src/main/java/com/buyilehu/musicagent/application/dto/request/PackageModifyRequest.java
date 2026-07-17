package com.buyilehu.musicagent.application.dto.request;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;
import javax.validation.constraints.Size;

/**
 * 教师对已经生成好的课堂互动包进行“局部修改”时，前端传给后端的请求对象。
 * 我要修改哪个活动节点 nodeId
 * 这次修改属于什么类型 modifyType
 * 具体修改配置是什么 config
 */
public class PackageModifyRequest {
    @NotNull
    @Positive
    private Long nodeId;

    private String modifyType = "node_config";

    @Size(max = 2000)
    private String feedback;

    @Valid
    @NotNull
    private PackageNodeConfigUpdateRequest config = new PackageNodeConfigUpdateRequest();

    public Long getNodeId() { return nodeId; }
    public void setNodeId(Long nodeId) { this.nodeId = nodeId; }
    public String getModifyType() { return modifyType; }
    public void setModifyType(String modifyType) { this.modifyType = modifyType; }
    public String getFeedback() { return feedback; }
    public void setFeedback(String feedback) { this.feedback = feedback; }
    public PackageNodeConfigUpdateRequest getConfig() { return config; }
    public void setConfig(PackageNodeConfigUpdateRequest config) { this.config = config; }
}
