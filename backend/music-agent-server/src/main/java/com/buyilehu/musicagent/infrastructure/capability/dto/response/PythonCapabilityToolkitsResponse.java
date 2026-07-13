package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonCapabilityToolkitsResponse {
    private boolean success;
    private PythonCapabilityToolkitsData data;

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public PythonCapabilityToolkitsData getData() {
        return data;
    }

    public void setData(PythonCapabilityToolkitsData data) {
        this.data = data;
    }
}
