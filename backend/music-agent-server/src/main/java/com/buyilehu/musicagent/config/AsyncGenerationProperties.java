package com.buyilehu.musicagent.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.async-generation")
public class AsyncGenerationProperties {
    private boolean enabled = true;
    private String exchange = "music-agent.generation";
    private String queue = "music-agent.generation.jobs";
    private String routingKey = "generation.job.created";
    private String deadLetterExchange = "music-agent.generation.dlx";
    private String deadLetterQueue = "music-agent.generation.jobs.dlq";
    private String statusChannel = "music-agent:generation:status-events";
    private Duration statusTtl = Duration.ofHours(24);
    private long sseTimeoutMs = 30 * 60 * 1000L;
    private int outboxBatchSize = 20;
    private int outboxMaxAttempts = 10;
    private Duration outboxProcessingTimeout = Duration.ofMinutes(2);
    private Duration publisherConfirmTimeout = Duration.ofSeconds(5);

    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public String getExchange() { return exchange; }
    public void setExchange(String exchange) { this.exchange = exchange; }
    public String getQueue() { return queue; }
    public void setQueue(String queue) { this.queue = queue; }
    public String getRoutingKey() { return routingKey; }
    public void setRoutingKey(String routingKey) { this.routingKey = routingKey; }
    public String getDeadLetterExchange() { return deadLetterExchange; }
    public void setDeadLetterExchange(String deadLetterExchange) { this.deadLetterExchange = deadLetterExchange; }
    public String getDeadLetterQueue() { return deadLetterQueue; }
    public void setDeadLetterQueue(String deadLetterQueue) { this.deadLetterQueue = deadLetterQueue; }
    public String getStatusChannel() { return statusChannel; }
    public void setStatusChannel(String statusChannel) { this.statusChannel = statusChannel; }
    public Duration getStatusTtl() { return statusTtl; }
    public void setStatusTtl(Duration statusTtl) { this.statusTtl = statusTtl; }
    public long getSseTimeoutMs() { return sseTimeoutMs; }
    public void setSseTimeoutMs(long sseTimeoutMs) { this.sseTimeoutMs = sseTimeoutMs; }
    public int getOutboxBatchSize() { return outboxBatchSize; }
    public void setOutboxBatchSize(int outboxBatchSize) { this.outboxBatchSize = outboxBatchSize; }
    public int getOutboxMaxAttempts() { return outboxMaxAttempts; }
    public void setOutboxMaxAttempts(int outboxMaxAttempts) { this.outboxMaxAttempts = outboxMaxAttempts; }
    public Duration getOutboxProcessingTimeout() { return outboxProcessingTimeout; }
    public void setOutboxProcessingTimeout(Duration outboxProcessingTimeout) { this.outboxProcessingTimeout = outboxProcessingTimeout; }
    public Duration getPublisherConfirmTimeout() { return publisherConfirmTimeout; }
    public void setPublisherConfirmTimeout(Duration publisherConfirmTimeout) { this.publisherConfirmTimeout = publisherConfirmTimeout; }
}
