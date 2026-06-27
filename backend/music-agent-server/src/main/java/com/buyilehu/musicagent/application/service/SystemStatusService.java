package com.buyilehu.musicagent.application.service;

import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class SystemStatusService {
    public Map<String, Object> health() {
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("status", "UP");
        status.put("service", "music-agent-server");
        status.put("time", Instant.now());
        return status;
    }
}
