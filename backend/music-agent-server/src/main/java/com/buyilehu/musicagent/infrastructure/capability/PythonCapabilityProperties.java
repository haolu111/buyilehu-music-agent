package com.buyilehu.musicagent.infrastructure.capability;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.python-capability")
public class PythonCapabilityProperties {
    private boolean enabled = true;
    private CallMode callMode = CallMode.SHADOW;
    private String baseUrl = "http://localhost:8001";
    private int connectTimeoutMs = 2000;
    private int readTimeoutMs = 10000;
    private Map<String, String> nodeTypeActivityIdMappings = new LinkedHashMap<String, String>();

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public CallMode getCallMode() {
        return callMode;
    }

    public void setCallMode(CallMode callMode) {
        this.callMode = callMode;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public int getConnectTimeoutMs() {
        return connectTimeoutMs;
    }

    public void setConnectTimeoutMs(int connectTimeoutMs) {
        this.connectTimeoutMs = connectTimeoutMs;
    }

    public int getReadTimeoutMs() {
        return readTimeoutMs;
    }

    public void setReadTimeoutMs(int readTimeoutMs) {
        this.readTimeoutMs = readTimeoutMs;
    }

    public Map<String, String> getNodeTypeActivityIdMappings() {
        return nodeTypeActivityIdMappings;
    }

    public void setNodeTypeActivityIdMappings(Map<String, String> nodeTypeActivityIdMappings) {
        this.nodeTypeActivityIdMappings = nodeTypeActivityIdMappings;
    }

    public enum CallMode {
        DISABLED,
        SHADOW,
        PRIMARY
    }
}
