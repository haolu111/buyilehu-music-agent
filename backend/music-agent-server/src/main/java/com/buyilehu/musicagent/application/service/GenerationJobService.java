package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;

public interface GenerationJobService {
    GenerationJobResponse createAndGenerate(CreateGenerationJobRequest request);
    GenerationJobResponse getJob(Long jobId);
}
