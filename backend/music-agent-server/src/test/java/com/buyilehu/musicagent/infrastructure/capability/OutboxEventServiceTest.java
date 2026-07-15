package com.buyilehu.musicagent.infrastructure.capability;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.buyilehu.musicagent.config.AsyncGenerationProperties;
import com.buyilehu.musicagent.domain.entity.OutboxEvent;
import com.buyilehu.musicagent.infrastructure.outbox.OutboxEventService;
import com.buyilehu.musicagent.infrastructure.repository.OutboxEventRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class OutboxEventServiceTest {
    @Mock
    private OutboxEventRepository outboxEventRepository;

    private AsyncGenerationProperties properties;
    private OutboxEventService outboxEventService;

    @BeforeEach
    void setUp() {
        properties = new AsyncGenerationProperties();
        outboxEventService = new OutboxEventService(
                outboxEventRepository, new ObjectMapper(), properties);
    }

    @Test
    void recordsGenerationEventPayload() {
        when(outboxEventRepository.save(any(OutboxEvent.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        OutboxEvent event = outboxEventService.recordGenerationJobCreated(42L);

        assertThat(event.getAggregateType()).isEqualTo("generation_job");
        assertThat(event.getAggregateId()).isEqualTo(42L);
        assertThat(event.getEventType()).isEqualTo("generation_job.created");
        assertThat(event.getPayloadJson()).contains("\"jobId\":42");
        assertThat(event.getStatus()).isEqualTo("pending");
    }

    @Test
    void claimsReadyEventsForOneWorker() {
        OutboxEvent event = pendingEvent(42L);
        when(outboxEventRepository.findReadyForDelivery(any(), any(), any()))
                .thenReturn(Collections.singletonList(event));
        when(outboxEventRepository.saveAll(any()))
                .thenAnswer(invocation -> invocation.getArgument(0));

        List<OutboxEvent> claimed = outboxEventService.claimReady("worker-1");

        assertThat(claimed).containsExactly(event);
        assertThat(event.getStatus()).isEqualTo("processing");
        assertThat(event.getAttempts()).isEqualTo(1);
        assertThat(event.getLockOwner()).isEqualTo("worker-1");
        assertThat(event.getLockedAt()).isNotNull();
    }

    @Test
    void marksEventFailedAfterMaximumAttempts() {
        OutboxEvent event = pendingEvent(42L);
        event.setAttempts(3);
        properties.setOutboxMaxAttempts(3);
        when(outboxEventRepository.findById(7L)).thenReturn(Optional.of(event));

        boolean terminal = outboxEventService.markDeliveryFailed(7L, new IllegalStateException("broker down"));

        assertThat(terminal).isTrue();
        assertThat(event.getStatus()).isEqualTo("failed");
        assertThat(event.getLastError()).isEqualTo("broker down");
    }

    private OutboxEvent pendingEvent(Long aggregateId) {
        OutboxEvent event = new OutboxEvent();
        event.setAggregateType("generation_job");
        event.setAggregateId(aggregateId);
        event.setEventType("generation_job.created");
        event.setPayloadJson("{\"jobId\":" + aggregateId + "}");
        event.setStatus("pending");
        event.setAttempts(0);
        event.setNextAttemptAt(LocalDateTime.now());
        return event;
    }
}
