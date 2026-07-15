package com.buyilehu.musicagent.application.event;

public class GenerationJobCreatedEvent {
    private final Long jobId;

    public GenerationJobCreatedEvent(Long jobId) {
        this.jobId = jobId;
    }

    public Long getJobId() { return jobId; }
}
