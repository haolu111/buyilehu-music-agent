package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.application.service.GenerationSseService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.MediaType;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/v1/generation-jobs")
public class GenerationJobController {
    private final GenerationJobService generationJobService;
    private final GenerationSseService generationSseService;

    public GenerationJobController(GenerationJobService generationJobService,
                                   GenerationSseService generationSseService) {
        this.generationJobService = generationJobService;
        this.generationSseService = generationSseService;
    }

    @PostMapping
    public ApiResponse<GenerationJobStatus> create(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @Valid @RequestBody CreateGenerationJobRequest request) {
        GenerationJobStatus created = generationJobService.create(request, idempotencyKey);
        return ApiResponse.success(generationJobService.getStatus(created.getId()));
    }

    @GetMapping("/{jobId}")
    public ApiResponse<GenerationJobStatus> get(@PathVariable Long jobId) {
        return ApiResponse.success(generationJobService.getStatus(jobId));
    }

    @GetMapping(value = "/{jobId}/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter events(@PathVariable Long jobId) {
        GenerationJobStatus snapshot = generationJobService.getStatus(jobId);
        return generationSseService.subscribe(jobId, snapshot);
    }
}
