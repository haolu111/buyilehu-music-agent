package com.buyilehu.musicagent.infrastructure.status;

import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import java.util.Optional;

public interface GenerationJobStatusStore {
    void save(GenerationJobStatus status);

    Optional<GenerationJobStatus> find(Long jobId);
}
