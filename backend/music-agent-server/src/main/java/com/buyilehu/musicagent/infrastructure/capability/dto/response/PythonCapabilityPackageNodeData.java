package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PythonCapabilityPackageNodeData extends PythonCapabilityRuntimeBuildData {
    @JsonProperty("client_ref")
    private String clientRef;

    public String getClientRef() { return clientRef; }
    public void setClientRef(String clientRef) { this.clientRef = clientRef; }
}
