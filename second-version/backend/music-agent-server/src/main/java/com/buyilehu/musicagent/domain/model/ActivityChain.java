package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;

public class ActivityChain {
    private String title;
    private List<ActivityStep> steps = new ArrayList<>();
    private String reasoningSummary;
    private String designProvider;
    private String designModel;
    private String designFallbackReason;
    private String designTraceId;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public List<ActivityStep> getSteps() { return steps; }
    public void setSteps(List<ActivityStep> steps) { this.steps = steps; }
    public String getReasoningSummary() { return reasoningSummary; }
    public void setReasoningSummary(String reasoningSummary) { this.reasoningSummary = reasoningSummary; }
    public String getDesignProvider() { return designProvider; }
    public void setDesignProvider(String designProvider) { this.designProvider = designProvider; }
    public String getDesignModel() { return designModel; }
    public void setDesignModel(String designModel) { this.designModel = designModel; }
    public String getDesignFallbackReason() { return designFallbackReason; }
    public void setDesignFallbackReason(String designFallbackReason) { this.designFallbackReason = designFallbackReason; }
    public String getDesignTraceId() { return designTraceId; }
    public void setDesignTraceId(String designTraceId) { this.designTraceId = designTraceId; }
}
