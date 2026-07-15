package com.buyilehu.musicagent.infrastructure.outbox;

import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.config.AsyncGenerationProperties;
import com.buyilehu.musicagent.domain.entity.OutboxEvent;
import com.buyilehu.musicagent.infrastructure.messaging.GenerationJobMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "true", matchIfMissing = true)
public class GenerationOutboxPublisher {
    private static final Logger log = LoggerFactory.getLogger(GenerationOutboxPublisher.class);

    private final String workerId = UUID.randomUUID().toString();
    private final OutboxEventService outboxEventService;
    private final RabbitTemplate rabbitTemplate;
    private final AsyncGenerationProperties properties;
    private final ObjectMapper objectMapper;
    private final GenerationJobService generationJobService;

    public GenerationOutboxPublisher(OutboxEventService outboxEventService,
                                     RabbitTemplate rabbitTemplate,
                                     AsyncGenerationProperties properties,
                                     ObjectMapper objectMapper,
                                     GenerationJobService generationJobService) {
        this.outboxEventService = outboxEventService;
        this.rabbitTemplate = rabbitTemplate;
        this.properties = properties;
        this.objectMapper = objectMapper;
        this.generationJobService = generationJobService;
    }

    @Scheduled(fixedDelayString = "${app.async-generation.outbox-publish-interval-ms:1000}")
    public void publishReadyEvents() {
        List<OutboxEvent> events = outboxEventService.claimReady(workerId);
        for (OutboxEvent event : events) {
            publish(event);
        }
    }

    private void publish(OutboxEvent event) {
        try {
            GenerationJobMessage message = objectMapper.readValue(
                    event.getPayloadJson(), GenerationJobMessage.class);
            CorrelationData correlationData = new CorrelationData(String.valueOf(event.getId()));
            rabbitTemplate.convertAndSend(
                    properties.getExchange(), properties.getRoutingKey(), message, correlationData);
            CorrelationData.Confirm confirm = correlationData.getFuture().get(
                    properties.getPublisherConfirmTimeout().toMillis(), TimeUnit.MILLISECONDS);
            if (!confirm.isAck()) {
                throw new IllegalStateException("RabbitMQ rejected message: " + confirm.getReason());
            }
            if (correlationData.getReturned() != null) {
                throw new IllegalStateException("RabbitMQ returned unroutable message: "
                        + correlationData.getReturned().getReplyText());
            }
            outboxEventService.markPublished(event.getId());
        } catch (Exception exception) {
            log.error("Unable to publish outbox event {}", event.getId(), exception);
            boolean terminal = outboxEventService.markDeliveryFailed(event.getId(), exception);
            if (terminal) {
                generationJobService.fail(event.getAggregateId(), exception);
            }
        }
    }
}
