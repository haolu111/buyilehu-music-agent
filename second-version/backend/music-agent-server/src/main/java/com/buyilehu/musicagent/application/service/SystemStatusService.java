package com.buyilehu.musicagent.application.service;

import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityClient;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityProperties;

@Service
public class SystemStatusService {
    private final PythonCapabilityClient pythonCapabilityClient;
    private final PythonCapabilityProperties pythonProperties;

    public SystemStatusService(PythonCapabilityClient pythonCapabilityClient, PythonCapabilityProperties pythonProperties) {
        this.pythonCapabilityClient = pythonCapabilityClient;
        this.pythonProperties = pythonProperties;
    }

    public Map<String, Object> health() {
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("status", "UP");
        status.put("service", "music-agent-server");
        status.put("time", Instant.now());
        Map<String, Object> capability = new LinkedHashMap<String, Object>();
        capability.put("enabled", pythonProperties.isEnabled());
        capability.put("callMode", String.valueOf(pythonProperties.getCallMode()).toLowerCase());
        if (!pythonProperties.isEnabled()) {
            capability.put("status", "DISABLED");
        } else {
            try {
                capability.put("status", pythonCapabilityClient.getHealth().isSuccess() ? "UP" : "DOWN");
            } catch (RuntimeException exception) {
                capability.put("status", "DOWN");
                capability.put("message", exception.getMessage());
            }
        }
        status.put("pythonCapability", capability);
        return status;
    }
}
