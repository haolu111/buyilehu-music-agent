package com.buyilehu.musicagent.infrastructure.capability.dto.request;

import java.util.ArrayList;
import java.util.List;

public class PythonPackageBuildRequest {
    private List<PythonPackageNodeBuildRequest> nodes = new ArrayList<PythonPackageNodeBuildRequest>();

    public List<PythonPackageNodeBuildRequest> getNodes() { return nodes; }
    public void setNodes(List<PythonPackageNodeBuildRequest> nodes) { this.nodes = nodes; }
}
