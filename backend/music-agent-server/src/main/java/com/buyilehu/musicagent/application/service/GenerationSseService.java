package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.config.AsyncGenerationProperties;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Service
public class GenerationSseService {
    private final Map<Long, List<SseEmitter>> emitters = new ConcurrentHashMap<>();
    private final AsyncGenerationProperties properties;

    public GenerationSseService(AsyncGenerationProperties properties) {
        this.properties = properties;
    }

    public SseEmitter subscribe(Long jobId, GenerationJobStatus snapshot) {
        SseEmitter emitter = new SseEmitter(properties.getSseTimeoutMs());
        emitters.computeIfAbsent(jobId, ignored -> new CopyOnWriteArrayList<>()).add(emitter);
        emitter.onCompletion(() -> remove(jobId, emitter));
        emitter.onTimeout(() -> remove(jobId, emitter));
        emitter.onError(error -> remove(jobId, emitter));
        send(jobId, emitter, snapshot);
        return emitter;
    }

    public void broadcast(GenerationJobStatus status) {
        List<SseEmitter> jobEmitters = emitters.get(status.getId());
        if (jobEmitters == null) {
            return;
        }
        for (SseEmitter emitter : jobEmitters) {
            send(status.getId(), emitter, status);
        }
    }

    @Scheduled(fixedRateString = "${app.async-generation.sse-heartbeat-ms:15000}")
    public void heartbeat() {
        for (Map.Entry<Long, List<SseEmitter>> entry : emitters.entrySet()) {
            for (SseEmitter emitter : entry.getValue()) {
                try {
                    emitter.send(SseEmitter.event().comment("heartbeat"));
                } catch (IOException exception) {
                    remove(entry.getKey(), emitter);
                }
            }
        }
    }

    private void send(Long jobId, SseEmitter emitter, GenerationJobStatus status) {
        try {
            emitter.send(SseEmitter.event()
                    .id(String.valueOf(System.currentTimeMillis()))
                    .name("status")
                    .data(status));
            if (status.isTerminal()) {
                emitter.complete();
                remove(jobId, emitter);
            }
        } catch (IOException exception) {
            emitter.completeWithError(exception);
            remove(jobId, emitter);
        }
    }

    private void remove(Long jobId, SseEmitter emitter) {
        List<SseEmitter> jobEmitters = emitters.get(jobId);
        if (jobEmitters == null) {
            return;
        }
        jobEmitters.remove(emitter);
        if (jobEmitters.isEmpty()) {
            emitters.remove(jobId, jobEmitters);
        }
    }
}
