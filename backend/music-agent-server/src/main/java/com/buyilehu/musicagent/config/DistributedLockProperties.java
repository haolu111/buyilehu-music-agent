package com.buyilehu.musicagent.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.distributed-lock")
public class DistributedLockProperties {
    private boolean enabled = true;
    private String keyPrefix = "music-agent:lock:";
    private Duration waitTimeout = Duration.ofSeconds(2);
    private Duration leaseTimeout = Duration.ofSeconds(30);
    private Duration retryInterval = Duration.ofMillis(50);

    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public String getKeyPrefix() { return keyPrefix; }
    public void setKeyPrefix(String keyPrefix) { this.keyPrefix = keyPrefix; }
    public Duration getWaitTimeout() { return waitTimeout; }
    public void setWaitTimeout(Duration waitTimeout) { this.waitTimeout = waitTimeout; }
    public Duration getLeaseTimeout() { return leaseTimeout; }
    public void setLeaseTimeout(Duration leaseTimeout) { this.leaseTimeout = leaseTimeout; }
    public Duration getRetryInterval() { return retryInterval; }
    public void setRetryInterval(Duration retryInterval) { this.retryInterval = retryInterval; }
}
