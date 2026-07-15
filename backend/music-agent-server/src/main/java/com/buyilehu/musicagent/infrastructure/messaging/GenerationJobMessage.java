package com.buyilehu.musicagent.infrastructure.messaging;

public class GenerationJobMessage {
    private Long jobId;

    public GenerationJobMessage() {
    }

    public GenerationJobMessage(Long jobId) {
        this.jobId = jobId;
    }

    public Long getJobId() { return jobId; }
    public void setJobId(Long jobId) { this.jobId = jobId; }
}
