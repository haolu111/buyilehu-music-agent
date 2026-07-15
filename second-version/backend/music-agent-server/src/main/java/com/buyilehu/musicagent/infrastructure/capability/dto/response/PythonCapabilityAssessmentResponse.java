package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.databind.JsonNode;

public class PythonCapabilityAssessmentResponse {
    private boolean success;
    private JsonNode data;

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public JsonNode getData() { return data; }
    public void setData(JsonNode data) { this.data = data; }
}
