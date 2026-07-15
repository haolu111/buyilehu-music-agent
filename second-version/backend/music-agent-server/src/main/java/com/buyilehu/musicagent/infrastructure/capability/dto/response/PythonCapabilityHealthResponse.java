package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonCapabilityHealthResponse {
    private boolean success;
    private PythonCapabilityHealthData data;

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public PythonCapabilityHealthData getData() {
        return data;
    }

    public void setData(PythonCapabilityHealthData data) {
        this.data = data;
    }
}
