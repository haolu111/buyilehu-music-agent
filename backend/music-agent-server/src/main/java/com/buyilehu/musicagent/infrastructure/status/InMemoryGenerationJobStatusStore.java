package com.buyilehu.musicagent.infrastructure.status;

import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.application.service.GenerationSseService;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "false")
public class InMemoryGenerationJobStatusStore implements GenerationJobStatusStore {
    private final Map<Long, GenerationJobStatus> statuses = new ConcurrentHashMap<>();
    private final GenerationSseService sseService;

    public InMemoryGenerationJobStatusStore(GenerationSseService sseService) {
        this.sseService = sseService;
    }

    @Override
    public void save(GenerationJobStatus status) {
        statuses.put(status.getId(), status);
        sseService.broadcast(status);
    }

    @Override
    public Optional<GenerationJobStatus> find(Long jobId) {
        return Optional.ofNullable(statuses.get(jobId));
    }
}
