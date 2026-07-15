package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class PythonPackageDesignMetadata {
    private String provider;
    private String model;
    @JsonProperty("fallback_reason")
    private String fallbackReason;
    @JsonProperty("trace_id")
    private String traceId;
    @JsonProperty("workflow_engine")
    private String workflowEngine;
    @JsonProperty("workflow_steps")
    private List<String> workflowSteps = new ArrayList<String>();
    @JsonProperty("tool_calls")
    private List<String> toolCalls = new ArrayList<String>();

    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getFallbackReason() { return fallbackReason; }
    public void setFallbackReason(String fallbackReason) { this.fallbackReason = fallbackReason; }
    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }
    public String getWorkflowEngine() { return workflowEngine; }
    public void setWorkflowEngine(String workflowEngine) { this.workflowEngine = workflowEngine; }
    public List<String> getWorkflowSteps() { return workflowSteps; }
    public void setWorkflowSteps(List<String> workflowSteps) { this.workflowSteps = workflowSteps; }
    public List<String> getToolCalls() { return toolCalls; }
    public void setToolCalls(List<String> toolCalls) { this.toolCalls = toolCalls; }
}
