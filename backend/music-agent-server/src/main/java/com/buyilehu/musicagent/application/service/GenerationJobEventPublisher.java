package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Component
public class GenerationJobEventPublisher {
    private static final long STREAM_TIMEOUT_MS = 900_000L;
    private final ConcurrentHashMap<Long, CopyOnWriteArrayList<SseEmitter>> subscribers =
            new ConcurrentHashMap<>();

    public SseEmitter subscribe(Long jobId, GenerationJobResponse snapshot) {
        SseEmitter emitter = new SseEmitter(STREAM_TIMEOUT_MS);
        subscribers.computeIfAbsent(jobId, ignored -> new CopyOnWriteArrayList<>()).add(emitter);
        emitter.onCompletion(() -> remove(jobId, emitter));
        emitter.onTimeout(() -> remove(jobId, emitter));
        emitter.onError(error -> remove(jobId, emitter));
        send(jobId, emitter, snapshot);
        return emitter;
    }

    public void publish(GenerationJobResponse status) {
        List<SseEmitter> emitters = subscribers.get(status.getId());
        if (emitters == null) return;
        for (SseEmitter emitter : emitters) {
            send(status.getId(), emitter, status);
        }
    }

    private void send(Long jobId, SseEmitter emitter, GenerationJobResponse status) {
        try {
            emitter.send(SseEmitter.event()
                    .name("generation-status")
                    .id(status.getProgress() == null ? "0" : String.valueOf(status.getProgress()))
                    .data(status));
            if ("success".equals(status.getStatus()) || "failed".equals(status.getStatus())) {
                emitter.complete();
                remove(jobId, emitter);
            }
        } catch (IOException | IllegalStateException exception) {
            emitter.completeWithError(exception);
            remove(jobId, emitter);
        }
    }

    private void remove(Long jobId, SseEmitter emitter) {
        List<SseEmitter> emitters = subscribers.get(jobId);
        if (emitters == null) return;
        emitters.remove(emitter);
        if (emitters.isEmpty()) subscribers.remove(jobId, emitters);
    }
}
