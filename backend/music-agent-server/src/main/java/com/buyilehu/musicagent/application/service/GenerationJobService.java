package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;

public interface GenerationJobService {
    default GenerationJobStatus create(CreateGenerationJobRequest request) {
        return create(request, null);
    }

    GenerationJobStatus create(CreateGenerationJobRequest request, String idempotencyKey);

    GenerationJobStatus getStatus(Long jobId);

    GenerationJobResponse execute(Long jobId);

    void fail(Long jobId, Throwable error);
}
