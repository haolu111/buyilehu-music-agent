package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonCapabilityRuntimeBuildResponse {
    private boolean success;
    private PythonCapabilityRuntimeBuildData data;

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public PythonCapabilityRuntimeBuildData getData() {
        return data;
    }

    public void setData(PythonCapabilityRuntimeBuildData data) {
        this.data = data;
    }
}
