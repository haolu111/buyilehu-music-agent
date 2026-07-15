package com.buyilehu.musicagent.infrastructure.messaging;

import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.event.GenerationJobCreatedEvent;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.application.service.GenerationJobStatusService;
import com.buyilehu.musicagent.infrastructure.outbox.OutboxEventService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

@Component
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "false")
public class SynchronousGenerationJobListener {
    private final GenerationJobService generationJobService;
    private final GenerationJobStatusService statusService;
    private final OutboxEventService outboxEventService;

    public SynchronousGenerationJobListener(GenerationJobService generationJobService,
                                             GenerationJobStatusService statusService,
                                             OutboxEventService outboxEventService) {
        this.generationJobService = generationJobService;
        this.statusService = statusService;
        this.outboxEventService = outboxEventService;
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void execute(GenerationJobCreatedEvent event) {
        try {
            GenerationJobResponse response = generationJobService.execute(event.getJobId());
            statusService.completed(response);
            outboxEventService.markGenerationJobPublished(event.getJobId());
        } catch (RuntimeException exception) {
            generationJobService.fail(event.getJobId(), exception);
            outboxEventService.markGenerationJobFailed(event.getJobId(), exception);
        }
    }
}
