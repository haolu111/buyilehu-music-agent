package com.buyilehu.musicagent.infrastructure.outbox;

import com.buyilehu.musicagent.config.AsyncGenerationProperties;
import com.buyilehu.musicagent.domain.entity.OutboxEvent;
import com.buyilehu.musicagent.infrastructure.messaging.GenerationJobMessage;
import com.buyilehu.musicagent.infrastructure.repository.OutboxEventRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.List;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OutboxEventService {
    public static final String GENERATION_JOB_AGGREGATE = "generation_job";
    public static final String GENERATION_JOB_CREATED = "generation_job.created";

    private final OutboxEventRepository outboxEventRepository;
    private final ObjectMapper objectMapper;
    private final AsyncGenerationProperties properties;

    public OutboxEventService(OutboxEventRepository outboxEventRepository,
                              ObjectMapper objectMapper,
                              AsyncGenerationProperties properties) {
        this.outboxEventRepository = outboxEventRepository;
        this.objectMapper = objectMapper;
        this.properties = properties;
    }

    public OutboxEvent recordGenerationJobCreated(Long jobId) {
        OutboxEvent event = new OutboxEvent();
        event.setAggregateType(GENERATION_JOB_AGGREGATE);
        event.setAggregateId(jobId);
        event.setEventType(GENERATION_JOB_CREATED);
        event.setPayloadJson(toJson(new GenerationJobMessage(jobId)));
        event.setStatus("pending");
        event.setAttempts(0);
        event.setNextAttemptAt(LocalDateTime.now());
        return outboxEventRepository.save(event);
    }

    @Transactional
    public List<OutboxEvent> claimReady(String workerId) {
        LocalDateTime now = LocalDateTime.now();
        List<OutboxEvent> events = outboxEventRepository.findReadyForDelivery(
                now,
                now.minus(properties.getOutboxProcessingTimeout()),
                PageRequest.of(0, properties.getOutboxBatchSize()));
        for (OutboxEvent event : events) {
            event.setStatus("processing");
            event.setAttempts(event.getAttempts() + 1);
            event.setLockedAt(now);
            event.setLockOwner(workerId);
        }
        return outboxEventRepository.saveAll(events);
    }

    @Transactional
    public void markPublished(Long eventId) {
        OutboxEvent event = outboxEventRepository.findById(eventId).orElse(null);
        if (event == null || "published".equals(event.getStatus())) {
            return;
        }
        event.setStatus("published");
        event.setPublishedAt(LocalDateTime.now());
        event.setLockedAt(null);
        event.setLockOwner(null);
        event.setLastError(null);
    }

    @Transactional
    public boolean markDeliveryFailed(Long eventId, Throwable error) {
        OutboxEvent event = outboxEventRepository.findById(eventId).orElse(null);
        if (event == null || "published".equals(event.getStatus())) {
            return false;
        }
        boolean terminal = event.getAttempts() >= properties.getOutboxMaxAttempts();
        event.setStatus(terminal ? "failed" : "pending");
        event.setLastError(errorMessage(error));
        event.setLockedAt(null);
        event.setLockOwner(null);
        if (!terminal) {
            long delaySeconds = Math.min(60L, 1L << Math.min(event.getAttempts() - 1, 6));
            event.setNextAttemptAt(LocalDateTime.now().plusSeconds(delaySeconds));
        }
        return terminal;
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void markGenerationJobPublished(Long jobId) {
        findGenerationEvent(jobId).ifPresent(event -> markPublished(event.getId()));
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void markGenerationJobFailed(Long jobId, Throwable error) {
        findGenerationEvent(jobId).ifPresent(event -> {
            event.setStatus("failed");
            event.setLastError(errorMessage(error));
            event.setLockedAt(null);
            event.setLockOwner(null);
        });
    }

    private java.util.Optional<OutboxEvent> findGenerationEvent(Long jobId) {
        return outboxEventRepository.findByAggregateTypeAndAggregateIdAndEventType(
                GENERATION_JOB_AGGREGATE, jobId, GENERATION_JOB_CREATED);
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("Unable to serialize outbox event", exception);
        }
    }

    private String errorMessage(Throwable error) {
        String message = error.getMessage();
        String value = message == null || message.trim().isEmpty()
                ? error.getClass().getSimpleName() : message;
        return value.length() > 2000 ? value.substring(0, 2000) : value;
    }
}
