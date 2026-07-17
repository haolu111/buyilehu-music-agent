package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonCapabilityErrorResponse {
    private boolean success;
    private PythonCapabilityError error;

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public PythonCapabilityError getError() {
        return error;
    }

    public void setError(PythonCapabilityError error) {
        this.error = error;
    }
}
