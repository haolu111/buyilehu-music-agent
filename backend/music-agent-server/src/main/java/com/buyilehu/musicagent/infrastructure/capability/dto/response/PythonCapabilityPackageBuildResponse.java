package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonCapabilityPackageBuildResponse {
    private boolean success;
    private PythonCapabilityPackageBuildData data;

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public PythonCapabilityPackageBuildData getData() { return data; }
    public void setData(PythonCapabilityPackageBuildData data) { this.data = data; }
}
