package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.CreateGenerationJobRequest;
import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.service.GenerationJobService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/generation-jobs")
public class GenerationJobController {
    private final GenerationJobService generationJobService;

    public GenerationJobController(GenerationJobService generationJobService) {
        this.generationJobService = generationJobService;
    }

    @PostMapping
    public ApiResponse<GenerationJobResponse> create(@Valid @RequestBody CreateGenerationJobRequest request) {
        return ApiResponse.success(generationJobService.createAndGenerate(request));
    }
}
