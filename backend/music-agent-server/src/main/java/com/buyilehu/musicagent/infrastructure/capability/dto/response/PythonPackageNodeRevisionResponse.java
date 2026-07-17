package com.buyilehu.musicagent.infrastructure.capability.dto.response;

public class PythonPackageNodeRevisionResponse {
    private boolean success;
    private PythonPackageNodeRevisionData data;

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public PythonPackageNodeRevisionData getData() { return data; }
    public void setData(PythonPackageNodeRevisionData data) { this.data = data; }
}
