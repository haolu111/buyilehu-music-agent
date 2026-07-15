package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class PythonPackageDesignData {
    @JsonProperty("schema_version")
    private String schemaVersion;
    private String title;
    @JsonProperty("reasoning_summary")
    private String reasoningSummary;
    private List<PythonPackageDesignStep> steps = new ArrayList<PythonPackageDesignStep>();
    private PythonPackageDesignMetadata design;

    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getReasoningSummary() { return reasoningSummary; }
    public void setReasoningSummary(String reasoningSummary) { this.reasoningSummary = reasoningSummary; }
    public List<PythonPackageDesignStep> getSteps() { return steps; }
    public void setSteps(List<PythonPackageDesignStep> steps) { this.steps = steps; }
    public PythonPackageDesignMetadata getDesign() { return design; }
    public void setDesign(PythonPackageDesignMetadata design) { this.design = design; }
}
