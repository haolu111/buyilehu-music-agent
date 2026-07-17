package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.application.service.GenerationJobEventPublisher;
import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/v1/generation-jobs")
public class GenerationJobController {
    private final GenerationJobService generationJobService;
    private final GenerationJobEventPublisher eventPublisher;

    public GenerationJobController(GenerationJobService generationJobService,
                                   GenerationJobEventPublisher eventPublisher) {
        this.generationJobService = generationJobService;
        this.eventPublisher = eventPublisher;
    }

    @PostMapping
    public ApiResponse<GenerationJobResponse> create(@Valid @RequestBody CreateGenerationJobRequest request) {
        return ApiResponse.success(generationJobService.createAndGenerate(request));
    }

    @GetMapping("/{jobId}")
    public ApiResponse<GenerationJobResponse> get(@PathVariable Long jobId) {
        return ApiResponse.success(generationJobService.getJob(jobId));
    }

    @GetMapping(value = "/{jobId}/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter events(@PathVariable Long jobId) {
        return eventPublisher.subscribe(jobId, generationJobService.getJob(jobId));
    }
}
