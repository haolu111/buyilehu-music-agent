package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonPackageDesignResponse {
    private boolean success;
    private PythonPackageDesignData data;

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public PythonPackageDesignData getData() { return data; }
    public void setData(PythonPackageDesignData data) { this.data = data; }
}
