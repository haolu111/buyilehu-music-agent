package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.databind.JsonNode;

public class PythonCapabilityError {
    private String code;
    private String message;
    private JsonNode detail;

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public JsonNode getDetail() {
        return detail;
    }

    public void setDetail(JsonNode detail) {
        this.detail = detail;
    }
}
