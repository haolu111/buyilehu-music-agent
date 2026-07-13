package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class PythonCapabilityPackageBuildData {
    @JsonProperty("schema_version")
    private String schemaVersion;
    private List<PythonCapabilityPackageNodeData> nodes = new ArrayList<PythonCapabilityPackageNodeData>();

    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }
    public List<PythonCapabilityPackageNodeData> getNodes() { return nodes; }
    public void setNodes(List<PythonCapabilityPackageNodeData> nodes) { this.nodes = nodes; }
}
