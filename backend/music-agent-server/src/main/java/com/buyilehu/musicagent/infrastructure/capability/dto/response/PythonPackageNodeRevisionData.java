package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import java.util.HashMap;
import java.util.Map;

public class PythonPackageNodeRevisionData {
    private Map<String, Object> node = new HashMap<String, Object>();
    private String provider;
    private String model;
    private String fallbackReason;

    public Map<String, Object> getNode() { return node; }
    public void setNode(Map<String, Object> node) { this.node = node; }
    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getFallbackReason() { return fallbackReason; }
    public void setFallbackReason(String fallbackReason) { this.fallbackReason = fallbackReason; }
}
