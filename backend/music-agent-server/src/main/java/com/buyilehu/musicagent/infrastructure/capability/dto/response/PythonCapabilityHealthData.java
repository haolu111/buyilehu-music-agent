package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PythonCapabilityHealthData {
    private String status;
    private String service;
    @JsonProperty("python_version")
    private String pythonVersion;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getService() {
        return service;
    }

    public void setService(String service) {
        this.service = service;
    }

    public String getPythonVersion() {
        return pythonVersion;
    }

    public void setPythonVersion(String pythonVersion) {
        this.pythonVersion = pythonVersion;
    }
}
