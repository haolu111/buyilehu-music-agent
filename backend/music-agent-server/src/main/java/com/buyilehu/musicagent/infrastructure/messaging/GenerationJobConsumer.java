package com.buyilehu.musicagent.infrastructure.messaging;

import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.application.service.GenerationJobStatusService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "true", matchIfMissing = true)
public class GenerationJobConsumer {
    private static final Logger log = LoggerFactory.getLogger(GenerationJobConsumer.class);

    private final GenerationJobService generationJobService;
    private final GenerationJobStatusService statusService;

    public GenerationJobConsumer(GenerationJobService generationJobService,
                                 GenerationJobStatusService statusService) {
        this.generationJobService = generationJobService;
        this.statusService = statusService;
    }

    @RabbitListener(queues = "${app.async-generation.queue:music-agent.generation.jobs}")
    public void consume(GenerationJobMessage message) {
        try {
            GenerationJobResponse response = generationJobService.execute(message.getJobId());
            statusService.completed(response);
        } catch (RuntimeException exception) {
            log.error("Generation job {} failed", message.getJobId(), exception);
            generationJobService.fail(message.getJobId(), exception);
        }
    }
}
